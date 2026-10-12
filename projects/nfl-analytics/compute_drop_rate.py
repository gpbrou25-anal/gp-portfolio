"""
Per-player drop rate — the WR-side counterpart to the QB's "true INT%"
idea from the whiteboard. Joins FTN charting's is_drop flag to the
receiver on each play. Run after compute_full_catalog.py.

Run with: python compute_drop_rate.py [season] [through_week]
through_week freezes a snapshot as of that week only and writes into
output/wk<N>/ instead of output/ — see compute_team_stats.py for why.
Writes: output/wr_te_drop_rate.csv (or output/wk<N>/wr_te_drop_rate.csv)
"""
import os
import sys
import pandas as pd
import nfl_data_py as nfl

SEASON = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
THROUGH_WEEK = int(sys.argv[2]) if len(sys.argv) > 2 else None
ONLY_WEEK = len(sys.argv) > 3 and sys.argv[3] == "only"  # isolates that single week instead of 1..N cumulative
OUT = f"output/wk{THROUGH_WEEK}{'only' if ONLY_WEEK else ''}" if THROUGH_WEEK else "output"


def main():
    pbp = nfl.import_pbp_data([SEASON], downcast=True)
    ftn = nfl.import_ftn_data([SEASON])
    if THROUGH_WEEK:
        pbp = pbp[pbp["week"] == THROUGH_WEEK] if ONLY_WEEK else pbp[pbp["week"] <= THROUGH_WEEK]
        if "week" in ftn.columns:
            ftn = ftn[ftn["week"] == THROUGH_WEEK] if ONLY_WEEK else ftn[ftn["week"] <= THROUGH_WEEK]

    reg = pbp[(pbp["play_type"] == "pass") & (pbp["season_type"] == "REG") & (pbp["receiver_player_name"].notna())]
    merged = reg.merge(
        ftn,
        left_on=["game_id", "play_id"],
        right_on=["nflverse_game_id", "nflverse_play_id"],
        how="inner",
        suffixes=("", "_ftn"),
    )

    grp = merged.groupby(["receiver_player_name", "posteam"]).agg(
        targets=("is_drop", "count"),
        drops=("is_drop", "sum"),
    ).reset_index()
    grp = grp[grp["targets"] >= 5]  # minimum sample to avoid one-drop-on-one-target noise
    grp["drop_rate_pct"] = round(grp["drops"] / grp["targets"] * 100, 1)
    grp = grp.rename(columns={"posteam": "team"}).sort_values("drop_rate_pct", ascending=False)

    os.makedirs(OUT, exist_ok=True)
    grp.to_csv(f"{OUT}/wr_te_drop_rate.csv", index=False)
    print(f"Wrote {OUT}/wr_te_drop_rate.csv — {len(grp)} players with 5+ targets")
    print(grp.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
