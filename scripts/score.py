#!/usr/bin/env python
"""Scorecard engine for Furton Coverage.

Reads the PER-TICKER sharded stores ``scorecard/calls/<TICKER>.jsonl`` and
``scorecard/guidance/<TICKER>.jsonl`` (schema documented in scorecard/SCHEMA.md),
grades them **deterministically in code**, and writes ``scorecard/summary.json``.

Two things this module guarantees, because getting either wrong silently poisons a
public accuracy scorecard (PLAN §3, §7):

1. **No LLM in the grading path.** Every numeric call is graded by comparing the call
   to its ``actual`` in Python -- Claude never grades its own quantitative calls. The
   only judgment-based calls (``kind: "qualitative"``) are counted, never numerically
   scored here.
2. **Basis is never crossed.** Every call/guidance record and every ``actual`` block
   carries a ``basis`` (``gaap`` | ``non_gaap``). Before ANY numeric comparison,
   ``_check_basis`` asserts ``record.basis == actual.basis`` and raises
   ``BasisMismatchError`` otherwise. A non-GAAP call graded against a GAAP actual (the
   §3 trap -- companies guide non-GAAP, companyfacts is GAAP) is a hard stop, not a
   silently-wrong score.

Fail-loud philosophy (same as Furton Research's vote parser): a malformed line, a
missing required field, an unknown ``kind``, an invalid ``basis``, or a record filed in
the wrong ticker shard raises rather than degrading to a quiet default.

Grading model (full detail in scorecard/SCHEMA.md)
--------------------------------------------------
* ``_classify_band(value, low, high)`` -> ``above`` | ``within`` | ``below`` is the pure
  numeric core. With ``higher_is_better`` applied it maps to ``beat`` | ``met`` | ``miss``.
* **Guidance** grades management's actual vs. its own guidance band -> beat/met/missed.
* **Our calls** come in four kinds:
    - ``direction``: we predicted the actual's relation to a benchmark band; HIT iff our
      predicted label equals the actual's classification.
    - ``range``: HIT iff ``low <= actual <= high``.
    - ``point``: HIT iff ``|actual - value| <= tolerance``.
    - ``qualitative``: counted, not numerically graded.
* A record with no ``actual`` is **pending** (the print hasn't landed) -- excluded from
  hit-rate denominators, tallied separately.

Windows: run via ``py`` and set ``PYTHONUTF8=1`` (console is cp1252).

CLI::

    py scripts/score.py                 # score all shards -> scorecard/summary.json
    py scripts/score.py --exclude-dummy # drop dummy-seeded rows (real run)
    py scripts/score.py --selftest      # in-memory smoke of the grading core
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths (resolved from config/settings.json, tolerant like edgar.py)
# --------------------------------------------------------------------------- #

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "settings.json"

_DEFAULT_CALLS_REL = "scorecard/calls"
_DEFAULT_GUIDANCE_REL = "scorecard/guidance"
_DEFAULT_SUMMARY_REL = "scorecard/summary.json"

VALID_BASES = ("gaap", "non_gaap")
KNOWN_CALL_TYPES = ("preview", "flash", "review", "initiation")
CALL_KINDS = ("direction", "range", "point", "qualitative")


def _load_paths() -> dict:
    calls_rel, guid_rel, summ_rel = (
        _DEFAULT_CALLS_REL,
        _DEFAULT_GUIDANCE_REL,
        _DEFAULT_SUMMARY_REL,
    )
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cfg = {}
        paths = cfg.get("paths") or {}
        calls_rel = paths.get("scorecard_calls") or calls_rel
        guid_rel = paths.get("scorecard_guidance") or guid_rel
        summ_rel = paths.get("scorecard_summary") or summ_rel
    return {
        "calls_dir": REPO_ROOT / calls_rel,
        "guidance_dir": REPO_ROOT / guid_rel,
        "summary": REPO_ROOT / summ_rel,
    }


# --------------------------------------------------------------------------- #
# Errors -- typed and loud (never a silently degraded score)
# --------------------------------------------------------------------------- #


class ScorecardError(Exception):
    """Base class for all score.py failures."""


class MalformedRecordError(ScorecardError):
    """A record is missing a required field, is ill-typed, names an unknown kind,
    or is filed in the wrong ticker shard."""


class BasisMismatchError(ScorecardError):
    """A call/guidance record's basis does not match its actual's basis. Grading a
    non_gaap call against a gaap actual (or vice-versa) is refused, never scored
    (PLAN §3 GAAP-trap rule)."""


# --------------------------------------------------------------------------- #
# Field validators -- fail loud with file:line context
# --------------------------------------------------------------------------- #


def _ctx(where: str) -> str:
    return f" [{where}]" if where else ""


def _req_str(rec: dict, key: str, where: str = "") -> str:
    if key not in rec:
        raise MalformedRecordError(f"missing required field '{key}'{_ctx(where)}")
    v = rec[key]
    if not isinstance(v, str) or not v.strip():
        raise MalformedRecordError(
            f"field '{key}' must be a non-empty string, got {v!r}{_ctx(where)}"
        )
    return v


def _num(v, key: str, where: str = "") -> float:
    # bool is a subclass of int -- reject it explicitly so True/False can't pose as 1/0.
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise MalformedRecordError(
            f"field '{key}' must be a number, got {v!r}{_ctx(where)}"
        )
    # json.loads accepts NaN/Infinity by default; a non-finite actual would classify as
    # within/above and silently score a HIT, so reject it loudly.
    if not math.isfinite(v):
        raise MalformedRecordError(
            f"field '{key}' must be finite, got {v!r}{_ctx(where)}"
        )
    return float(v)


def _req_num(rec: dict, key: str, where: str = "") -> float:
    if key not in rec:
        raise MalformedRecordError(f"missing required field '{key}'{_ctx(where)}")
    return _num(rec[key], key, where)


def _basis(rec: dict, where: str = "") -> str:
    b = _req_str(rec, "basis", where)
    if b not in VALID_BASES:
        raise MalformedRecordError(
            f"basis must be one of {VALID_BASES}, got {b!r}{_ctx(where)}"
        )
    return b


def _bool_field(rec: dict, key: str, default: bool, where: str = "") -> bool:
    if key not in rec:
        return default
    v = rec[key]
    if not isinstance(v, bool):
        raise MalformedRecordError(
            f"field '{key}' must be a boolean, got {v!r}{_ctx(where)}"
        )
    return v


def _validate_confidence(rec: dict, where: str = "") -> None:
    """Optional field, but if present it must be a number in [0, 1]. Validated on load
    (not just when the call is graded) so a bad confidence on a pending/qualitative call
    fails loud immediately rather than the day its actual lands."""
    if "confidence" not in rec:
        return
    c = _num(rec["confidence"], "confidence", where)
    if not 0.0 <= c <= 1.0:
        raise MalformedRecordError(
            f"confidence must be in [0, 1], got {c}{_ctx(where)}"
        )


def _band(spec: dict, where: str) -> tuple[float, float]:
    """Normalise a range/point spec to an inclusive [low, high] band."""
    if not isinstance(spec, dict):
        raise MalformedRecordError(f"band spec must be an object, got {spec!r}{_ctx(where)}")
    kind = _req_str(spec, "kind", where)
    if kind == "range":
        low = _req_num(spec, "low", where)
        high = _req_num(spec, "high", where)
        if low > high:
            raise MalformedRecordError(
                f"range low ({low}) exceeds high ({high}){_ctx(where)}"
            )
        return low, high
    if kind == "point":
        val = _req_num(spec, "value", where)
        tol = _num(spec.get("tolerance", 0.0), "tolerance", where)
        if tol < 0:
            raise MalformedRecordError(f"tolerance must be >= 0, got {tol}{_ctx(where)}")
        return val - tol, val + tol
    raise MalformedRecordError(
        f"band kind must be 'range' or 'point', got {kind!r}{_ctx(where)}"
    )


# --------------------------------------------------------------------------- #
# The deterministic grading core
# --------------------------------------------------------------------------- #


def _classify_band(value: float, low: float, high: float) -> str:
    """Pure numeric core: where does ``value`` land relative to [low, high]?"""
    if value > high:
        return "above"
    if value < low:
        return "below"
    return "within"


def _label(position: str, higher_is_better: bool) -> str:
    """Map a band position to a beat/met/miss label, honouring metric direction.

    For a higher-is-better metric (revenue, EPS) landing *above* the band is a beat.
    For a lower-is-better metric (opex, capex) landing *above* the guided band is a
    miss -- so the labels flip.
    """
    if position == "within":
        return "met"
    above = position == "above"
    if not higher_is_better:
        above = not above
    return "beat" if above else "miss"


def _check_basis(rec: dict, actual: dict, where: str) -> None:
    """The §3 guard. Raises BEFORE any numeric comparison if the bases differ."""
    rec_basis = _basis(rec, where)
    act_basis = _req_str(actual, "basis", where + ".actual")
    if act_basis not in VALID_BASES:
        raise MalformedRecordError(
            f"actual.basis must be one of {VALID_BASES}, got {act_basis!r}{_ctx(where)}"
        )
    if rec_basis != act_basis:
        raise BasisMismatchError(
            f"basis mismatch{_ctx(where)}: record is {rec_basis!r} but actual is "
            f"{act_basis!r} -- refusing to grade across bases (PLAN §3 GAAP trap)"
        )


def grade_guidance(rec: dict, where: str = "") -> dict:
    """Grade one guidance record: actual vs. management's own guidance band.

    Returns a result dict; does not mutate ``rec``. status is 'pending' when no actual
    has been recorded yet.
    """
    where = where or rec.get("id", "guidance")
    band = _band(_require(rec, "guidance", where), where)
    higher = _bool_field(rec, "higher_is_better", True, where)

    actual = rec.get("actual")
    if actual is None:
        return {"status": "pending", "outcome": None, "hit": None}
    if not isinstance(actual, dict):
        raise MalformedRecordError(f"actual must be an object{_ctx(where)}")

    _check_basis(rec, actual, where)  # raises on cross-basis before we compare
    value = _req_num(actual, "value", where + ".actual")
    outcome = _label(_classify_band(value, *band), higher)
    return {"status": "graded", "outcome": outcome, "hit": None}


def grade_call(rec: dict, where: str = "") -> dict:
    """Grade one of our calls. Returns a result dict; does not mutate ``rec``.

    ``hit`` is True/False for numerically-graded calls, None for qualitative or pending.
    ``outcome`` records the actual's classification (beat/met/miss or within/above/below)
    where meaningful.
    """
    where = where or rec.get("id", "call")
    call = _require(rec, "call", where)
    if not isinstance(call, dict):
        raise MalformedRecordError(f"'call' must be an object{_ctx(where)}")
    kind = _req_str(call, "kind", where)
    if kind not in CALL_KINDS:
        raise MalformedRecordError(
            f"call.kind must be one of {CALL_KINDS}, got {kind!r}{_ctx(where)}"
        )

    if kind == "qualitative":
        # Explicitly non-numeric -- score.py never LLM-grades. Counted, not scored.
        _require(call, "value", where)
        return {"status": "qualitative", "outcome": None, "hit": None}

    higher = _bool_field(rec, "higher_is_better", True, where)

    # Validate the call's structure NOW, before the pending check, so a malformed
    # pending call (missing benchmark, low>high, bad direction enum) fails loud at
    # load rather than silently sitting in the store until the print lands.
    if kind == "direction":
        predicted = _req_str(call, "value", where)
        if predicted not in ("beat", "met", "miss"):
            raise MalformedRecordError(
                f"direction call value must be beat|met|miss, got {predicted!r}{_ctx(where)}"
            )
        band = _band(_require(call, "benchmark", where), where + ".benchmark")
    else:  # range | point -- the call object itself is the band spec
        predicted = None
        band = _band(call, where)

    actual = rec.get("actual")
    if actual is None:
        return {"status": "pending", "outcome": None, "hit": None}
    if not isinstance(actual, dict):
        raise MalformedRecordError(f"actual must be an object{_ctx(where)}")

    _check_basis(rec, actual, where)  # raises on cross-basis before we compare
    value = _req_num(actual, "value", where + ".actual")

    if kind == "direction":
        outcome = _label(_classify_band(value, *band), higher)
        return {"status": "graded", "outcome": outcome, "hit": predicted == outcome}

    # range | point: HIT iff the actual lands inside the band.
    low, high = band
    return {
        "status": "graded",
        "outcome": _classify_band(value, low, high),
        "hit": low <= value <= high,
    }


def _require(rec: dict, key: str, where: str):
    if key not in rec:
        raise MalformedRecordError(f"missing required field '{key}'{_ctx(where)}")
    return rec[key]


# --------------------------------------------------------------------------- #
# Record-level validation (shape common to a store, checked on load)
# --------------------------------------------------------------------------- #


def validate_call(rec: dict, where: str = "") -> None:
    where = where or rec.get("id", "call")
    _req_str(rec, "id", where)
    _req_str(rec, "ticker", where)
    _req_str(rec, "timestamp", where)
    # call_type must be a real string; an unfamiliar value is surfaced as a summary
    # warning (compute_summary), not silently swallowed -- catches note-type typos.
    _req_str(rec, "call_type", where)
    _req_str(rec, "period", where)
    _req_str(rec, "metric", where)
    _req_str(rec, "unit", where)
    _basis(rec, where)
    _req_str(rec, "source_note", where)
    _validate_confidence(rec, where)
    # grade_call performs the deep structural validation of 'call' / 'actual', including
    # for still-pending calls (a malformed band fails loud here, not later).
    grade_call(rec, where)


def validate_guidance(rec: dict, where: str = "") -> None:
    where = where or rec.get("id", "guidance")
    _req_str(rec, "id", where)
    _req_str(rec, "ticker", where)
    _req_str(rec, "timestamp", where)
    _req_str(rec, "metric", where)
    _req_str(rec, "unit", where)
    _basis(rec, where)
    _req_str(rec, "period", where)
    _req_str(rec, "guided_at_period", where)
    _req_str(rec, "source_filing", where)
    grade_guidance(rec, where)


# --------------------------------------------------------------------------- #
# Shard loading (fail loud on bad JSON / mis-sharded records)
# --------------------------------------------------------------------------- #


def load_shard(path: Path, validator) -> list[dict]:
    """Parse one JSONL shard. Blank lines are skipped; every other line must be a JSON
    object that passes ``validator``. The record's ``ticker`` must match the filename
    stem (mis-sharding guard). Raises MalformedRecordError with file:line context."""
    expected_ticker = path.stem.upper()
    records: list[dict] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        where = f"{path.name}:{lineno}"
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MalformedRecordError(f"invalid JSON{_ctx(where)}: {exc}") from exc
        if not isinstance(rec, dict):
            raise MalformedRecordError(f"line is not a JSON object{_ctx(where)}")
        validator(rec, where)
        if rec["ticker"].upper() != expected_ticker:
            raise MalformedRecordError(
                f"record ticker {rec['ticker']!r} does not match shard file "
                f"{path.name} (expected {expected_ticker}){_ctx(where)}"
            )
        records.append(rec)
    return records


def _shards(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.glob("*.jsonl") if p.is_file())


def _assert_unique_ids(records: list[dict], store: str) -> None:
    """A repeated id (SCHEMA.md: id is unique; corrections are new dated records) means
    a retried run double-appended -- both copies would be double-counted, inflating the
    denominator. Fail loud instead."""
    seen: dict[str, str] = {}
    for rec in records:
        rid = rec["id"]
        if rid in seen:
            raise MalformedRecordError(
                f"duplicate id {rid!r} in {store} store (also on ticker "
                f"{seen[rid]}) -- ids must be unique (a correction is a new dated record)"
            )
        seen[rid] = rec["ticker"]


def load_all_calls(calls_dir: Path) -> list[dict]:
    out: list[dict] = []
    for shard in _shards(calls_dir):
        out.extend(load_shard(shard, validate_call))
    _assert_unique_ids(out, "calls")
    return out


def load_all_guidance(guidance_dir: Path) -> list[dict]:
    out: list[dict] = []
    for shard in _shards(guidance_dir):
        out.extend(load_shard(shard, validate_guidance))
    _assert_unique_ids(out, "guidance")
    return out


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


def _hit_tally() -> dict:
    return {"n_graded": 0, "hits": 0, "hit_rate": None, "pending": 0, "qualitative": 0}


def _finalise_hits(t: dict) -> dict:
    t["hit_rate"] = round(t["hits"] / t["n_graded"], 4) if t["n_graded"] else None
    return t


def _add_hit(t: dict, result: dict) -> None:
    status = result["status"]
    if status == "pending":
        t["pending"] += 1
    elif status == "qualitative":
        t["qualitative"] += 1
    elif status == "graded":
        t["n_graded"] += 1
        if result["hit"]:
            t["hits"] += 1


def _guid_tally() -> dict:
    return {"n_graded": 0, "beat": 0, "met": 0, "missed": 0, "pending": 0}


def _add_guid(t: dict, result: dict) -> None:
    if result["status"] == "pending":
        t["pending"] += 1
        return
    t["n_graded"] += 1
    outcome = result["outcome"]
    # _label emits beat/met/miss; the guidance store spells the shortfall "missed".
    t["beat" if outcome == "beat" else "met" if outcome == "met" else "missed"] += 1


def _calibration(graded_calls: list[tuple[dict, dict]]) -> dict:
    """Reliability curve: bucket calls that carry a numeric ``confidence`` into deciles
    and compare stated confidence to realised hit rate."""
    bins = [
        {"lo": round(i / 10, 1), "hi": round((i + 1) / 10, 1), "n": 0, "hits": 0,
         "empirical_rate": None, "mean_confidence": None, "_csum": 0.0}
        for i in range(10)
    ]
    used = 0
    for rec, result in graded_calls:
        conf = rec.get("confidence")
        if conf is None:
            continue
        # already range-validated on load by _validate_confidence.
        c = float(conf)
        # +1e-9 keeps decile boundaries in the intended bin: 0.3*10 == 2.9999...
        # would otherwise int-truncate to bin 2 instead of 3. 1.0 lands in the top bin.
        idx = min(int(c * 10 + 1e-9), 9)
        b = bins[idx]
        b["n"] += 1
        b["_csum"] += c
        if result["hit"]:
            b["hits"] += 1
        used += 1
    for b in bins:
        if b["n"]:
            b["empirical_rate"] = round(b["hits"] / b["n"], 4)
            b["mean_confidence"] = round(b["_csum"] / b["n"], 4)
        del b["_csum"]
    return {
        "scored_calls_with_confidence": used,
        "bins": bins,
        "note": (
            "Reliability curve over calls carrying a numeric 'confidence'. Empty until "
            "notes start attaching confidences." if used == 0 else
            "Compare mean_confidence to empirical_rate within each decile."
        ),
    }


def compute_summary(
    calls: list[dict],
    guidance: list[dict],
    *,
    include_dummy: bool = True,
    generated_at: str | None = None,
) -> dict:
    """Grade every record and roll up per-ticker + aggregate stats. Pure: no I/O."""
    warnings: list[str] = []
    dummy_calls = sum(1 for r in calls if r.get("dummy"))
    dummy_guid = sum(1 for r in guidance if r.get("dummy"))
    if not include_dummy:
        calls = [r for r in calls if not r.get("dummy")]
        guidance = [r for r in guidance if not r.get("dummy")]

    # ---- our calls ----
    overall = _hit_tally()
    by_type: dict[str, dict] = {}
    by_metric: dict[str, dict] = {}
    per_ticker_calls: dict[str, dict] = {}
    over_time_calls: dict[str, dict] = {}
    graded_pairs: list[tuple[dict, dict]] = []

    for rec in calls:
        result = grade_call(rec)
        _add_hit(overall, result)
        _add_hit(by_type.setdefault(rec["call_type"], _hit_tally()), result)
        _add_hit(by_metric.setdefault(rec["metric"], _hit_tally()), result)
        _add_hit(per_ticker_calls.setdefault(rec["ticker"], _hit_tally()), result)
        _add_hit(over_time_calls.setdefault(rec["period"], _hit_tally()), result)
        if result["status"] == "graded":
            graded_pairs.append((rec, result))

    for t in (overall, *by_type.values(), *by_metric.values(),
              *per_ticker_calls.values(), *over_time_calls.values()):
        _finalise_hits(t)

    # ---- management guidance ----
    guid_overall = _guid_tally()
    guid_by_ticker: dict[str, dict] = {}
    guid_over_time: dict[str, dict] = {}
    per_ticker_guid: dict[str, dict] = {}

    for rec in guidance:
        result = grade_guidance(rec)
        _add_guid(guid_overall, result)
        _add_guid(guid_by_ticker.setdefault(rec["ticker"], _guid_tally()), result)
        _add_guid(guid_over_time.setdefault(rec["period"], _guid_tally()), result)
        _add_guid(per_ticker_guid.setdefault(rec["ticker"], _guid_tally()), result)

    # ---- combined per-ticker view ----
    by_ticker: dict[str, dict] = {}
    for tk in sorted(set(per_ticker_calls) | set(per_ticker_guid)):
        by_ticker[tk] = {
            "our_calls": per_ticker_calls.get(tk, _finalise_hits(_hit_tally())),
            "guidance": per_ticker_guid.get(tk, _guid_tally()),
        }

    if overall["n_graded"] == 0 and overall["pending"]:
        warnings.append("no calls graded yet -- all outstanding calls are pending an actual")
    unknown_types = sorted(set(by_type) - set(KNOWN_CALL_TYPES))
    if unknown_types:
        warnings.append(
            f"unfamiliar call_type(s) {unknown_types} -- expected one of "
            f"{list(KNOWN_CALL_TYPES)} (possible note-type typo)"
        )

    return {
        "generated_at": generated_at,
        "totals": {
            "call_records": len(calls),
            "guidance_records": len(guidance),
            "calls_graded": overall["n_graded"],
            "calls_pending": overall["pending"],
            "calls_qualitative": overall["qualitative"],
            "guidance_graded": guid_overall["n_graded"],
            "guidance_pending": guid_overall["pending"],
            "tickers": len(by_ticker),
        },
        "our_calls": {
            "overall": overall,
            "by_call_type": dict(sorted(by_type.items())),
            "by_metric": dict(sorted(by_metric.items())),
            "over_time": dict(sorted(over_time_calls.items())),
            "calibration": _calibration(graded_pairs),
        },
        "guidance_accuracy": {
            "overall": guid_overall,
            "by_ticker": dict(sorted(guid_by_ticker.items())),
            "over_time": dict(sorted(guid_over_time.items())),
        },
        "by_ticker": by_ticker,
        "dummy": {
            "included": include_dummy,
            "call_records": dummy_calls,
            "guidance_records": dummy_guid,
        },
        "warnings": warnings,
    }


# --------------------------------------------------------------------------- #
# Top-level run + CLI
# --------------------------------------------------------------------------- #


def run(
    *,
    calls_dir: Path | None = None,
    guidance_dir: Path | None = None,
    out_path: Path | None = None,
    include_dummy: bool = True,
    write: bool = True,
) -> dict:
    paths = _load_paths()
    calls_dir = calls_dir or paths["calls_dir"]
    guidance_dir = guidance_dir or paths["guidance_dir"]
    out_path = out_path or paths["summary"]

    calls = load_all_calls(calls_dir)
    guidance = load_all_guidance(guidance_dir)
    summary = compute_summary(
        calls,
        guidance,
        include_dummy=include_dummy,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    if write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return summary


def _selftest() -> int:
    """In-memory smoke of the grading core (the real suite is tests/test_score.py)."""
    checks = []

    # guidance beat/met/miss
    def g(actual_val, hib=True):
        rec = {
            "id": "X", "ticker": "X", "timestamp": "t", "metric": "m", "unit": "u",
            "basis": "non_gaap", "period": "P", "guided_at_period": "P0",
            "source_filing": "http://x", "higher_is_better": hib,
            "guidance": {"kind": "range", "low": 100, "high": 110},
            "actual": {"value": actual_val, "basis": "non_gaap"},
        }
        return grade_guidance(rec)["outcome"]

    checks.append(("guid beat", g(120) == "beat"))
    checks.append(("guid met", g(105) == "met"))
    checks.append(("guid miss", g(90) == "miss"))
    checks.append(("guid lower-is-better flips", g(120, hib=False) == "miss"))

    # our direction call hit/miss
    call = {
        "id": "C", "ticker": "X", "timestamp": "t", "call_type": "preview",
        "period": "P", "metric": "m", "unit": "u", "basis": "non_gaap",
        "source_note": "n.md",
        "call": {"kind": "direction", "value": "beat",
                 "benchmark": {"kind": "range", "low": 100, "high": 110}},
        "actual": {"value": 120, "basis": "non_gaap"},
    }
    checks.append(("call direction hit", grade_call(call)["hit"] is True))

    # basis guard raises
    bad = dict(call, actual={"value": 120, "basis": "gaap"})
    try:
        grade_call(bad)
        checks.append(("basis guard raises", False))
    except BasisMismatchError:
        checks.append(("basis guard raises", True))

    # malformed raises
    try:
        validate_call({"id": "z"})
        checks.append(("malformed raises", False))
    except MalformedRecordError:
        checks.append(("malformed raises", True))

    ok = all(passed for _, passed in checks)
    for name, passed in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print("selftest:", "GREEN" if ok else "RED")
    return 0 if ok else 1


def _main(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(description="Furton Coverage scorecard engine")
    p.add_argument("--exclude-dummy", action="store_true",
                   help="drop rows flagged dummy:true (use for the real scorecard)")
    p.add_argument("--calls-dir", type=Path, default=None)
    p.add_argument("--guidance-dir", type=Path, default=None)
    p.add_argument("--out", type=Path, default=None, help="summary.json path")
    p.add_argument("--no-write", action="store_true", help="compute but do not write")
    p.add_argument("--selftest", action="store_true", help="run the in-memory smoke test")
    args = p.parse_args(argv)

    if args.selftest:
        return _selftest()

    summary = run(
        calls_dir=args.calls_dir,
        guidance_dir=args.guidance_dir,
        out_path=args.out,
        include_dummy=not args.exclude_dummy,
        write=not args.no_write,
    )
    tot = summary["totals"]
    oc = summary["our_calls"]["overall"]
    ga = summary["guidance_accuracy"]["overall"]
    print(
        f"scored {tot['call_records']} calls / {tot['guidance_records']} guidance "
        f"across {tot['tickers']} tickers"
        + (" (dummy excluded)" if args.exclude_dummy else "")
    )
    print(
        f"  our calls : {oc['hits']}/{oc['n_graded']} hit "
        f"(rate {oc['hit_rate']}), {oc['pending']} pending, {oc['qualitative']} qualitative"
    )
    print(
        f"  guidance  : beat {ga['beat']} / met {ga['met']} / missed {ga['missed']}, "
        f"{ga['pending']} pending"
    )
    for w in summary["warnings"]:
        print(f"  warning: {w}")
    if not args.no_write:
        print(f"  wrote {(args.out or _load_paths()['summary'])}")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_main(sys.argv[1:]))
