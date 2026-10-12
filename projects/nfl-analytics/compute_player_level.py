"""
Individual player-level stats — QB and RB computed directly from
play-by-play (nfl_data_py's weekly/seasonal aggregate endpoints 404 for
an in-progress season, so this doesn't depend on them), and a proper
DL / LB / DB position split by joining real roster position data onto
the PFR defensive table.

Honest limitation: individual O-line attribution (who blocked what) is
NOT available in any free data source — that requires paid, per-player
charting (PFF-style). Team-level O-line proxies (already built) are the
real ceiling here without buying that data.

Run with: python compute_player_level.py [season] [through_week]
through_week freezes a snapshot as of that week only and writes into
output/wk<N>/ instead of output/ — see compute_team_stats.py for why.
Writes: output/qb_player_level.csv, output/rb_player_level.csv,
        output/defense_player_level_by_position.csv
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
    if THROUGH_WEEK:
        pbp = pbp[pbp["week"] == THROUGH_WEEK] if ONLY_WEEK else pbp[pbp["week"] <= THROUGH_WEEK]
    reg = pbp[pbp["season_type"] == "REG"]

    # ---------------- QB, computed directly from pbp ----------------
    passes = reg[(reg["play_type"] == "pass") & (reg["passer_player_name"].notna())]
    qb = passes.groupby(["passer_player_name", "posteam"]).agg(
        attempts=("play_id", "count"),
        completions=("complete_pass", "sum"),
        pass_yards=("yards_gained", "sum"),
        pass_tds=("pass_touchdown", "sum"),
        interceptions=("interception", "sum"),
        sacks_taken=("sack", "sum"),
        epa_per_play=("epa", "mean"),
    ).reset_index()
    qb = qb[qb["attempts"] >= 10]  # filter out mop-up/trick-play throws by non-QBs
    qb["completion_pct"] = round(qb["completions"] / qb["attempts"] * 100, 1)
    qb["int_pct"] = round(qb["interceptions"] / qb["attempts"] * 100, 2)
    qb["epa_per_play"] = qb["epa_per_play"].round(3)
    qb = qb.rename(columns={"passer_player_name": "player", "posteam": "team"}).sort_values("epa_per_play", ascending=False)
    os.makedirs(OUT, exist_ok=True)
    qb.to_csv(f"{OUT}/qb_player_level.csv", index=False)
    print(f"Wrote {OUT}/qb_player_level.csv — {len(qb)} QBs (10+ attempts)")

    # ---------------- Real position lookup (shared by RB split + defense split) ----------------
    rosters = nfl.import_seasonal_rosters([SEASON])
    gsis_pos_lookup = rosters[["player_id", "position"]].dropna().drop_duplicates(subset="player_id")
    gsis_pos_lookup = gsis_pos_lookup.rename(columns={"player_id": "rusher_player_id"})

    # ---------------- Real NGS rushing (cutback/lateral-movement proxy) ----------------
    # efficiency = yards actually traveled per rushing yard gained, per NGS's own definition —
    # a real, direct measure of how much a back cuts/dances vs. runs in a straight line.
    ngs_rush = nfl.import_ngs_data("rushing", [SEASON])
    # NGS only ships a cumulative "week 0" row for this metric, no per-game
    # breakdown — always read that row regardless of ONLY_WEEK, since there's
    # no other source for it (it stays season-to-date even in "only" mode).
    if THROUGH_WEEK and not ONLY_WEEK and "week" in ngs_rush.columns:
        ngs_rush = ngs_rush[ngs_rush["week"] <= THROUGH_WEEK]
    ngs_rush_season = ngs_rush[ngs_rush["week"] == 0][
        ["player_gsis_id", "efficiency", "rush_yards_over_expected_per_att", "percent_attempts_gte_eight_defenders"]
    ].rename(columns={"player_gsis_id": "rusher_player_id"})

    # ---------------- RB, computed directly from pbp — REAL RBs/FBs only, QBs split out below ----------------
    runs = reg[(reg["play_type"] == "run") & (reg["rusher_player_name"].notna())]
    runs = runs.merge(gsis_pos_lookup, on="rusher_player_id", how="left")
    rb_runs = runs[runs["position"].isin(["RB", "FB"])]
    qb_runs = runs[runs["position"] == "QB"]

    def rush_summary(df, min_carries):
        out = df.groupby(["rusher_player_name", "posteam", "rusher_player_id"]).agg(
            carries=("play_id", "count"),
            rush_yards=("yards_gained", "sum"),
            rush_tds=("rush_touchdown", "sum"),
        ).reset_index()
        eff4 = df[df["yards_gained"] >= 4].groupby(["rusher_player_name", "posteam", "rusher_player_id"]).size().rename("carries_4plus")
        eff10 = df[df["yards_gained"] >= 10].groupby(["rusher_player_name", "posteam", "rusher_player_id"]).size().rename("carries_10plus")
        out = out.merge(eff4, on=["rusher_player_name", "posteam", "rusher_player_id"], how="left") \
                 .merge(eff10, on=["rusher_player_name", "posteam", "rusher_player_id"], how="left")
        out[["carries_4plus", "carries_10plus"]] = out[["carries_4plus", "carries_10plus"]].fillna(0)
        out = out[out["carries"] >= min_carries]
        out["ypc"] = round(out["rush_yards"] / out["carries"], 2)
        out["pct_carries_4plus"] = round(out["carries_4plus"] / out["carries"] * 100, 1)
        out["explosive_rate_10plus"] = round(out["carries_10plus"] / out["carries"] * 100, 1)
        return out.rename(columns={"rusher_player_name": "player", "posteam": "team"})

    rb = rush_summary(rb_runs, min_carries=5)
    rb = rb.merge(ngs_rush_season, on="rusher_player_id", how="left").drop(columns=["rusher_player_id"])
    rb = rb.rename(columns={"percent_attempts_gte_eight_defenders": "pct_carries_vs_stacked_box"}) \
           .sort_values("pct_carries_4plus", ascending=False)
    rb.to_csv(f"{OUT}/rb_player_level.csv", index=False)
    print(f"Wrote {OUT}/rb_player_level.csv — {len(rb)} RBs/FBs (5+ carries, QBs excluded)")

    qb_rush = rush_summary(qb_runs, min_carries=3)
    qb_rush = qb_rush.drop(columns=["rusher_player_id"])
    qb_rush.to_csv(f"{OUT}/qb_rush_player_level.csv", index=False)
    print(f"Wrote {OUT}/qb_rush_player_level.csv — {len(qb_rush)} QBs (3+ designed/scramble carries)")

    # ---------------- Defense, position-split via roster join ----------------
    pfr_def = nfl.import_weekly_pfr("def", [SEASON])
    if THROUGH_WEEK and "week" in pfr_def.columns:
        pfr_def = pfr_def[pfr_def["week"] == THROUGH_WEEK] if ONLY_WEEK else pfr_def[pfr_def["week"] <= THROUGH_WEEK]
    pos_lookup = rosters[["pfr_id", "position"]].dropna().drop_duplicates(subset="pfr_id")

    def_pos = pfr_def.merge(pos_lookup, left_on="pfr_player_id", right_on="pfr_id", how="left")
    agg = def_pos.groupby(["pfr_player_name", "team", "position"]).agg(
        targets=("def_targets", "sum"),
        completions_allowed=("def_completions_allowed", "sum"),
        yards_allowed=("def_yards_allowed", "sum"),
        interceptions=("def_ints", "sum"),
        pressures=("def_pressures", "sum"),
        sacks=("def_sacks", "sum"),
        tackles_combined=("def_tackles_combined", "sum"),
        missed_tackles=("def_missed_tackles", "sum"),
    ).reset_index()
    agg["completion_pct_allowed"] = (agg["completions_allowed"] / agg["targets"] * 100).round(1)
    agg["yards_per_target"] = (agg["yards_allowed"] / agg["targets"]).round(2)
    agg["missed_tackle_pct"] = (agg["missed_tackles"] / agg["tackles_combined"] * 100).round(1)

    def group_position(p):
        if pd.isna(p):
            return "Unknown"
        if p in ("DE", "DT", "NT"):
            return "DL"
        if p == "LB":
            return "LB"
        if p in ("CB", "S", "FS", "SS", "DB"):
            return "DB"
        return p

    agg["position_group"] = agg["position"].apply(group_position)
    agg = agg.rename(columns={"pfr_player_name": "player"}).sort_values(["position_group", "pressures"], ascending=[True, False])
    agg.to_csv(f"{OUT}/defense_player_level_by_position.csv", index=False)
    print(f"Wrote {OUT}/defense_player_level_by_position.csv — {len(agg)} defenders")
    print(agg["position_group"].value_counts())

    # team-level missed tackle %, split by position group (the locked grill decision)
    team_split = agg[agg["tackles_combined"] > 0].groupby(["team", "position_group"]).agg(
        missed_tackles=("missed_tackles", "sum"),
        tackles_combined=("tackles_combined", "sum"),
    ).reset_index()
    team_split["missed_tackle_pct"] = (team_split["missed_tackles"] / team_split["tackles_combined"] * 100).round(1)
    team_split = team_split[team_split["position_group"].isin(["LB", "DB"])]
    team_split.to_csv(f"{OUT}/team_missed_tackle_by_position_group.csv", index=False)

    # ---------------- Passes defended / PBU — no PFR source for this, built
    # straight from raw play-by-play's own charting (pass_defense_1/2 fields),
    # joined to real roster position data the same way as the tackle split above.
    pass_plays = reg[reg["play_type"] == "pass"]
    pbu_parts = []
    for i in (1, 2):
        col_id, col_name = f"pass_defense_{i}_player_id", f"pass_defense_{i}_player_name"
        part = pass_plays[pass_plays[col_name].notna()][[col_id, col_name, "defteam", "interception"]].rename(
            columns={col_id: "player_id", col_name: "player_name", "defteam": "team"}
        )
        pbu_parts.append(part)
    pbu_plays = pd.concat(pbu_parts, ignore_index=True)

    pos_lookup_gsis = rosters[["player_id", "position"]].dropna().drop_duplicates(subset="player_id")
    pbu_plays = pbu_plays.merge(pos_lookup_gsis, on="player_id", how="left")

    pbu = pbu_plays.groupby(["player_id", "player_name", "team", "position"]).agg(
        pbu=("interception", lambda s: int((s == 0).sum())),  # incompletions only — INTs tracked separately, not double-counted
        passes_defended=("interception", "count"),  # official convention: PBU + the INTs where the same player also gets PD credit
    ).reset_index()
    pbu["position_group"] = pbu["position"].apply(group_position)
    pbu = pbu.sort_values("pbu", ascending=False)
    pbu.to_csv(f"{OUT}/defense_pbu_player_level.csv", index=False)
    print(f"Wrote {OUT}/defense_pbu_player_level.csv — {len(pbu)} defenders")

    team_pbu = pbu[pbu["position_group"].isin(["LB", "DB"])].groupby(["team", "position_group"]).agg(
        pbu=("pbu", "sum"),
        passes_defended=("passes_defended", "sum"),
    ).reset_index()
    team_pbu.to_csv(f"{OUT}/team_pbu_by_position_group.csv", index=False)
    print(f"Wrote {OUT}/team_pbu_by_position_group.csv — {len(team_pbu)} rows (LB vs DB split, per team)")

    # ---------------- Forced fumbles & defensive fumble recoveries — also not
    # in the PFR table, built the same way from raw pbp's own credited players.
    # Recoveries only count when the RECOVERING team is the defense (defteam) —
    # a defense recovering its own... wait, an offense recovering its own fumble
    # keeps possession, that's not a defensive stat; only defteam == recovery
    # team is a real takeaway credited to that player.
    ff_parts = []
    for i in (1, 2):
        col_id, col_name, col_team = (f"forced_fumble_player_{i}_player_id",
                                       f"forced_fumble_player_{i}_player_name",
                                       f"forced_fumble_player_{i}_team")
        part = reg[reg[col_name].notna()][[col_id, col_name, col_team]].rename(
            columns={col_id: "player_id", col_name: "player_name", col_team: "team"}
        )
        ff_parts.append(part)
    forced_fumbles = pd.concat(ff_parts, ignore_index=True).groupby(
        ["player_id", "player_name", "team"]
    ).size().reset_index(name="forced_fumbles")

    rec_parts = []
    for i in (1, 2):
        col_id, col_name, col_team = (f"fumble_recovery_{i}_player_id",
                                       f"fumble_recovery_{i}_player_name",
                                       f"fumble_recovery_{i}_team")
        part = reg[(reg[col_name].notna()) & (reg[col_team] == reg["defteam"])][[col_id, col_name, col_team]].rename(
            columns={col_id: "player_id", col_name: "player_name", col_team: "team"}
        )
        rec_parts.append(part)
    fumble_recoveries = pd.concat(rec_parts, ignore_index=True).groupby(
        ["player_id", "player_name", "team"]
    ).size().reset_index(name="fumble_recoveries")

    hustle = pbu[["player_id", "player_name", "team", "pbu", "passes_defended"]].merge(
        forced_fumbles, on=["player_id", "player_name", "team"], how="outer"
    ).merge(fumble_recoveries, on=["player_id", "player_name", "team"], how="outer")
    for col in ["pbu", "passes_defended", "forced_fumbles", "fumble_recoveries"]:
        hustle[col] = hustle[col].fillna(0).astype(int)
    hustle = hustle.merge(pos_lookup_gsis, on="player_id", how="left")
    hustle["position_group"] = hustle["position"].apply(group_position)
    hustle = hustle.sort_values(["forced_fumbles", "fumble_recoveries", "pbu"], ascending=False)
    hustle.to_csv(f"{OUT}/defense_hustle_stats_player_level.csv", index=False)
    print(f"Wrote {OUT}/defense_hustle_stats_player_level.csv — {len(hustle)} defenders (PBU, forced fumbles, fumble recoveries)")

    team_hustle = hustle[hustle["position_group"].isin(["LB", "DB"])].groupby(["team", "position_group"]).agg(
        pbu=("pbu", "sum"),
        passes_defended=("passes_defended", "sum"),
        forced_fumbles=("forced_fumbles", "sum"),
        fumble_recoveries=("fumble_recoveries", "sum"),
    ).reset_index()
    team_hustle.to_csv(f"{OUT}/team_hustle_stats_by_position_group.csv", index=False)
    print(f"Wrote {OUT}/team_hustle_stats_by_position_group.csv — {len(team_hustle)} rows (LB vs DB split, per team)")
    print(f"Wrote {OUT}/team_missed_tackle_by_position_group.csv — {len(team_split)} rows (LB vs DB split, per team)")


if __name__ == "__main__":
    main()
