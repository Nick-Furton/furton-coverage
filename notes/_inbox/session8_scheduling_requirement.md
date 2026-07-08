# REQUIREMENT for Session 8 (Automation) — schedule the daily job in the CLOUD, not locally

**Raised by:** Session 1, 2026-07-08 (at Nick's explicit request).
**Applies to:** PLAN §8 item (1) — the daily `refresh_calendar.py` + "reports within 48h" notify job.
**Full rationale lives in the header of `scripts/refresh_calendar.py`** (the file Session 8 extends);
this note just makes it discoverable at the Phase 3→4 merge gate so it isn't missed.

## The requirement

Wire the daily calendar-refresh/notify job as a **cloud scheduled agent** (the `schedule` skill's
cron routine), **NOT a local Windows Task Scheduler task.**

**Why:** the whole EDGAR spine is no-auth and fully headless, so the daily job has no reason to
depend on Nick's computer being awake. A local scheduled task only fires when the machine is on —
which turns the laptop into a pager that can't sleep at the scheduled minute. A cloud routine runs
regardless of the laptop's state and can push the "NVDA reports in <48h — run /preview NVDA"
notification to Nick's phone.

**The outcome Nick wants:** with cloud scheduling, the computer can stay **asleep for all daily
automation**; it only needs to be awake when Nick is actively driving `/preview` `/flash` `/review`
`/digest` around an actual print (a handful of afternoons per earnings cluster, a few times a year).

## Fallback (only if a cloud routine is genuinely unavailable)

Use a local Task Scheduler task **only** as a last resort, and if so:
- enable **"Wake the computer to run this task,"** and
- document in `RUNBOOK.md` that daily automation then requires the laptop plugged in / not fully
  powered off.

Do not silently ship a daily job that only works when the machine happens to be on.

## Related

- Session 8 is also chartered to prototype a **headless flash-draft** (PLAN §8 item 4). Same logic:
  if that runs cloud-side, even earnings-day moves toward "computer asleep, Nick skims a draft on his
  phone." Worth building on the same cloud-scheduling foundation.
