"""Unit tests for the deterministic grading logic in scripts/score.py.

Covers the three things Session 4's kickoff calls out explicitly:
  * beat / met / miss grading (our calls AND management guidance),
  * the basis-mismatch REFUSAL (a non_gaap call vs a gaap actual must RAISE,
    never silently score -- the PLAN §3 GAAP trap), and
  * malformed input (missing/ill-typed fields, unknown kinds, bad JSON, a
    record filed in the wrong ticker shard) failing loud.

No network, no LLM -- the whole point is that grading is pure Python.
"""
import json

import pytest

import score  # noqa: E402  (scripts/ put on sys.path by conftest)


# --------------------------------------------------------------------------- #
# Record builders (minimal valid records; tests override the interesting bits)
# --------------------------------------------------------------------------- #


def make_call(**over):
    rec = {
        "id": "T-1", "ticker": "NVDA", "timestamp": "2026-05-27T20:00:00Z",
        "call_type": "preview", "period": "FY2027Q1", "metric": "revenue",
        "unit": "USD_M", "basis": "non_gaap", "source_note": "notes/NVDA/x.md",
        "call": {"kind": "direction", "value": "beat",
                 "benchmark": {"kind": "range", "low": 100, "high": 110}},
        "actual": {"value": 120, "basis": "non_gaap"},
    }
    rec.update(over)
    return rec


def make_guidance(**over):
    rec = {
        "id": "G-1", "ticker": "AMZN", "timestamp": "2026-07-30T21:00:00Z",
        "metric": "net_sales", "unit": "USD_M", "basis": "gaap",
        "period": "FY2026Q3", "guided_at_period": "FY2026Q2",
        "source_filing": "https://sec.gov/x",
        "guidance": {"kind": "range", "low": 194000, "high": 199000},
        "actual": {"value": 196300, "basis": "gaap"},
    }
    rec.update(over)
    return rec


# --------------------------------------------------------------------------- #
# The pure numeric core
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("value,expected", [(120, "above"), (105, "within"),
                                            (100, "within"), (110, "within"), (90, "below")])
def test_classify_band(value, expected):
    assert score._classify_band(value, 100, 110) == expected


def test_label_direction_flip():
    # higher-is-better: above -> beat
    assert score._label("above", higher_is_better=True) == "beat"
    assert score._label("below", higher_is_better=True) == "miss"
    # lower-is-better (opex/capex): above the guide -> miss
    assert score._label("above", higher_is_better=False) == "miss"
    assert score._label("below", higher_is_better=False) == "beat"
    assert score._label("within", higher_is_better=False) == "met"


# --------------------------------------------------------------------------- #
# Guidance grading: beat / met / miss
# --------------------------------------------------------------------------- #


def test_guidance_beat():
    assert score.grade_guidance(make_guidance(actual={"value": 205000, "basis": "gaap"}))["outcome"] == "beat"


def test_guidance_met():
    assert score.grade_guidance(make_guidance())["outcome"] == "met"


def test_guidance_miss():
    assert score.grade_guidance(make_guidance(actual={"value": 180000, "basis": "gaap"}))["outcome"] == "miss"


def test_guidance_lower_is_better_flips_beat_and_miss():
    # capex guided [100,110]; coming in high (120) is a MISS when lower is better.
    rec = make_guidance(basis="gaap", metric="capex", higher_is_better=False,
                        guidance={"kind": "range", "low": 100, "high": 110},
                        actual={"value": 120, "basis": "gaap"})
    assert score.grade_guidance(rec)["outcome"] == "miss"
    rec2 = dict(rec, actual={"value": 90, "basis": "gaap"})
    assert score.grade_guidance(rec2)["outcome"] == "beat"


def test_guidance_point_with_tolerance():
    rec = make_guidance(guidance={"kind": "point", "value": 100, "tolerance": 5},
                        actual={"value": 103, "basis": "gaap"})
    assert score.grade_guidance(rec)["outcome"] == "met"
    assert score.grade_guidance(dict(rec, actual={"value": 112, "basis": "gaap"}))["outcome"] == "beat"


def test_guidance_pending_when_no_actual():
    rec = make_guidance()
    rec.pop("actual")
    r = score.grade_guidance(rec)
    assert r["status"] == "pending" and r["outcome"] is None


# --------------------------------------------------------------------------- #
# Our-call grading: direction / range / point / qualitative / pending
# --------------------------------------------------------------------------- #


def test_call_direction_hit():
    # predicted beat, actual 120 above [100,110] -> beat -> hit
    r = score.grade_call(make_call())
    assert r["status"] == "graded" and r["outcome"] == "beat" and r["hit"] is True


def test_call_direction_miss():
    # predicted beat, actual 105 within band -> met -> our call is wrong
    r = score.grade_call(make_call(actual={"value": 105, "basis": "non_gaap"}))
    assert r["outcome"] == "met" and r["hit"] is False


def test_call_range_hit_and_miss():
    rec = make_call(call={"kind": "range", "low": 100, "high": 110})
    assert score.grade_call(dict(rec, actual={"value": 105, "basis": "non_gaap"}))["hit"] is True
    assert score.grade_call(dict(rec, actual={"value": 130, "basis": "non_gaap"}))["hit"] is False


def test_call_point_tolerance():
    rec = make_call(metric="gross_margin", unit="pct",
                    call={"kind": "point", "value": 75.0, "tolerance": 0.5})
    assert score.grade_call(dict(rec, actual={"value": 75.2, "basis": "non_gaap"}))["hit"] is True
    assert score.grade_call(dict(rec, actual={"value": 76.0, "basis": "non_gaap"}))["hit"] is False


def test_call_qualitative_counted_not_graded():
    rec = make_call(metric="thesis", unit="narrative",
                    call={"kind": "qualitative", "value": "DC stays supply-constrained"})
    rec.pop("actual")
    r = score.grade_call(rec)
    assert r["status"] == "qualitative" and r["hit"] is None


def test_call_pending_when_no_actual():
    rec = make_call()
    rec.pop("actual")
    r = score.grade_call(rec)
    assert r["status"] == "pending" and r["hit"] is None


# --------------------------------------------------------------------------- #
# The basis-mismatch REFUSAL (PLAN §3) -- the critical guard
# --------------------------------------------------------------------------- #


def test_call_basis_mismatch_raises():
    # non_gaap call graded against a gaap actual must RAISE, never score.
    bad = make_call(basis="non_gaap", actual={"value": 120, "basis": "gaap"})
    with pytest.raises(score.BasisMismatchError):
        score.grade_call(bad)


def test_guidance_basis_mismatch_raises():
    bad = make_guidance(basis="gaap", actual={"value": 196300, "basis": "non_gaap"})
    with pytest.raises(score.BasisMismatchError):
        score.grade_guidance(bad)


def test_basis_checked_before_comparison():
    # Even when the numbers would grade cleanly, a basis mismatch still raises.
    bad = make_call(basis="non_gaap",
                    call={"kind": "range", "low": 100, "high": 110},
                    actual={"value": 105, "basis": "gaap"})
    with pytest.raises(score.BasisMismatchError):
        score.grade_call(bad)


# --------------------------------------------------------------------------- #
# Malformed input fails loud
# --------------------------------------------------------------------------- #


def test_missing_required_field_raises():
    rec = make_call()
    rec.pop("source_note")
    with pytest.raises(score.MalformedRecordError):
        score.validate_call(rec)


def test_invalid_basis_raises():
    with pytest.raises(score.MalformedRecordError):
        score.validate_call(make_call(basis="ifrs"))


def test_actual_value_not_a_number_raises():
    with pytest.raises(score.MalformedRecordError):
        score.grade_call(make_call(actual={"value": "lots", "basis": "non_gaap"}))


def test_bool_is_not_accepted_as_number():
    # bool is a subclass of int -- must be rejected, not read as 1/0.
    with pytest.raises(score.MalformedRecordError):
        score.grade_call(make_call(actual={"value": True, "basis": "non_gaap"}))


def test_unknown_call_kind_raises():
    with pytest.raises(score.MalformedRecordError):
        score.grade_call(make_call(call={"kind": "vibes", "value": "up"}))


def test_range_low_above_high_raises():
    with pytest.raises(score.MalformedRecordError):
        score.grade_call(make_call(call={"kind": "range", "low": 110, "high": 100}))


def test_direction_value_must_be_beat_met_miss():
    with pytest.raises(score.MalformedRecordError):
        score.grade_call(make_call(call={"kind": "direction", "value": "up",
                                         "benchmark": {"kind": "range", "low": 1, "high": 2}}))


def test_negative_tolerance_raises():
    with pytest.raises(score.MalformedRecordError):
        score.grade_call(make_call(call={"kind": "point", "value": 5, "tolerance": -1}))


def test_nan_actual_raises_not_silently_scored():
    # json parses NaN/Infinity; a non-finite actual must raise, not classify as within.
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(score.MalformedRecordError):
            score.grade_call(make_call(actual={"value": bad, "basis": "non_gaap"}))


def test_pending_call_with_malformed_band_still_fails_loud():
    # No actual yet, but a low>high range must be rejected at load, not held until the print.
    rec = make_call(call={"kind": "range", "low": 110, "high": 100})
    rec.pop("actual")
    with pytest.raises(score.MalformedRecordError):
        score.validate_call(rec)


def test_pending_direction_call_bad_enum_fails_loud():
    rec = make_call(call={"kind": "direction", "value": "MAYBE",
                          "benchmark": {"kind": "range", "low": 1, "high": 2}})
    rec.pop("actual")
    with pytest.raises(score.MalformedRecordError):
        score.validate_call(rec)


def test_pending_direction_call_missing_benchmark_fails_loud():
    rec = make_call(call={"kind": "direction", "value": "beat"})
    rec.pop("actual")
    with pytest.raises(score.MalformedRecordError):
        score.validate_call(rec)


def test_bad_confidence_on_pending_call_fails_loud():
    rec = make_call(confidence=1.5)
    rec.pop("actual")
    with pytest.raises(score.MalformedRecordError):
        score.validate_call(rec)


def test_confidence_wrong_type_fails_loud():
    with pytest.raises(score.MalformedRecordError):
        score.validate_call(make_call(confidence="high"))


def test_confidence_decile_boundary_bins_correctly():
    # 0.3 must land in the [0.3,0.4) bin (index 3), not slip to index 2 via float truncation.
    s = score.compute_summary([make_call(id="b", confidence=0.3)], [])
    bins = s["our_calls"]["calibration"]["bins"]
    assert bins[3]["n"] == 1 and bins[2]["n"] == 0


# --------------------------------------------------------------------------- #
# Duplicate-id integrity + unknown call_type warning
# --------------------------------------------------------------------------- #


def test_duplicate_id_across_shards_raises(tmp_path):
    (tmp_path / "NVDA.jsonl").write_text(json.dumps(make_call(id="dup", ticker="NVDA")) + "\n", encoding="utf-8")
    (tmp_path / "AMD.jsonl").write_text(json.dumps(make_call(id="dup", ticker="AMD")) + "\n", encoding="utf-8")
    with pytest.raises(score.MalformedRecordError):
        score.load_all_calls(tmp_path)


def test_unknown_call_type_surfaces_warning():
    s = score.compute_summary([make_call(call_type="teaser")], [])
    assert any("teaser" in w for w in s["warnings"])


# --------------------------------------------------------------------------- #
# Shard loading: bad JSON, mis-sharded ticker, blank-line tolerance
# --------------------------------------------------------------------------- #


def test_load_shard_bad_json_raises(tmp_path):
    p = tmp_path / "NVDA.jsonl"
    p.write_text('{"id": "ok"\n', encoding="utf-8")  # truncated JSON
    with pytest.raises(score.MalformedRecordError):
        score.load_shard(p, score.validate_call)


def test_load_shard_misfiled_ticker_raises(tmp_path):
    # A record for AMD living in NVDA.jsonl is a sharding-integrity error.
    p = tmp_path / "NVDA.jsonl"
    p.write_text(json.dumps(make_call(ticker="AMD")) + "\n", encoding="utf-8")
    with pytest.raises(score.MalformedRecordError):
        score.load_shard(p, score.validate_call)


def test_load_shard_skips_blank_lines(tmp_path):
    p = tmp_path / "NVDA.jsonl"
    p.write_text("\n" + json.dumps(make_call()) + "\n\n", encoding="utf-8")
    recs = score.load_shard(p, score.validate_call)
    assert len(recs) == 1 and recs[0]["ticker"] == "NVDA"


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


def test_compute_summary_rollup():
    calls = [
        make_call(id="c1"),  # hit
        make_call(id="c2", actual={"value": 105, "basis": "non_gaap"}),  # miss (met vs beat)
        make_call(id="c3", call={"kind": "qualitative", "value": "x"}, actual=None),
    ]
    calls[2].pop("actual")
    guidance = [make_guidance(id="g1"),  # met
                make_guidance(id="g2", actual={"value": 205000, "basis": "gaap"})]  # beat
    s = score.compute_summary(calls, guidance, generated_at="fixed")
    oc = s["our_calls"]["overall"]
    assert oc["n_graded"] == 2 and oc["hits"] == 1 and oc["hit_rate"] == 0.5
    assert oc["qualitative"] == 1
    ga = s["guidance_accuracy"]["overall"]
    assert (ga["beat"], ga["met"], ga["missed"]) == (1, 1, 0)
    assert s["generated_at"] == "fixed"


def test_compute_summary_exclude_dummy():
    real = make_call(id="real")
    dummy = make_call(id="dummy", dummy=True)
    s = score.compute_summary([real, dummy], [], include_dummy=False)
    assert s["totals"]["call_records"] == 1
    assert s["dummy"]["included"] is False and s["dummy"]["call_records"] == 1


def test_hit_rate_none_when_nothing_graded():
    pending = make_call()
    pending.pop("actual")
    s = score.compute_summary([pending], [])
    assert s["our_calls"]["overall"]["hit_rate"] is None
    assert any("pending" in w for w in s["warnings"])


def test_calibration_bins_confidence():
    c = make_call(id="hi", confidence=0.85)  # hit
    s = score.compute_summary([c], [])
    calib = s["our_calls"]["calibration"]
    top_bin = calib["bins"][8]  # [0.8, 0.9)
    assert top_bin["n"] == 1 and top_bin["hits"] == 1 and top_bin["empirical_rate"] == 1.0


def test_out_of_range_confidence_raises_at_load():
    # Range-checked on load (validate_call) rather than deep in aggregation, so it fails
    # loud the moment the record is read.
    with pytest.raises(score.MalformedRecordError):
        score.validate_call(make_call(confidence=1.5))
