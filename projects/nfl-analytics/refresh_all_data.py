"""
One-shot full data refresh — run this after any batch of games finishes
(e.g. every Tuesday morning once Monday Night Football is final) instead of
running each compute_*.py script by hand.

What it does, in order:
  1. Live/current data (no snapshot arg) — the root CSVs + team_ledger.json +
     METRIC_GLOSSARY.pdf that viewer_app.py's "Latest (cumulative)" view reads.
  2. Re-freezes output/wk<week>/   — cumulative-through-that-week snapshot.
  3. Re-freezes output/wk<week>only/ — that single week in isolation.

Both snapshots exist so a stale snapshot (the actual bug this script exists to
prevent — see 2026-10-08) can never silently linger after more games finish.

Usage:
    python refresh_all_data.py <week_number>
    python refresh_all_data.py 4
"""
import subprocess
import sys

PY = sys.executable  # run with the same interpreter this script was launched with

REAL_DATA_SCRIPTS = [
    "compute_team_stats.py",
    "compute_full_catalog.py",
    "compute_drop_rate.py",
    "compute_special_teams.py",
    "compute_player_level.py",
    "compute_quarter_splits.py",
]
DOWNSTREAM_SCRIPTS = [
    "compute_league_standings.py",
    "compute_team_ledger.py",
    "generate_glossary_pdf.py",
]


def run(args, label):
    print(f"\n=== {label} ===")
    result = subprocess.run([PY, *args], capture_output=True, text=True)
    print(result.stdout[-1500:])
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise SystemExit(f"FAILED: {label}")


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python refresh_all_data.py <week_number>  (e.g. 4)")
    week = sys.argv[1]

    print(f"Refreshing all NFL data — through week {week}.")

    for script in REAL_DATA_SCRIPTS:
        run([script], f"live: {script}")
    for script in DOWNSTREAM_SCRIPTS:
        run([script], f"live downstream: {script}")

    for script in REAL_DATA_SCRIPTS:
        run([script, "2026", week], f"snapshot wk{week}: {script}")

    for script in REAL_DATA_SCRIPTS:
        run([script, "2026", week, "only"], f"snapshot wk{week}only: {script}")

    print(f"\nDone. Live data, output/wk{week}/, and output/wk{week}only/ are all current.")
    print("Restart league_overview_app.py and viewer_app.py to pick up the refresh.")


if __name__ == "__main__":
    main()
