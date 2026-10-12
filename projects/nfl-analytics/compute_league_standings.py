"""
League-wide standings + auto-pulled player examples, for the analytics
report (distinct from the per-team scouting form). Reads the CSVs already
written by compute_team_stats.py / compute_full_catalog.py /
compute_player_level.py — computes nothing new from play-by-play itself.

For each of the six "trust first" categories in SCOUTING_FORM.md section 3,
ranks all 32 teams and identifies the individual player most responsible
for the best and worst team's number, pulled from the real player-level
files (never invented).

Run with: python compute_league_standings.py
Writes: output/league_standings.json
"""
import json
import pandas as pd

OUT = "output"


def top_player(df, team, sort_col, ascending=False, min_col=None, min_val=0):
    t = df[df["team"] == team]
    if min_col:
        t = t[t[min_col] >= min_val]
    if not len(t):
        return None
    t = t.sort_values(sort_col, ascending=ascending)
    row = t.iloc[0]
    return {"player": row["player"], "value": row[sort_col]}


def rank_board(df, col, ascending, label_high, label_low):
    d = df.dropna(subset=[col]).sort_values(col, ascending=ascending).reset_index(drop=True)
    d["rank"] = range(1, len(d) + 1)
    return d, label_high, label_low


def main():
    team_stats = pd.read_csv("team_stats_2026.csv")
    qb_stats = pd.read_csv(f"{OUT}/qb_stats.csv")
    qb_player = pd.read_csv(f"{OUT}/qb_player_level.csv")
    ol_dl = pd.read_csv(f"{OUT}/ol_dl_stats.csv")
    rb_stats = pd.read_csv(f"{OUT}/rb_stats.csv")
    rb_player = pd.read_csv(f"{OUT}/rb_player_level.csv")
    wr_te = pd.read_csv(f"{OUT}/wr_te_team_level.csv")
    wr_te_player = pd.read_csv(f"{OUT}/wr_te_player_level_ngs.csv").rename(columns={"team_abbr": "team", "player_display_name": "player"})
    lb_db = pd.read_csv(f"{OUT}/lb_db_team_level.csv")

    max_games = int(team_stats["games"].max())
    min_games = int(team_stats["games"].min())

    boards = {}

    # 1. QB — EPA/dropback (trust first), CPOE (trust second)
    d, _, _ = rank_board(qb_stats, "epa_per_dropback", ascending=False, label_high="best", label_low="worst")
    best_team, worst_team = d.iloc[0]["team"], d.iloc[-1]["team"]
    boards["qb_epa"] = {
        "metric": "EPA per dropback", "table": d[["rank", "team", "epa_per_dropback", "cpoe"]].to_dict("records"),
        "best_team": best_team, "worst_team": worst_team,
        "best_player": top_player(qb_player, best_team, "attempts", ascending=False),
        "worst_player": top_player(qb_player, worst_team, "attempts", ascending=False),
    }

    # 2. O-Line — QB hits allowed (fewer = better)
    d, _, _ = rank_board(ol_dl, "qb_hits_allowed", ascending=True, label_high="best", label_low="worst")
    boards["ol_hits_allowed"] = {
        "metric": "QB hits allowed", "table": d[["rank", "team", "qb_hits_allowed", "sacks_allowed_by_OL"]].to_dict("records"),
        "best_team": d.iloc[0]["team"], "worst_team": d.iloc[-1]["team"],
    }

    # 3. RB — % carries 4+ yards (trust first), explosive rate (trust second)
    d, _, _ = rank_board(rb_stats, "pct_carries_4plus_yards", ascending=False, label_high="best", label_low="worst")
    best_team, worst_team = d.iloc[0]["team"], d.iloc[-1]["team"]
    boards["rb_consistency"] = {
        "metric": "% carries gaining 4+ yards", "table": d[["rank", "team", "pct_carries_4plus_yards", "explosive_run_rate_10plus"]].to_dict("records"),
        "best_team": best_team, "worst_team": worst_team,
        "best_player": top_player(rb_player, best_team, "carries", ascending=False),
        "worst_player": top_player(rb_player, worst_team, "carries", ascending=False),
    }

    # 4. WR/TE — avg separation (trust first), YAC over expected (descriptive)
    d, _, _ = rank_board(wr_te, "avg_separation", ascending=False, label_high="best", label_low="worst")
    best_team, worst_team = d.iloc[0]["team"], d.iloc[-1]["team"]
    boards["wr_separation"] = {
        "metric": "Avg. separation (yards)", "table": d[["rank", "team", "avg_separation", "avg_yac_above_expected"]].to_dict("records"),
        "best_team": best_team, "worst_team": worst_team,
        "best_player": top_player(wr_te_player, best_team, "targets", ascending=False),
        "worst_player": top_player(wr_te_player, worst_team, "targets", ascending=False),
    }

    # 5. CB/Secondary — yards allowed per target (fewer = better)
    d, _, _ = rank_board(lb_db, "yards_allowed_per_target", ascending=True, label_high="best", label_low="worst")
    boards["secondary_yards_allowed"] = {
        "metric": "Yards allowed per target", "table": d[["rank", "team", "yards_allowed_per_target", "completion_pct_allowed"]].to_dict("records"),
        "best_team": d.iloc[0]["team"], "worst_team": d.iloc[-1]["team"],
    }

    # 6. Team overall — turnover margin + EPA differential (trust first), point diff (trust second)
    team_stats["epa_diff"] = (team_stats["off_epa_play"] - team_stats["def_epa_play_allowed"]).round(3)
    d, _, _ = rank_board(team_stats, "epa_diff", ascending=False, label_high="best", label_low="worst")
    boards["team_epa_diff"] = {
        "metric": "EPA differential (off minus def allowed)",
        "table": d[["rank", "team", "epa_diff", "turnover_margin", "point_diff", "wins", "losses", "games"]].to_dict("records"),
        "best_team": d.iloc[0]["team"], "worst_team": d.iloc[-1]["team"],
    }

    out = {
        "min_games": min_games, "max_games": max_games,
        "generated_note": f"Standings through {max_games} game(s) for the furthest-along team, as few as {min_games} for others.",
        "boards": boards,
    }
    with open(f"{OUT}/league_standings.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Wrote {OUT}/league_standings.json — games played range {min_games}-{max_games}")
    for k, b in boards.items():
        print(f"  {k}: best={b['best_team']}, worst={b['worst_team']}")


if __name__ == "__main__":
    main()
