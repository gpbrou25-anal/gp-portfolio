"""
Special teams — the 3 core numbers: FG% by distance bucket, punt/kickoff
net average, and return yards (allowed/gained). Deliberately kept short —
smallest phase of the game, per your call to not over-invest here.

Run with: python compute_special_teams.py [season] [through_week]
through_week freezes a snapshot as of that week only and writes into
output/wk<N>/ instead of output/ — see compute_team_stats.py for why.
Writes: output/special_teams.csv (or output/wk<N>/special_teams.csv)
"""
import os
import sys
import pandas as pd
import nfl_data_py as nfl

SEASON = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
THROUGH_WEEK = int(sys.argv[2]) if len(sys.argv) > 2 else None
ONLY_WEEK = len(sys.argv) > 3 and sys.argv[3] == "only"  # isolates that single week instead of 1..N cumulative
OUT = f"output/wk{THROUGH_WEEK}{'only' if ONLY_WEEK else ''}" if THROUGH_WEEK else "output"


def fg_bucket(d):
    if d < 30:
        return "<30"
    if d < 40:
        return "30-39"
    if d < 50:
        return "40-49"
    return "50+"


def main():
    pbp = nfl.import_pbp_data([SEASON], downcast=True)
    if THROUGH_WEEK:
        pbp = pbp[pbp["week"] == THROUGH_WEEK] if ONLY_WEEK else pbp[pbp["week"] <= THROUGH_WEEK]
    reg = pbp[pbp["season_type"] == "REG"]
    teams = sorted(set(reg["posteam"].dropna().unique()))

    fg = reg[reg["field_goal_attempt"] == 1].copy()
    fg["bucket"] = fg["kick_distance"].apply(fg_bucket)

    punts = reg[reg["punt_attempt"] == 1].copy()
    punts["net_yards"] = punts["kick_distance"] - punts["return_yards"].fillna(0)

    kicks = reg[reg["kickoff_attempt"] == 1].copy()
    kicks["net_yards"] = kicks["kick_distance"] - kicks["return_yards"].fillna(0)

    rows = []
    for team in teams:
        team_fg = fg[fg["posteam"] == team]
        made = team_fg[team_fg["field_goal_result"] == "made"]
        fg_pct_by_bucket = {}
        for b in ["<30", "30-39", "40-49", "50+"]:
            att = team_fg[team_fg["bucket"] == b]
            made_b = len(made[made["bucket"] == b])
            fg_pct_by_bucket[f"fg_att_{b}"] = len(att)
            fg_pct_by_bucket[f"fg_made_{b}"] = made_b
            fg_pct_by_bucket[f"fg_pct_{b}"] = round(made_b / len(att) * 100, 1) if len(att) else None

        team_punts = punts[punts["posteam"] == team]
        team_kicks = kicks[kicks["posteam"] == team]
        # return defense: yards this team allowed as the receiving/return team
        opp_punts_returned = punts[punts["return_team"] == team]
        opp_kicks_returned = kicks[kicks["return_team"] == team]

        rows.append({
            "team": team,
            "fg_attempts": len(team_fg),
            "fg_made": len(made),
            "fg_pct_overall": round(len(made) / len(team_fg) * 100, 1) if len(team_fg) else None,
            **fg_pct_by_bucket,
            "punts": len(team_punts),
            "punt_net_avg": round(float(team_punts["net_yards"].mean()), 1) if len(team_punts) else None,
            "kickoff_net_avg": round(float(team_kicks["net_yards"].mean()), 1) if len(team_kicks) else None,
            "punt_return_yards_gained": int(punts[punts["return_team"] == team]["return_yards"].fillna(0).sum()),
            "kick_return_yards_gained": int(kicks[kicks["return_team"] == team]["return_yards"].fillna(0).sum()),
        })

    df = pd.DataFrame(rows).sort_values("fg_pct_overall", ascending=False)
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(f"{OUT}/special_teams.csv", index=False)
    print(f"Wrote {OUT}/special_teams.csv — {len(df)} teams")
    print(df[["team", "fg_pct_overall", "punt_net_avg", "kickoff_net_avg"]].to_string(index=False))


if __name__ == "__main__":
    main()
