#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""refresh_calendar.py — build config/calendar.json (next earnings event per ticker).

Session 1 (scaffold) owns this. It reads config/universe.json and writes
config/calendar.json with each covered name's NEXT earnings date, so downstream
sessions (and Session 8's daily scheduled task) know when to fire /preview, /flash,
and /review.

WHY NOT EDGAR? Future earnings *dates* are not on SEC EDGAR — EDGAR only carries
filings that already happened. The kickoff is explicit that "web search is fine as
the source." So the authoritative input here is a small web-search-sourced SEED
file (ticker -> date + citation); a session with the WebSearch tool, or Nick, fills
it. An OPTIONAL live HTTP provider (--provider nasdaq) is attempted best-effort for
headless automation, but public earnings-calendar endpoints frequently block bots,
so it must degrade honestly, never invent a date.

FAIL-LOUD CONTRACT (same philosophy as Furton Research's vote parser):
  * A ticker that cannot be resolved is recorded status="unresolved" with a reason
    and listed in the top-level "unresolved" array. It is NEVER given a guessed date.
  * A previously-resolved date is PRESERVED across a refresh that can't re-resolve it
    (a transient fetch failure must not wipe good data) — but it is flagged stale.
  * Exit code is non-zero if ANY covered (candidate=true) ticker is unresolved,
    unless --allow-unresolved is passed. This makes a scheduled run's failure visible.

This module does NOT touch SEC EDGAR APIs — scripts/edgar.py (Session 2) owns those.

=============================================================================
SESSION 8 AUTOMATION REQUIREMENT — schedule this in the CLOUD, not locally.
=============================================================================
When Session 8 wires the "daily calendar refresh + 48h-warning" job (PLAN §8),
it MUST run as a CLOUD scheduled agent (the `schedule` skill's routine / cron
agent), NOT as a local Windows Task Scheduler task. Rationale:
  * This script + the whole EDGAR spine are no-auth and fully headless, so the
    daily job has no reason to depend on Nick's machine being on.
  * A LOCAL scheduled task only fires when the computer is awake — turning the
    laptop into a pager that must never sleep at the scheduled minute. A cloud
    routine runs regardless of the laptop's state and can push the "X reports in
    <48h, run /preview X" notification to Nick's phone.
  * Net effect Nick asked for: with cloud scheduling the computer can stay
    ASLEEP for all daily automation; it only needs to be awake when Nick is
    actively driving /preview /flash /review /digest around a print.
If a cloud routine is genuinely unavailable and a local task is the only option,
enable Task Scheduler's "Wake the computer to run this task" AND document the
degraded behavior (laptop must be plugged in / not fully powered off) in
RUNBOOK.md — do not silently ship a job that only works when the machine happens
to be on. (Mirror this note in notes/_inbox/ so it also surfaces at the gate.)
=============================================================================

Windows: run with `py`; set PYTHONUTF8=1 (console is cp1252).

Usage:
  py scripts/refresh_calendar.py                          # seed provider (default), reads config/calendar.seed.json if present
  py scripts/refresh_calendar.py --seed path/to/seed.json # explicit seed file
  py scripts/refresh_calendar.py --provider nasdaq        # best-effort live HTTP scan (may be blocked)
  py scripts/refresh_calendar.py --ticker NVDA            # limit to one ticker
  py scripts/refresh_calendar.py --dry-run                # print, do not write
  py scripts/refresh_calendar.py --as-of 2026-07-08       # pin "today" (testing / reproducibility)

Seed file format (web-search-sourced; every entry SHOULD carry a source_url):
  {
    "NVDA": {"date": "2026-08-26", "confidence": "estimated",
             "time_of_day": "after_market", "source_url": "https://..."},
    "UNH":  {"date": "2026-07-15", "confidence": "confirmed",
             "time_of_day": "before_market", "source_url": "https://..."}
  }
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import NoReturn

# --- make stdout tolerant of the cp1252 Windows console (belt-and-suspenders vs PYTHONUTF8) ---
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover - older Pythons
    pass

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / "config"
SETTINGS_PATH = CONFIG / "settings.json"
UNIVERSE_PATH = CONFIG / "universe.json"
CALENDAR_PATH = CONFIG / "calendar.json"
DEFAULT_SEED_PATH = CONFIG / "calendar.seed.json"

VALID_CONFIDENCE = {"confirmed", "estimated", "unknown"}
VALID_TOD = {"before_market", "after_market", "during_market", "unknown"}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def die(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def load_json(path: Path) -> dict:
    if not path.exists():
        die(f"required file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{path} is not valid JSON: {e}")


def load_settings() -> dict:
    return load_json(SETTINGS_PATH)


def covered_tickers(universe: dict) -> list[dict]:
    """Return universe entries flagged candidate=true (the working roster)."""
    entries = universe.get("universe", [])
    if not entries:
        die("universe.json has no 'universe' array — Session 1 must populate it first.")
    return [e for e in entries if e.get("candidate") is True]


def parse_date(s: str) -> dt.date:
    return dt.datetime.strptime(s, "%Y-%m-%d").date()


def normalize_seed_entry(ticker: str, raw: dict) -> dict:
    """Validate one seed entry, FAIL LOUD on bad shape (no silent coercion)."""
    if "date" not in raw:
        die(f"seed[{ticker}] missing 'date'")
    try:
        d = parse_date(raw["date"])
    except ValueError:
        die(f"seed[{ticker}] date {raw['date']!r} is not YYYY-MM-DD")
    conf = raw.get("confidence", "unknown")
    if conf not in VALID_CONFIDENCE:
        die(f"seed[{ticker}] confidence {conf!r} not in {sorted(VALID_CONFIDENCE)}")
    tod = raw.get("time_of_day", "unknown")
    if tod not in VALID_TOD:
        die(f"seed[{ticker}] time_of_day {tod!r} not in {sorted(VALID_TOD)}")
    return {
        "date": d.isoformat(),
        "confidence": conf,
        "time_of_day": tod,
        "source": "web_search",
        "source_url": raw.get("source_url", ""),
    }


# --------------------------------------------------------------------------- #
# providers — each returns {date, confidence, time_of_day, source, source_url}
#            or None if it cannot resolve the ticker (caller handles fail-loud)
# --------------------------------------------------------------------------- #
def provider_seed(tickers: list[str], seed_path: Path) -> dict[str, dict]:
    """Authoritative provider: a web-search-sourced JSON of dates + citations."""
    if not seed_path.exists():
        print(
            f"note: seed file {seed_path} not found — no dates to apply from 'seed' provider.\n"
            f"      Populate it from a web search (see this file's docstring) or use --seed.",
            file=sys.stderr,
        )
        return {}
    raw = load_json(seed_path)
    out: dict[str, dict] = {}
    for t in tickers:
        if t in raw:
            out[t] = normalize_seed_entry(t, raw[t])
    return out


def provider_nasdaq(tickers: list[str], settings: dict, as_of: dt.date,
                    horizon_days: int = 120) -> dict[str, dict]:
    """Best-effort live scan of the Nasdaq public earnings calendar.

    Scans forward from as_of, one weekday at a time, matching universe tickers.
    Public earnings endpoints routinely block non-browser clients, so this is a
    NICE-TO-HAVE for headless runs; failures are swallowed per-day and any ticker
    left unmatched is simply not returned (caller then marks it unresolved).
    """
    ua = settings["sec"]["user_agent"]  # honest contact identity; reused as polite UA
    min_interval = settings["sec"].get("min_interval_ms", 100) / 1000.0
    timeout = settings["sec"].get("timeout_sec", 30)
    wanted = set(tickers)
    found: dict[str, dict] = {}

    day = as_of
    scanned = 0
    while wanted and scanned < horizon_days:
        if day.weekday() < 5:  # Mon-Fri only
            url = f"https://api.nasdaq.com/api/calendar/earnings?date={day.isoformat()}"
            req = urllib.request.Request(
                url, headers={"User-Agent": ua, "Accept": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    payload = json.loads(r.read().decode("utf-8"))
                rows = ((payload or {}).get("data") or {}).get("rows") or []
                for row in rows:
                    sym = (row.get("symbol") or "").upper()
                    if sym in wanted:
                        found[sym] = {
                            "date": day.isoformat(),
                            "confidence": "confirmed",
                            "time_of_day": _nasdaq_tod(row.get("time", "")),
                            "source": "nasdaq",
                            "source_url": url,
                        }
                        wanted.discard(sym)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as e:
                print(f"  nasdaq {day}: fetch failed ({type(e).__name__}) — skipping day",
                      file=sys.stderr)
            time.sleep(min_interval)
        day += dt.timedelta(days=1)
        scanned += 1
    return found


def _nasdaq_tod(raw: str) -> str:
    raw = (raw or "").lower()
    if "pre" in raw or "before" in raw:
        return "before_market"
    if "after" in raw or "post" in raw:
        return "after_market"
    return "unknown"


# --------------------------------------------------------------------------- #
# assembly
# --------------------------------------------------------------------------- #
def build_calendar(universe: dict, resolved: dict[str, dict],
                   prior: dict, as_of: dt.date, warn_hours: int,
                   in_scope: set[str] | None = None) -> dict:
    """Assemble calendar.json.

    in_scope = the tickers this run actually refreshed (from --ticker). Tickers
    OUTSIDE the scope are carried over verbatim from the prior calendar (NOT
    relabeled stale) — a single-ticker refresh must not touch the rest. 'stale'
    is reserved for a ticker that WAS in scope but could not be re-resolved.
    None means every covered ticker is in scope (a full refresh).
    """
    warn_days = warn_hours / 24.0
    prior_events = (prior or {}).get("events", {})
    events: dict[str, dict] = {}
    unresolved: list[str] = []

    for entry in covered_tickers(universe):
        t = entry["ticker"]
        base = {
            "ticker": t,
            "cik": entry.get("cik"),
            "company": entry.get("company"),
        }
        if in_scope is not None and t not in in_scope:
            # not refreshed this run — preserve prior entry exactly, or skip if none
            if t in prior_events:
                events[t] = prior_events[t]
            continue
        r = resolved.get(t)
        if r is None:
            # try to preserve a still-future prior date so a transient miss doesn't wipe it
            p = prior_events.get(t)
            if p and p.get("next_earnings_date") and p.get("status") == "resolved":
                try:
                    if parse_date(p["next_earnings_date"]) >= as_of:
                        preserved = dict(p)
                        preserved["stale"] = True
                        preserved["note"] = "preserved from prior calendar; not re-resolved this run"
                        events[t] = preserved
                        continue
                except ValueError:
                    pass
            events[t] = {
                **base,
                "next_earnings_date": None,
                "time_of_day": "unknown",
                "confidence": "unknown",
                "source": None,
                "source_url": None,
                "days_until": None,
                "within_warn_window": False,
                "status": "unresolved",
                "stale": False,
                "note": "no date from any provider — supply via seed file (web search)",
                "fetched_at": as_of.isoformat(),
            }
            unresolved.append(t)
            continue

        d = parse_date(r["date"])
        days_until = (d - as_of).days
        events[t] = {
            **base,
            "next_earnings_date": r["date"],
            "time_of_day": r.get("time_of_day", "unknown"),
            "confidence": r.get("confidence", "unknown"),
            "source": r.get("source"),
            "source_url": r.get("source_url", ""),
            "days_until": days_until,
            "within_warn_window": 0 <= days_until <= warn_days,
            "status": "resolved" if days_until >= 0 else "past",
            "stale": False,
            "note": "" if days_until >= 0 else "resolved date is in the past — needs refresh",
            "fetched_at": as_of.isoformat(),
        }

    return {
        "_schema": {
            "description": "Next earnings event per covered ticker. GENERATED by scripts/refresh_calendar.py — do not hand-edit; edit config/calendar.seed.json (web-search-sourced dates) and re-run.",
            "event_fields": {
                "next_earnings_date": "YYYY-MM-DD or null if unresolved.",
                "time_of_day": "before_market | after_market | during_market | unknown.",
                "confidence": "confirmed (company/exchange announced) | estimated (projected from history) | unknown.",
                "source": "seed provider -> 'web_search'; live provider -> 'nasdaq'; null if unresolved.",
                "source_url": "citation for the date (required for web_search entries).",
                "days_until": "as_of -> next_earnings_date, in days.",
                "within_warn_window": "true if 0 <= days_until <= warn_within_hours/24 (Session 8's notify trigger).",
                "status": "resolved | unresolved | past.",
                "stale": "true if preserved from a prior run because this run could not re-resolve it."
            }
        },
        "generated_at": as_of.isoformat(),
        "generator": "scripts/refresh_calendar.py",
        "as_of": as_of.isoformat(),
        "warn_within_hours": warn_hours,
        "resolved_count": sum(1 for e in events.values() if e.get("next_earnings_date")),
        "unresolved_count": len(unresolved),
        "unresolved": unresolved,
        "events": events,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Refresh config/calendar.json from a web-search seed (default) or a best-effort live provider.")
    ap.add_argument("--provider", choices=["seed", "nasdaq"], default="seed",
                    help="seed = web-search-sourced JSON (default, reliable); nasdaq = best-effort live scan.")
    ap.add_argument("--seed", type=Path, default=DEFAULT_SEED_PATH,
                    help=f"seed JSON path (default {DEFAULT_SEED_PATH}).")
    ap.add_argument("--ticker", action="append", default=None,
                    help="limit to this ticker (repeatable).")
    ap.add_argument("--as-of", default=None,
                    help="pin 'today' as YYYY-MM-DD (default: system date).")
    ap.add_argument("--dry-run", action="store_true", help="print result, do not write calendar.json.")
    ap.add_argument("--allow-unresolved", action="store_true",
                    help="exit 0 even if some covered tickers are unresolved.")
    args = ap.parse_args(argv)

    settings = load_settings()
    universe = load_json(UNIVERSE_PATH)
    warn_hours = settings.get("calendar", {}).get("warn_within_hours", 48)

    if args.as_of:
        try:
            as_of = parse_date(args.as_of)
        except ValueError:
            die(f"--as-of {args.as_of!r} is not YYYY-MM-DD")
    else:
        as_of = dt.date.today()

    tickers = [e["ticker"] for e in covered_tickers(universe)]
    if args.ticker:
        want = {t.upper() for t in args.ticker}
        missing = want - set(tickers)
        if missing:
            die(f"--ticker names not in the candidate universe: {sorted(missing)}")
        tickers = [t for t in tickers if t in want]

    print(f"refresh_calendar: provider={args.provider} as_of={as_of} tickers={len(tickers)}")

    if args.provider == "seed":
        resolved = provider_seed(tickers, args.seed)
    else:
        resolved = provider_nasdaq(tickers, settings, as_of)

    prior = load_json(CALENDAR_PATH) if CALENDAR_PATH.exists() else {}
    calendar = build_calendar(universe, resolved, prior, as_of, warn_hours,
                              in_scope=set(tickers))

    # report (only the tickers this run refreshed)
    print(f"  resolved={calendar['resolved_count']}  unresolved={calendar['unresolved_count']}")
    for t in tickers:
        ev = calendar["events"].get(t, {})
        date = ev.get("next_earnings_date") or "--------"
        du = ev.get("days_until")
        dcol = f"{du:+d}" if isinstance(du, int) else "  ?"
        warn = " [WARN <48h]" if ev.get("within_warn_window") else ""
        stale = " [stale]" if ev.get("stale") else ""
        print(f"    {t:6s} {date}  d{dcol:>5}  "
              f"{ev.get('confidence','?'):9s} {ev.get('status','?')}{warn}{stale}")
    if calendar["unresolved"]:
        print(f"  UNRESOLVED: {', '.join(calendar['unresolved'])}", file=sys.stderr)

    if args.dry_run:
        print("  --dry-run: not writing.")
    else:
        CALENDAR_PATH.write_text(json.dumps(calendar, indent=2) + "\n", encoding="utf-8")
        print(f"  wrote {CALENDAR_PATH}")

    if calendar["unresolved"] and not args.allow_unresolved:
        print("  exiting non-zero: unresolved tickers (pass --allow-unresolved to suppress).",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
