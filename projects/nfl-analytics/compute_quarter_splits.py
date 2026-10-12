"""
Team performance split by quarter — scoring, giveaways, completion %, and
run/pass tendency, each broken out Q1-Q4 (+ OT), computed directly from
play-by-play. Answers "how much are they scoring this quarter vs. that
quarter," "when are they losing the ball," "what do they run late vs. early."

Run with: python compute_quarter_splits.py [season] [through_week]
through_week freezes a snapshot as of that week only and writes into
output/wk<N>/ instead of output/ — see compute_team_stats.py for why.
Writes: output/quarter_splits.csv (long format: one row per team per quarter)
"""
import os
import sys
import pandas as pd
import nfl_data_py as nfl

SEASON = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
THROUGH_WEEK = int(sys.argv[2]) if len(sys.argv) > 2 else None
ONLY_WEEK = len(sys.argv) > 3 and sys.argv[3] == "only"  # isolates that single week instead of 1..N cumulative
OUT = f"output/wk{THROUGH_WEEK}{'only' if ONLY_WEEK else ''}" if THROUGH_WEEK else "output"
QTR_LABEL = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4", 5: "OT"}


def main():
    pbp = nfl.import_pbp_data([SEASON], downcast=True)
    ftn = nfl.import_ftn_data([SEASON])
    if THROUGH_WEEK:
        pbp = pbp[pbp["week"] == THROUGH_WEEK] if ONLY_WEEK else pbp[pbp["week"] <= THROUGH_WEEK]
        if "week" in ftn.columns:
            ftn = ftn[ftn["week"] == THROUGH_WEEK] if ONLY_WEEK else ftn[ftn["week"] <= THROUGH_WEEK]
    reg = pbp[pbp["season_type"] == "REG"].copy()
    reg["quarter"] = reg["qtr"].map(QTR_LABEL)
    reg = reg[reg["quarter"].notna()]

    # ---------------- scoring, by quarter ----------------
    scoring_frames = []

    td = reg[reg["touchdown"] == 1][["td_team", "posteam", "defteam", "quarter"]].copy()
    td["scoring_team"] = td["td_team"]
    td["allowing_team"] = td.apply(lambda r: r["defteam"] if r["td_team"] == r["posteam"] else r["posteam"], axis=1)
    td["pts"] = 6
    scoring_frames.append(td[["scoring_team", "allowing_team", "pts", "quarter"]])

    xp = reg[reg["extra_point_result"] == "good"][["posteam", "defteam", "quarter"]].copy()
    xp["scoring_team"], xp["allowing_team"], xp["pts"] = xp["posteam"], xp["defteam"], 1
    scoring_frames.append(xp[["scoring_team", "allowing_team", "pts", "quarter"]])

    twopt = reg[reg["two_point_conv_result"] == "success"][["posteam", "defteam", "quarter"]].copy()
    twopt["scoring_team"], twopt["allowing_team"], twopt["pts"] = twopt["posteam"], twopt["defteam"], 2
    scoring_frames.append(twopt[["scoring_team", "allowing_team", "pts", "quarter"]])

    fg = reg[reg["field_goal_result"] == "made"][["posteam", "defteam", "quarter"]].copy()
    fg["scoring_team"], fg["allowing_team"], fg["pts"] = fg["posteam"], fg["defteam"], 3
    scoring_frames.append(fg[["scoring_team", "allowing_team", "pts", "quarter"]])

    safety = reg[reg["safety"] == 1][["posteam", "defteam", "quarter"]].copy()
    safety["scoring_team"], safety["allowing_team"], safety["pts"] = safety["defteam"], safety["posteam"], 2
    scoring_frames.append(safety[["scoring_team", "allowing_team", "pts", "quarter"]])

    scoring = pd.concat(scoring_frames, ignore_index=True)
    points_scored = scoring.groupby(["scoring_team", "quarter"])["pts"].sum().rename("points_scored")
    points_allowed = scoring.groupby(["allowing_team", "quarter"])["pts"].sum().rename("points_allowed")

    # ---------------- giveaways, by quarter ----------------
    give = reg[(reg["interception"] == 1) | (reg["fumble_lost"] == 1)]
    giveaways = give.groupby(["posteam", "quarter"]).size().rename("giveaways")

    # ---------------- completion %, by quarter (offense thrown, defense allowed) ----------------
    passes = reg[reg["pass_attempt"] == 1]
    comp = passes.groupby(["posteam", "quarter"]).agg(
        completions=("complete_pass", "sum"), attempts=("pass_attempt", "sum")
    )
    comp["completion_pct"] = (comp["completions"] / comp["attempts"] * 100).round(1)

    comp_allowed = passes.groupby(["defteam", "quarter"]).agg(
        completions_allowed=("complete_pass", "sum"), attempts_faced=("pass_attempt", "sum")
    )
    comp_allowed["completion_pct_allowed"] = (comp_allowed["completions_allowed"] / comp_allowed["attempts_faced"] * 100).round(1)

    # ---------------- run/pass split + EPA, by quarter — offense (posteam) and defense-faced (defteam) ----------------
    plays = reg[reg["play_type"].isin(["pass", "run"])]
    tendency = plays.groupby(["posteam", "quarter"]).agg(
        total_plays=("play_id", "count"),
        pass_plays=("play_type", lambda s: (s == "pass").sum()),
        run_plays=("play_type", lambda s: (s == "run").sum()),
        epa_per_play=("epa", "mean"),
    )
    tendency["pass_pct"] = (tendency["pass_plays"] / tendency["total_plays"] * 100).round(1)
    tendency["run_pct"] = (tendency["run_plays"] / tendency["total_plays"] * 100).round(1)
    tendency["epa_per_play"] = tendency["epa_per_play"].round(3)

    def_tendency = plays.groupby(["defteam", "quarter"]).agg(
        total_plays_faced=("play_id", "count"),
        pass_plays_faced=("play_type", lambda s: (s == "pass").sum()),
        run_plays_faced=("play_type", lambda s: (s == "run").sum()),
        def_epa_per_play=("epa", "mean"),
    )
    def_tendency["pass_pct_faced"] = (def_tendency["pass_plays_faced"] / def_tendency["total_plays_faced"] * 100).round(1)
    def_tendency["run_pct_faced"] = (def_tendency["run_plays_faced"] / def_tendency["total_plays_faced"] * 100).round(1)
    def_tendency["def_epa_per_play"] = def_tendency["def_epa_per_play"].round(3)

    # ---------------- defensive scheme (blitz/box), by quarter — same real FTN charting ----------------
    if "nflverse_play_id" in ftn.columns:
        plays_ftn = plays.merge(ftn, left_on="play_id", right_on="nflverse_play_id", how="inner", suffixes=("", "_ftn"))
        rush_charted = plays_ftn[plays_ftn["n_pass_rushers"] > 0] if "n_pass_rushers" in plays_ftn.columns else plays_ftn.iloc[0:0]
        box_charted = plays_ftn[plays_ftn["n_defense_box"] > 0] if "n_defense_box" in plays_ftn.columns else plays_ftn.iloc[0:0]
        scheme = pd.DataFrame(index=pd.MultiIndex.from_product([[], []], names=["defteam", "quarter"]))
        if len(rush_charted):
            blitz = rush_charted.groupby(["defteam", "quarter"]).agg(
                blitz_rate_pct=("n_blitzers", lambda s: round(float((s > 0).mean()) * 100, 1)),
                avg_blitzers=("n_blitzers", lambda s: round(float(s.mean()), 2)),
            )
            scheme = blitz
        if len(box_charted):
            box = box_charted.groupby(["defteam", "quarter"]).agg(
                stacked_box_pct=("n_defense_box", lambda s: round(float((s >= 8).mean()) * 100, 1)),
            )
            scheme = scheme.join(box, how="outer") if len(scheme) else box
    else:
        scheme = pd.DataFrame(columns=["blitz_rate_pct", "avg_blitzers", "stacked_box_pct"])

    # ---------------- assemble long-format table ----------------
    teams = sorted(set(reg["posteam"].dropna()) | set(reg["defteam"].dropna()))
    quarters = ["Q1", "Q2", "Q3", "Q4", "OT"]
    idx = pd.MultiIndex.from_product([teams, quarters], names=["team", "quarter"])
    out = pd.DataFrame(index=idx).reset_index()

    out = out.merge(points_scored.rename_axis(["team", "quarter"]).reset_index(), on=["team", "quarter"], how="left")
    out = out.merge(points_allowed.rename_axis(["team", "quarter"]).reset_index(), on=["team", "quarter"], how="left")
    out = out.merge(giveaways.rename_axis(["team", "quarter"]).reset_index(), on=["team", "quarter"], how="left")
    out = out.merge(comp[["completions", "attempts", "completion_pct"]].rename_axis(["team", "quarter"]).reset_index(), on=["team", "quarter"], how="left")
    out = out.merge(comp_allowed[["completions_allowed", "attempts_faced", "completion_pct_allowed"]].rename_axis(["team", "quarter"]).reset_index(), on=["team", "quarter"], how="left")
    out = out.merge(tendency[["total_plays", "pass_pct", "run_pct", "epa_per_play"]].rename_axis(["team", "quarter"]).reset_index(), on=["team", "quarter"], how="left")
    out = out.merge(def_tendency[["total_plays_faced", "pass_pct_faced", "run_pct_faced", "def_epa_per_play"]].rename_axis(["team", "quarter"]).reset_index(), on=["team", "quarter"], how="left")
    if len(scheme):
        out = out.merge(scheme.rename_axis(["team", "quarter"]).reset_index(), on=["team", "quarter"], how="left")

    # drop all-empty OT rows for teams that never played OT (keeps the file honest, not padded with fake zeros)
    out = out[~((out["quarter"] == "OT") & out["total_plays"].isna())]

    for col in ["points_scored", "points_allowed", "giveaways"]:
        out[col] = out[col].fillna(0).astype(int)

    os.makedirs(OUT, exist_ok=True)
    out.to_csv(f"{OUT}/quarter_splits.csv", index=False)
    print(f"Wrote {OUT}/quarter_splits.csv — {len(teams)} teams x up to 5 quarters ({len(out)} rows)")


if __name__ == "__main__":
    main()
