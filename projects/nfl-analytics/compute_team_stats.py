"""
NFL Team Diagnostic — core stats engine.

Pulls real nflverse (nflfastR) play-by-play + schedule data for the given
season and computes a team-level table covering the "core" metrics from
the project brief: record, PPG/PA, offensive & defensive EPA per play,
success rate, yards per play, 3rd/4th down conversion (offense & defense),
takeaway/giveaway margin, and hot/cold start flag.

This is deliberately the FIRST pass — the deeper film-charting-style
metrics (coverage type, pressure scheme, quarter-by-quarter tendency
breakdown) need either richer NGS data or the whiteboard photos to define
precisely, and come in a second pass once those are confirmed.

Run with: python compute_team_stats.py [season] [through_week]
through_week freezes a snapshot as of that week only (e.g. `2026 2` = only
weeks 1-2 count, even if more have been played since) and writes into
output/wk<N>/ instead of the root — used for the "with Week 3 data" toggle
in viewer_app.py so you can see the pattern before/after a week landed.
Writes: team_stats_<season>.csv and team_stats_<season>.json
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import nfl_data_py as nfl

SEASON = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
THROUGH_WEEK = int(sys.argv[2]) if len(sys.argv) > 2 else None
ONLY_WEEK = len(sys.argv) > 3 and sys.argv[3] == "only"  # isolates that single week instead of 1..N cumulative


def main():
    print(f"Pulling schedule + play-by-play for {SEASON} ...")
    sched = nfl.import_schedules([SEASON])
    pbp = nfl.import_pbp_data([SEASON], downcast=True)

    played = sched.dropna(subset=["home_score"]).copy()
    if THROUGH_WEEK:
        played = played[played["week"] == THROUGH_WEEK] if ONLY_WEEK else played[played["week"] <= THROUGH_WEEK]
        pbp = pbp[pbp["week"] == THROUGH_WEEK] if ONLY_WEEK else pbp[pbp["week"] <= THROUGH_WEEK]
    max_week = int(played["week"].max())
    print(f"Weeks with completed games: up to week {max_week} ({len(played)} games)")

    teams = sorted(set(sched["home_team"]).union(sched["away_team"]))
    rows = []

    reg_plays = pbp[(pbp["play_type"].isin(["pass", "run"])) & (pbp["season_type"] == "REG")]
    # Safeties often land on a no_play (accepted penalty) row, so they need the
    # unfiltered REG pbp, not reg_plays (pass/run only) — sourcing from a
    # narrower filter would silently drop real ones.
    reg_all = pbp[pbp["season_type"] == "REG"]

    for team in teams:
        team_games = played[(played["home_team"] == team) | (played["away_team"] == team)]
        wins = losses = ties = pf = pa = 0
        weekly_margin = []
        for _, g in team_games.iterrows():
            is_home = g["home_team"] == team
            team_score = g["home_score"] if is_home else g["away_score"]
            opp_score = g["away_score"] if is_home else g["home_score"]
            pf += team_score
            pa += opp_score
            margin = team_score - opp_score
            weekly_margin.append((int(g["week"]), margin))
            if team_score > opp_score:
                wins += 1
            elif team_score < opp_score:
                losses += 1
            else:
                ties += 1
        n = len(team_games)

        off = reg_plays[reg_plays["posteam"] == team]
        deff = reg_plays[reg_plays["defteam"] == team]

        def safe_mean(s):
            return round(float(s.mean()), 3) if len(s) else None

        off_epa = safe_mean(off["epa"])
        def_epa_allowed = safe_mean(deff["epa"])
        off_success = safe_mean(off["success"])
        def_success_allowed = safe_mean(deff["success"])
        off_ypp = safe_mean(off["yards_gained"])
        def_ypp_allowed = safe_mean(deff["yards_gained"])

        def conv_rate(df, down):
            d = df[df["down"] == down]
            if not len(d):
                return None
            return round(float((d["third_down_converted"].fillna(0) + d["fourth_down_converted"].fillna(0)).clip(0, 1).mean()), 3) if "third_down_converted" in d.columns else None

        third_off = off[off["down"] == 3]
        third_off_conv = round(float(third_off["third_down_converted"].mean()), 3) if len(third_off) and "third_down_converted" in third_off.columns else None
        third_def = deff[deff["down"] == 3]
        third_def_conv_allowed = round(float(third_def["third_down_converted"].mean()), 3) if len(third_def) and "third_down_converted" in third_def.columns else None

        fourth_off = off[off["down"] == 4]
        fourth_off_attempts = int(len(fourth_off))
        fourth_off_conv = round(float(fourth_off["fourth_down_converted"].mean()), 3) if len(fourth_off) and "fourth_down_converted" in fourth_off.columns else None

        turnovers_forced = int(deff["interception"].fillna(0).sum() + deff["fumble_lost"].fillna(0).sum())
        turnovers_given = int(off["interception"].fillna(0).sum() + off["fumble_lost"].fillna(0).sum())

        pick_six_td = int(((deff["interception"] == 1) & (deff["return_touchdown"] == 1)).sum())
        fumble_return_td = int(((deff["fumble_lost"] == 1) & (deff["return_touchdown"] == 1)).sum())
        safeties_forced = int((reg_all[reg_all["defteam"] == team]["safety"] == 1).sum())

        # hot/cold start: margin trend across played weeks (simple linear slope sign)
        if len(weekly_margin) >= 2:
            wm = sorted(weekly_margin)
            xs = np.array([w for w, _ in wm], dtype=float)
            ys = np.array([m for _, m in wm], dtype=float)
            slope = float(np.polyfit(xs, ys, 1)[0]) if len(xs) > 1 else 0.0
        else:
            slope = 0.0

        rows.append({
            "team": team,
            "games": n,
            "wins": wins, "losses": losses, "ties": ties,
            "ppg": round(pf / n, 1) if n else None,
            "pa_pg": round(pa / n, 1) if n else None,
            "point_diff": pf - pa,
            "off_epa_play": off_epa,
            "def_epa_play_allowed": def_epa_allowed,
            "off_success_rate": off_success,
            "def_success_rate_allowed": def_success_allowed,
            "off_yards_play": off_ypp,
            "def_yards_play_allowed": def_ypp_allowed,
            "third_down_off_conv": third_off_conv,
            "third_down_def_conv_allowed": third_def_conv_allowed,
            "fourth_down_off_attempts": fourth_off_attempts,
            "fourth_down_off_conv": fourth_off_conv,
            "takeaways": turnovers_forced,
            "giveaways": turnovers_given,
            "turnover_margin": turnovers_forced - turnovers_given,
            "pick_six_td": pick_six_td,
            "fumble_return_td": fumble_return_td,
            "defensive_takeaway_tds": pick_six_td + fumble_return_td,
            "safeties_forced": safeties_forced,
            "margin_trend_slope": round(slope, 2),
        })

    df = pd.DataFrame(rows).sort_values("point_diff", ascending=False)
    if THROUGH_WEEK:
        wk_dir = f"wk{THROUGH_WEEK}{'only' if ONLY_WEEK else ''}"
        os.makedirs(f"output/{wk_dir}", exist_ok=True)
        out_csv = f"output/{wk_dir}/team_stats_{SEASON}.csv"
        out_json = f"output/{wk_dir}/team_stats_{SEASON}.json"
    else:
        out_csv = f"team_stats_{SEASON}.csv"
        out_json = f"team_stats_{SEASON}.json"
    df.to_csv(out_csv, index=False)
    df.to_json(out_json, orient="records", indent=2)
    print(f"\nWrote {out_csv} and {out_json} — {len(df)} teams, through week {max_week}.\n")
    print(df[["team", "wins", "losses", "ppg", "pa_pg", "point_diff", "off_epa_play", "def_epa_play_allowed", "turnover_margin"]].to_string(index=False))


if __name__ == "__main__":
    main()
