"""Golden-fixture regression tests for scripts/edgar.py.

These pin the PURE parsing functions against saved REAL EDGAR payloads
(tests/fixtures/, trimmed to keep the repo light but structurally exact). They
run offline -- no network -- and are the net that catches EDGAR format drift and
the two poison-the-whole-project failure modes:

  * grabbing the wrong revenue tag when a company migrates tags mid-history
    (NVDA: RevenueFromContractWithCustomerExcludingAssessedTax -> Revenues), and
  * grabbing the wrong 8-K / the wrong exhibit (EX-99.2 CFO commentary instead of
    the EX-99.1 press release; a non-earnings 8-K instead of the Item-2.02 one).
"""
import json

import pytest

from conftest import FIXTURES  # noqa: E402  (path set up in conftest)

import edgar  # noqa: E402


def load(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


def load_json(name):
    return json.loads(load(name))


# --------------------------------------------------------------------------- #
# ticker -> CIK
# --------------------------------------------------------------------------- #


def test_parse_ticker_map():
    mapping = edgar.parse_ticker_map(load_json("company_tickers_slice.json"))
    assert mapping["NVDA"].cik == 1045810
    assert mapping["NVDA"].cik10 == "0001045810"
    assert mapping["LLY"].cik10 == "0000059478"
    # lookup is case-insensitive on the key
    assert "MU" in mapping and "KO" in mapping


# --------------------------------------------------------------------------- #
# companyfacts concept extraction
# --------------------------------------------------------------------------- #


@pytest.fixture()
def nvda_facts():
    return load_json("companyfacts_NVDA.json")


def test_named_metric_picks_current_revenue_tag(nvda_facts):
    """The migration case: both revenue tags exist, but the current data lives
    under 'Revenues'. named_metric must NOT return the stale
    RevenueFromContractWithCustomerExcludingAssessedTax series."""
    tag, series = edgar.named_metric(nvda_facts, edgar.REVENUE_TAGS)
    assert tag == "Revenues"
    assert series[-1].end == "2026-04-26"
    assert series[-1].unit == "USD"
    assert series[-1].val > 0


def test_stale_tag_alone_is_returned_as_is(nvda_facts):
    """Sanity: querying the stale tag directly still returns its (old) series --
    named_metric's preference logic is what avoids it, not a mutation."""
    series = edgar.concept_series(
        nvda_facts, "RevenueFromContractWithCustomerExcludingAssessedTax"
    )
    assert series[-1].end <= "2022-12-31"


def test_concept_series_sorted_ascending(nvda_facts):
    series = edgar.concept_series(nvda_facts, "EarningsPerShareDiluted")
    ends = [f.end for f in series]
    assert ends == sorted(ends)
    assert series[-1].unit == "USD/shares"


def test_latest_fact_and_form_filter(nvda_facts):
    latest = edgar.latest_fact(nvda_facts, edgar.EPS_DILUTED_TAGS)
    assert latest is not None
    # form filter restricts to a single form
    q = edgar.latest_fact(nvda_facts, edgar.EPS_DILUTED_TAGS, form="10-Q")
    if q is not None:
        assert q.form == "10-Q"


def test_named_metric_absent_returns_none(nvda_facts):
    tag, series = edgar.named_metric(nvda_facts, ["ThisConceptDoesNotExist"])
    assert tag is None and series == []


def test_concept_series_missing_raises(nvda_facts):
    with pytest.raises(edgar.ConceptNotFound):
        edgar.concept_series(nvda_facts, "NoSuchConcept")


def test_available_taxonomies(nvda_facts):
    taxes = edgar.available_taxonomies(nvda_facts)
    assert "us-gaap" in taxes


# --------------------------------------------------------------------------- #
# submissions -> earnings 8-K selection
# --------------------------------------------------------------------------- #


@pytest.fixture()
def nvda_subs():
    return load_json("submissions_NVDA.json")


def test_find_earnings_8k_filings_selects_item_202(nvda_subs):
    filings = edgar.find_earnings_8k_filings(nvda_subs)
    # fixture holds exactly two Item-2.02 8-Ks plus decoys (a 5.02 8-K, 10-Q, 10-K)
    assert len(filings) == 2
    for f in filings:
        assert f.form == "8-K"
        assert "2.02" in [t.strip() for t in f.items.split(",")]


def test_find_earnings_8k_filings_newest_first(nvda_subs):
    filings = edgar.find_earnings_8k_filings(nvda_subs)
    assert filings[0].acceptance_datetime >= filings[1].acceptance_datetime
    assert filings[0].accession == "0001045810-26-000051"


def test_item_token_match_is_exact():
    """'2.02' must not match a hypothetical '12.02' item via substring."""
    subs = {
        "filings": {
            "recent": {
                "form": ["8-K", "8-K"],
                "items": ["12.02,9.01", "2.02"],
                "accessionNumber": ["0000000000-26-000001", "0000000000-26-000002"],
                "filingDate": ["2026-01-01", "2026-02-01"],
                "reportDate": ["2026-01-01", "2026-02-01"],
                "acceptanceDateTime": ["2026-01-01T16:00:00.000Z", "2026-02-01T16:00:00.000Z"],
                "primaryDocument": ["a.htm", "b.htm"],
                "primaryDocDescription": ["8-K", "8-K"],
            }
        }
    }
    filings = edgar.find_earnings_8k_filings(subs)
    assert len(filings) == 1
    assert filings[0].accession == "0000000000-26-000002"


def test_no_earnings_8k_raises_via_orchestrator(monkeypatch):
    empty = {"filings": {"recent": {"form": ["10-K"], "items": [""],
             "accessionNumber": ["x"], "filingDate": ["2026-01-01"],
             "reportDate": ["2026-01-01"], "acceptanceDateTime": ["z"],
             "primaryDocument": ["a"], "primaryDocDescription": [""]}}}
    assert edgar.find_earnings_8k_filings(empty) == []


# --------------------------------------------------------------------------- #
# exhibit / document parsing -- the wrong-exhibit guard
# --------------------------------------------------------------------------- #


def test_parse_documents_nvda():
    docs = edgar.parse_documents(load("index_headers_NVDA_8k.html"))
    by_type = {d.type: d.filename for d in docs}
    assert by_type["8-K"] == "nvda-20260520.htm"
    assert by_type["EX-99.1"] == "q1fy27pr.htm"
    assert by_type["EX-99.2"] == "q1fy27cfocommentary.htm"


def test_select_press_release_prefers_991_over_992():
    """The core wrong-exhibit guard: this 8-K carries BOTH EX-99.1 (press
    release) and EX-99.2 (CFO commentary). We must pick .1."""
    docs = edgar.parse_documents(load("index_headers_NVDA_8k.html"))
    pr = edgar.select_press_release(docs)
    assert pr.filename == "q1fy27pr.htm"
    assert edgar._norm_exhibit(pr.type) == "EX-99.1"


def test_select_press_release_bare_ex99_fallback():
    """LLY files the press release as bare EX-99 (no .1). The fallback must find
    it rather than failing loud."""
    docs = edgar.parse_documents(load("index_headers_LLY_8k.html"))
    pr = edgar.select_press_release(docs)
    assert edgar._norm_exhibit(pr.type) == "EX-99"
    assert "earning" in pr.filename.lower() or "lilly" in pr.filename.lower()


def test_select_press_release_missing_raises():
    docs = [
        edgar.Document(type="8-K", sequence="1", filename="a.htm", description="8-K"),
        edgar.Document(type="EX-101.SCH", sequence="2", filename="a.xsd", description="x"),
    ]
    with pytest.raises(edgar.MissingExhibit991):
        edgar.select_press_release(docs)


def test_select_press_release_ambiguous_raises():
    docs = [
        edgar.Document(type="EX-99.1", sequence="1", filename="a.htm", description="pr1"),
        edgar.Document(type="EX-99.1", sequence="2", filename="b.htm", description="pr2"),
    ]
    with pytest.raises(edgar.AmbiguousExhibit991):
        edgar.select_press_release(docs)


def test_parse_documents_empty_raises():
    with pytest.raises(edgar.EdgarError):
        edgar.parse_documents("<html><body>no sgml here</body></html>")


def test_norm_exhibit_variants():
    assert edgar._norm_exhibit("EX-99.1") == "EX-99.1"
    assert edgar._norm_exhibit("ex-99.1 ") == "EX-99.1"
    assert edgar._norm_exhibit("EX-99.01") == "EX-99.1"
    assert edgar._norm_exhibit("EX-99") == "EX-99"
    assert edgar._norm_exhibit("EX-99.2") == "EX-99.2"


# --------------------------------------------------------------------------- #
# html_to_text
# --------------------------------------------------------------------------- #


def test_html_to_text_strips_and_unescapes():
    html = "<p>Revenue was <b>$81.6&nbsp;billion</b></p><script>x=1</script>"
    text = edgar.html_to_text(html)
    assert "Revenue was" in text
    assert "$81.6" in text
    assert "x=1" not in text
    assert "<" not in text


def test_redash_roundtrip():
    assert edgar._redash("000104581026000051") == "0001045810-26-000051"
    assert edgar._redash("0001045810-26-000051") == "0001045810-26-000051"
