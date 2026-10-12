"""
NFL Team Diagnostic — full metrics catalog computation.

Pulls every real data source confirmed available (nflfastR play-by-play,
NGS passing/receiving, PFR defensive advanced stats, FTN charting data,
snap counts, schedules) and computes team-level tables covering every
family in METRICS_CATALOG.md, plus the two added metrics: tackle
accuracy (missed-tackle %) and penalty discipline.

This is a data dump for review, not the final report — you look at these
numbers yourself first, then we decide what goes into the built report.

Run with: python compute_full_catalog.py [season] [through_week]
through_week freezes a snapshot as of that week only and writes into
output/wk<N>/ instead of output/ — see compute_team_stats.py for why.
Writes CSVs into ./output/ (or ./output/wk<N>/)
"""
import sys
import os
import numpy as np
import pandas as pd
import nfl_data_py as nfl

SEASON = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
THROUGH_WEEK = int(sys.argv[2]) if len(sys.argv) > 2 else None
ONLY_WEEK = len(sys.argv) > 3 and sys.argv[3] == "only"  # isolates that single week instead of 1..N cumulative
OUT = f"output/wk{THROUGH_WEEK}{'only' if ONLY_WEEK else ''}" if THROUGH_WEEK else "output"


def w(df, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    df.to_csv(path, index=False)
    print(f"  wrote {path}  ({len(df)} rows)")


def main():
    print(f"Pulling all data sources for {SEASON} ...")
    sched = nfl.import_schedules([SEASON])
    pbp = nfl.import_pbp_data([SEASON], downcast=True)
    ngs_pass = nfl.import_ngs_data("passing", [SEASON])
    ngs_rec = nfl.import_ngs_data("receiving", [SEASON])
    pfr_def = nfl.import_weekly_pfr("def", [SEASON])
    ftn = nfl.import_ftn_data([SEASON])
    snaps = nfl.import_snap_counts([SEASON])

    def capped(df):
        if not THROUGH_WEEK or "week" not in df.columns:
            return df
        return df[df["week"] == THROUGH_WEEK] if ONLY_WEEK else df[df["week"] <= THROUGH_WEEK]

    sched, pbp, ngs_pass, ngs_rec = capped(sched), capped(pbp), capped(ngs_pass), capped(ngs_rec)
    pfr_def, ftn, snaps = capped(pfr_def), capped(ftn), capped(snaps)
    if THROUGH_WEEK:
        op = "==" if ONLY_WEEK else "<="
        print(f"Snapshot mode: filtered every source to week {op} {THROUGH_WEEK}")

    played = sched.dropna(subset=["home_score"])
    max_week = int(played["week"].max())
    teams = sorted(set(sched["home_team"]).union(sched["away_team"]))
    reg = pbp[(pbp["play_type"].isin(["pass", "run"])) & (pbp["season_type"] == "REG")]

    print(f"Through week {max_week}, {len(played)} games played.\n")

    # ---------------------------------------------------------------
    # TEAM LEVEL (extends the existing compute_team_stats.py output
    # with the two new metrics: penalties/discipline + team tackle accuracy)
    # ---------------------------------------------------------------
    team_rows = []
    pen = pbp[(pbp["penalty"] == 1) & (pbp["season_type"] == "REG")]
    for team in teams:
        team_pens = pen[pen["penalty_team"] == team]
        n_games = len(played[(played["home_team"] == team) | (played["away_team"] == team)])
        pens_per_game = round(len(team_pens) / n_games, 2) if n_games else None
        pen_yards_per_game = round(float(team_pens["penalty_yards"].sum()) / n_games, 1) if n_games else None

        team_def = pfr_def[pfr_def["team"] == team]
        missed_tkl_pct_team = round(float(team_def["def_missed_tackles"].sum()) /
                                     float(team_def["def_tackles_combined"].sum()) * 100, 1) \
            if team_def["def_tackles_combined"].sum() else None

        team_rows.append({
            "team": team,
            "games": n_games,
            "penalties_per_game": pens_per_game,
            "penalty_yards_per_game": pen_yards_per_game,
            "team_missed_tackle_pct": missed_tkl_pct_team,
            "team_missed_tackles": int(team_def["def_missed_tackles"].sum()),
            "team_tackles_combined": int(team_def["def_tackles_combined"].sum()),
        })
    w(pd.DataFrame(team_rows).sort_values("penalty_yards_per_game", ascending=False), "team_discipline_and_tackling.csv")

    # ---------------------------------------------------------------
    # QB
    # ---------------------------------------------------------------
    qb_rows = []
    for team in teams:
        off = reg[reg["posteam"] == team]
        pass_plays = off[off["play_type"] == "pass"]
        rush_by_qb = off[(off["play_type"] == "run") & (off["rusher_player_name"].notna()) & (off["qb_scramble"] == 1)]
        n_dropbacks = len(pass_plays) + len(off[off["qb_scramble"] == 1])
        ints = int(pass_plays["interception"].sum())
        team_ngs_pass = ngs_pass[(ngs_pass["team_abbr"] == team) & (ngs_pass["week"] <= max_week)]
        qb_rows.append({
            "team": team,
            "pass_attempts": int(pass_plays["pass_attempt"].sum()) if "pass_attempt" in pass_plays.columns else len(pass_plays),
            "pass_yards": round(float(pass_plays["yards_gained"].sum()), 0),
            "rush_yards_qb_scramble": round(float(off[off["qb_scramble"] == 1]["yards_gained"].sum()), 0),
            "scramble_pct": round(len(off[off["qb_scramble"] == 1]) / n_dropbacks * 100, 1) if n_dropbacks else None,
            "int_pct": round(ints / len(pass_plays) * 100, 2) if len(pass_plays) else None,
            "epa_per_dropback": round(float(off[off["qb_dropback"] == 1]["epa"].mean()), 3) if "qb_dropback" in off.columns and len(off[off["qb_dropback"] == 1]) else None,
            "avg_time_to_throw": round(float(team_ngs_pass["avg_time_to_throw"].mean()), 2) if len(team_ngs_pass) else None,
            "cpoe": round(float(team_ngs_pass["completion_percentage_above_expectation"].mean()), 2) if len(team_ngs_pass) else None,
            "avg_intended_air_yards": round(float(team_ngs_pass["avg_intended_air_yards"].mean()), 2) if len(team_ngs_pass) else None,
            "sacks_allowed": int(off["sack"].sum()),
            "sack_rate": round(float(off["sack"].sum()) / n_dropbacks * 100, 2) if n_dropbacks else None,
        })
    w(pd.DataFrame(qb_rows).sort_values("epa_per_dropback", ascending=False), "qb_stats.csv")

    # ---------------------------------------------------------------
    # OL / DL (team-level proxies + FTN sack-fault split)
    # ---------------------------------------------------------------
    oldl_rows = []
    for team in teams:
        off = reg[reg["posteam"] == team]
        deff = reg[reg["defteam"] == team]
        off_sacks = off[off["sack"] == 1]
        off_sack_ftn = off_sacks.merge(
            ftn, left_on=["game_id", "play_id"], right_on=["nflverse_game_id", "nflverse_play_id"], how="left"
        ) if "nflverse_play_id" in ftn.columns else off_sacks
        qb_fault_sacks = int(off_sack_ftn["is_qb_fault_sack"].sum()) if "is_qb_fault_sack" in off_sack_ftn.columns else None
        oldl_rows.append({
            "team": team,
            "sacks_allowed_by_OL": int(off["sack"].sum()),
            "qb_fault_sacks": qb_fault_sacks,
            "ol_fault_sacks": (int(off["sack"].sum()) - qb_fault_sacks) if qb_fault_sacks is not None else None,
            "qb_hits_allowed": int(off["qb_hit"].sum()) if "qb_hit" in off.columns else None,
            "penalties_off_line": int(pen[(pen["penalty_team"] == team) & (pen["penalty_type"].isin(["Holding", "False Start"]))].shape[0]) if "penalty_type" in pen.columns else None,
            "run_yards_per_carry_off": round(float(off[off["play_type"] == "run"]["yards_gained"].mean()), 2) if len(off[off["play_type"] == "run"]) else None,
            "sacks_generated_by_DL": int(deff["sack"].sum()),
            "qb_hits_generated": int(deff["qb_hit"].sum()) if "qb_hit" in deff.columns else None,
            "run_yards_per_carry_allowed": round(float(deff[deff["play_type"] == "run"]["yards_gained"].mean()), 2) if len(deff[deff["play_type"] == "run"]) else None,
        })
    w(pd.DataFrame(oldl_rows), "ol_dl_stats.csv")

    # ---------------------------------------------------------------
    # RB
    # ---------------------------------------------------------------
    rb_rows = []
    runs = reg[reg["play_type"] == "run"]
    for team in teams:
        team_runs = runs[runs["posteam"] == team]
        if not len(team_runs):
            continue
        efficient = team_runs[team_runs["yards_gained"] >= 4]
        explosive = team_runs[team_runs["yards_gained"] >= 10]
        rb_rows.append({
            "team": team,
            "carries": len(team_runs),
            "yards_per_carry": round(float(team_runs["yards_gained"].mean()), 2),
            "pct_carries_4plus_yards": round(len(efficient) / len(team_runs) * 100, 1),
            "explosive_run_rate_10plus": round(len(explosive) / len(team_runs) * 100, 1),
            "rb_receiving_targets": int(reg[(reg["posteam"] == team) & (reg["play_type"] == "pass") & (reg["receiver_player_name"].notna())].shape[0]),
        })
    w(pd.DataFrame(rb_rows).sort_values("yards_per_carry", ascending=False), "rb_stats.csv")

    # ---------------------------------------------------------------
    # WR / TE (NGS receiving). NGS ships a "week 0" row meant to be the
    # season-to-date total, but it's missing for a real chunk of players
    # (confirmed: ~15% of them) — rather than trust an inconsistent field,
    # this computes ONE real season row per player directly from the
    # per-week rows (sum counts, weight rate stats by real volume), which
    # both fills the gap and avoids charting the same player 2-4 times at
    # different single-week numbers, which is what "All metrics" and the
    # WR/TE tab were doing before this fix.
    # ---------------------------------------------------------------
    def aggregate_ngs_receiving(df):
        per_week = df[df["week"] > 0]
        if not len(per_week):
            return pd.DataFrame()

        def wavg(g, col, weight_col):
            wsum = g[weight_col].sum()
            return round(float((g[col] * g[weight_col]).sum() / wsum), 2) if wsum else None

        rows = []
        for (gsis_id, name), g in per_week.groupby(["player_gsis_id", "player_display_name"]):
            targets = int(g["targets"].sum())
            receptions = int(g["receptions"].sum())
            rows.append({
                "player_gsis_id": gsis_id, "player_display_name": name,
                "team_abbr": g["team_abbr"].mode().iat[0],
                "player_position": g["player_position"].mode().iat[0] if g["player_position"].notna().any() else None,
                "targets": targets, "receptions": receptions,
                "yards": float(g["yards"].sum()), "rec_touchdowns": int(g["rec_touchdowns"].sum()),
                "catch_percentage": round(receptions / targets * 100, 1) if targets else None,
                "avg_cushion": wavg(g, "avg_cushion", "targets"),
                "avg_separation": wavg(g, "avg_separation", "targets"),
                "avg_intended_air_yards": wavg(g, "avg_intended_air_yards", "targets"),
                "percent_share_of_intended_air_yards": wavg(g, "percent_share_of_intended_air_yards", "targets"),
                "avg_yac": wavg(g, "avg_yac", "receptions"),
                "avg_expected_yac": wavg(g, "avg_expected_yac", "receptions"),
                "avg_yac_above_expectation": wavg(g, "avg_yac_above_expectation", "receptions"),
            })
        return pd.DataFrame(rows)

    ngs_rec_season = aggregate_ngs_receiving(ngs_rec[ngs_rec["week"] <= max_week].copy())

    # NGS's per-week rows have real gaps for a chunk of players (e.g. a whole
    # week missing), which silently undercounts anyone summed from them.
    # Worse, in an isolated single-week snapshot NGS can be missing a player
    # ENTIRELY if that player's game hasn't been NGS-processed yet (confirmed:
    # Next Gen Stats can lag a day or more behind raw play-by-play for recent
    # games) — a plain override-in-place misses that case, since there's no
    # existing row to override. Raw play-by-play has no such gap, so every
    # receiver who ran a real route gets a row here regardless of whether NGS
    # has caught up: volume counts (targets/receptions/yards/TDs) always come
    # from pbp; NGS-exclusive tracking metrics (separation, cushion, YAC above
    # expectation) stay as NGS reports them, and are simply null for players
    # whose game NGS hasn't processed yet — not fabricated, not dropped.
    pbp_pass_reg = pbp[(pbp["play_type"] == "pass") & (pbp["season_type"] == "REG") & (pbp["receiver_player_name"].notna())]
    pbp_pass_reg = pbp_pass_reg[pbp_pass_reg["week"] <= max_week]
    pbp_pass_reg = pbp_pass_reg.assign(
        is_rec_td=(pbp_pass_reg["pass_touchdown"] == 1) & (pbp_pass_reg["td_player_id"] == pbp_pass_reg["receiver_player_id"])
    )
    rec_truth = pbp_pass_reg.groupby("receiver_player_id").agg(
        player_display_name_pbp=("receiver_player_name", "first"),
        team_abbr_pbp=("posteam", "first"),
        targets_pbp=("play_id", "count"),
        receptions_pbp=("complete_pass", "sum"),
        yards_pbp=("receiving_yards", "sum"),
        rec_touchdowns_pbp=("is_rec_td", "sum"),
    ).reset_index()

    ngs_rec_season = ngs_rec_season.merge(
        rec_truth, left_on="player_gsis_id", right_on="receiver_player_id", how="outer"
    )
    # Fill identity fields for players pbp has but NGS doesn't have yet.
    missing_ngs = ngs_rec_season["player_gsis_id"].isna()
    ngs_rec_season.loc[missing_ngs, "player_gsis_id"] = ngs_rec_season.loc[missing_ngs, "receiver_player_id"]
    ngs_rec_season.loc[missing_ngs, "player_display_name"] = ngs_rec_season.loc[missing_ngs, "player_display_name_pbp"]
    ngs_rec_season.loc[missing_ngs, "team_abbr"] = ngs_rec_season.loc[missing_ngs, "team_abbr_pbp"]
    if missing_ngs.any():
        try:
            roster_pos = nfl.import_seasonal_rosters([SEASON])[["player_id", "position"]].drop_duplicates("player_id")
            pos_by_id = dict(zip(roster_pos["player_id"], roster_pos["position"]))
            ngs_rec_season.loc[missing_ngs, "player_position"] = ngs_rec_season.loc[missing_ngs, "player_gsis_id"].map(pos_by_id)
        except Exception:
            pass  # position stays null for these rows if the roster pull fails — not fatal

    for col, truth_col, as_int in [
        ("targets", "targets_pbp", True), ("receptions", "receptions_pbp", True),
        ("yards", "yards_pbp", False), ("rec_touchdowns", "rec_touchdowns_pbp", True),
    ]:
        has_truth = ngs_rec_season[truth_col].notna()
        ngs_rec_season.loc[has_truth, col] = ngs_rec_season.loc[has_truth, truth_col]
        if as_int:
            ngs_rec_season[col] = ngs_rec_season[col].fillna(0).astype(int)
    ngs_rec_season["catch_percentage"] = (ngs_rec_season["receptions"] / ngs_rec_season["targets"] * 100).round(1)
    ngs_rec_season = ngs_rec_season.drop(columns=[
        "receiver_player_id", "targets_pbp", "receptions_pbp", "yards_pbp", "rec_touchdowns_pbp",
        "player_display_name_pbp", "team_abbr_pbp",
    ])
    ngs_rec_season = ngs_rec_season[ngs_rec_season["targets"] > 0]  # drop any zero-target artifact rows

    added_from_pbp = int(missing_ngs.sum())
    if added_from_pbp:
        print(f"  (+{added_from_pbp} receivers added from raw play-by-play — NGS hadn't published their game yet)")
    w(ngs_rec_season.sort_values(["team_abbr", "targets"], ascending=[True, False]),
      "wr_te_player_level_ngs.csv")

    ftn_drops = ftn[ftn["is_drop"] == 1] if "is_drop" in ftn.columns else pd.DataFrame()
    wr_team_rows = []
    for team in teams:
        team_ngs = ngs_rec_season[ngs_rec_season["team_abbr"] == team]
        total_targets = int(team_ngs["targets"].sum()) if len(team_ngs) else 0
        wr_team_rows.append({
            "team": team,
            "avg_separation": round(float((team_ngs["avg_separation"] * team_ngs["targets"]).sum() / total_targets), 2) if total_targets else None,
            "avg_yac_above_expected": round(float((team_ngs["avg_yac_above_expectation"] * team_ngs["receptions"]).sum() / team_ngs["receptions"].sum()), 2) if len(team_ngs) and team_ngs["receptions"].sum() else None,
            "total_targets": total_targets or None,
            "team_catch_pct": round(float(team_ngs["receptions"].sum()) / total_targets * 100, 1) if total_targets else None,
        })
    w(pd.DataFrame(wr_team_rows), "wr_te_team_level.csv")

    # ---------------------------------------------------------------
    # LB / DB (from PFR defensive weekly data — already per player)
    # ---------------------------------------------------------------
    w(pfr_def.sort_values(["team", "def_targets"], ascending=[True, False]), "lb_db_player_level_pfr.csv")

    # PFR's weekly defensive charting has confirmed gaps for very recent games/
    # less-prominent players (e.g. a whole game's worth of picks missing days
    # after it aired) — raw play-by-play never has that lag, so interceptions
    # come from there instead of summing PFR's def_ints.
    raw_ints_by_team = reg[reg["interception"] == 1].groupby("defteam").size()

    # Same lag pattern as NGS above: a team with no PFR row yet for this
    # snapshot used to be skipped from this file entirely, even though
    # completion%/yards-allowed are both directly computable from raw pbp.
    # Only pressures_generated and missed_tackle_pct have no pbp equivalent
    # (nothing in nflfastR charts "pressure" or "missed tackle") — those stay
    # null for a team until PFR actually publishes that game, instead of being
    # guessed at.
    pbp_pass_def = reg[reg["play_type"] == "pass"]
    db_team_rows = []
    added_from_pbp_def = 0
    for team in teams:
        team_def = pfr_def[pfr_def["team"] == team]
        if len(team_def):
            db_team_rows.append({
                "team": team,
                "completion_pct_allowed": round(float(team_def["def_completions_allowed"].sum()) / float(team_def["def_targets"].sum()) * 100, 1) if team_def["def_targets"].sum() else None,
                "yards_allowed_per_target": round(float(team_def["def_yards_allowed"].sum()) / float(team_def["def_targets"].sum()), 2) if team_def["def_targets"].sum() else None,
                "interceptions": int(raw_ints_by_team.get(team, 0)),
                "pressures_generated": int(team_def["def_pressures"].sum()),
                "missed_tackle_pct": round(float(team_def["def_missed_tackles"].sum()) / float(team_def["def_tackles_combined"].sum()) * 100, 1) if team_def["def_tackles_combined"].sum() else None,
            })
            continue
        faced = pbp_pass_def[pbp_pass_def["defteam"] == team]
        if not len(faced):
            continue  # team genuinely hasn't played in this snapshot yet
        targets_faced = int(faced["pass_attempt"].sum())
        comps_allowed = int(faced["complete_pass"].sum())
        db_team_rows.append({
            "team": team,
            "completion_pct_allowed": round(comps_allowed / targets_faced * 100, 1) if targets_faced else None,
            "yards_allowed_per_target": round(float(faced["receiving_yards"].sum()) / targets_faced, 2) if targets_faced else None,
            "interceptions": int(raw_ints_by_team.get(team, 0)),
            "pressures_generated": None,  # no raw-pbp equivalent — fills in once PFR publishes this game
            "missed_tackle_pct": None,    # same — tackle charting only exists in PFR's weekly data
        })
        added_from_pbp_def += 1
    if added_from_pbp_def:
        print(f"  (+{added_from_pbp_def} teams added from raw play-by-play — PFR hadn't published their game "
              f"yet; pressures/missed-tackle% stay blank for those until it does)")
    db_team_df = pd.DataFrame(db_team_rows)
    if len(db_team_df):
        db_team_df = db_team_df.sort_values("completion_pct_allowed")
    w(db_team_df, "lb_db_team_level.csv")

    # ---------------------------------------------------------------
    # Play-type tendency (FTN charting: play-action, RPO, screens, motion, blitz)
    # ---------------------------------------------------------------
    if "nflverse_play_id" in ftn.columns:
        reg_ftn = reg.merge(
            ftn,
            left_on=["game_id", "play_id"],
            right_on=["nflverse_game_id", "nflverse_play_id"],
            how="inner",
            suffixes=("", "_ftn"),
        )
        tendency_rows = []
        for team in teams:
            t = reg_ftn[reg_ftn["posteam"] == team]
            # Run/pass split comes from the full play-by-play, not the FTN-charted
            # subset above — FTN charting can lag behind raw pbp (same gap seen
            # elsewhere), and a plain run-vs-pass count doesn't need FTN at all.
            off_all = reg[reg["posteam"] == team]
            run_plays = int((off_all["play_type"] == "run").sum())
            pass_plays = int((off_all["play_type"] == "pass").sum())
            total_plays = run_plays + pass_plays
            if not len(t) and not total_plays:
                continue
            tendency_rows.append({
                "team": team,
                "run_plays": run_plays,
                "pass_plays": pass_plays,
                "run_pct": round(run_plays / total_plays * 100, 1) if total_plays else None,
                "pass_pct": round(pass_plays / total_plays * 100, 1) if total_plays else None,
                "plays_charted": len(t),
                "play_action_pct": round(float(t["is_play_action"].mean()) * 100, 1) if len(t) else None,
                "rpo_pct": round(float(t["is_rpo"].mean()) * 100, 1) if len(t) else None,
                "screen_pct": round(float(t["is_screen_pass"].mean()) * 100, 1) if len(t) else None,
                "no_huddle_pct": round(float(t["is_no_huddle"].mean()) * 100, 1) if len(t) else None,
                "motion_pct": round(float(t["is_motion"].mean()) * 100, 1) if len(t) else None,
                "drop_rate_offense": round(float(t["is_drop"].mean()) * 100, 1) if len(t) and "is_drop" in t.columns else None,
            })
        w(pd.DataFrame(tendency_rows), "play_type_tendency.csv")

        # Defense identity: the same tags, grouped by the team ON DEFENSE instead
        # of on offense — what kind of plays does this defense typically FACE,
        # PLUS this defense's own real scheme signals from the same FTN charting:
        # blitz rate (n_blitzers), total rushers sent, and box count (run-defense
        # loading). Man/zone coverage shell is the one honest gap — that's not
        # in FTN or NGS, only paid PFF-style charting has it.
        def_tendency_rows = []
        for team in teams:
            t = reg_ftn[reg_ftn["defteam"] == team]
            if not len(t):
                continue
            # n_pass_rushers/n_blitzers are 0 both for "genuinely zero" AND for
            # "not charted this play" (mostly run plays, where pass-rush charting
            # doesn't apply) — FTN gives no way to tell those apart except that a
            # real dropback always has at least a few rushers, so >0 is the real
            # "this was actually charted" filter. Same logic for box count.
            rush_charted = t[t["n_pass_rushers"] > 0] if "n_pass_rushers" in t.columns else t.iloc[0:0]
            box_charted = t[t["n_defense_box"] > 0] if "n_defense_box" in t.columns else t.iloc[0:0]

            # D-line-alone vs. blitz-assisted pressure: same rush-charted plays,
            # split by whether this specific play sent extra rushers (n_blitzers>0)
            # or not, then checking the real pbp qb_hit/sack outcome on that play.
            natural_rush = rush_charted[rush_charted["n_blitzers"] == 0] if len(rush_charted) else rush_charted
            blitz_rush = rush_charted[rush_charted["n_blitzers"] > 0] if len(rush_charted) else rush_charted
            pressure_rate_natural = round(float(((natural_rush["qb_hit"] == 1) | (natural_rush["sack"] == 1)).mean()) * 100, 1) if len(natural_rush) else None
            pressure_rate_blitz = round(float(((blitz_rush["qb_hit"] == 1) | (blitz_rush["sack"] == 1)).mean()) * 100, 1) if len(blitz_rush) else None

            def_tendency_rows.append({
                "team": team,
                "plays_faced": len(t),
                "play_action_faced_pct": round(float(t["is_play_action"].mean()) * 100, 1),
                "rpo_faced_pct": round(float(t["is_rpo"].mean()) * 100, 1),
                "screen_faced_pct": round(float(t["is_screen_pass"].mean()) * 100, 1),
                "no_huddle_faced_pct": round(float(t["is_no_huddle"].mean()) * 100, 1),
                "motion_faced_pct": round(float(t["is_motion"].mean()) * 100, 1),
                "drop_faced_pct": round(float(t["is_drop"].mean()) * 100, 1) if "is_drop" in t.columns else None,
                "blitz_rate_pct": round(float((rush_charted["n_blitzers"] > 0).mean()) * 100, 1) if len(rush_charted) else None,
                "avg_blitzers": round(float(rush_charted["n_blitzers"].mean()), 2) if len(rush_charted) else None,
                "avg_pass_rushers": round(float(rush_charted["n_pass_rushers"].mean()), 2) if len(rush_charted) else None,
                "stacked_box_pct": round(float((box_charted["n_defense_box"] >= 8).mean()) * 100, 1) if len(box_charted) else None,
                "avg_box_defenders": round(float(box_charted["n_defense_box"].mean()), 2) if len(box_charted) else None,
                "pressure_rate_natural_rush": pressure_rate_natural,
                "pressure_rate_blitz": pressure_rate_blitz,
            })
        w(pd.DataFrame(def_tendency_rows), "defense_tendency_faced.csv")
    else:
        print("  FTN play-id join key not found — skipping play-type tendency file, needs a closer look.")

    print(f"\nDone. All files in ./{OUT}/ — through week {max_week} of {SEASON}.")


if __name__ == "__main__":
    main()
