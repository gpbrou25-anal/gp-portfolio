"""
NFL Diagnostic — insight dashboard.

Curated charts per position family, colored with each team's real
primary color (collisions between teams with identical/near-identical
colors resolved with a distinct marker shape, not a fake color), plus
an "All metrics" tab that tables + charts + explains the relevance of
literally every computed metric, raw, before any editorializing.

Run with: streamlit run viewer_app.py
"""
import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from metric_glossary import METRIC_META, RELEVANCE_BY_KEY, FAMILIES

st.set_page_config(page_title="NFL Diagnostic", layout="wide")

BASE = os.path.dirname(__file__)

with st.sidebar:
    st.markdown("### Data snapshot")
    SNAPSHOT = st.radio(
        "Which data?",
        ["Latest (cumulative)", "Frozen at Week 2 (cumulative)", "Frozen at Week 3 (cumulative)",
         "Frozen at Week 4 (cumulative, complete — all 32 teams at 4 games)",
         "Frozen at Week 5 (cumulative, partial — MNF not yet played)",
         "Week 3 only (isolated)", "Week 4 only (isolated, complete — 16/16 games)",
         "Week 5 only (isolated, partial — MNF not yet played)"],
        index=0,
        help="Latest = every game played so far, summed together. Frozen at Week 2/3/4/5 = cumulative "
             "through that week only, all 32 teams at the same number of games — the fair basis for "
             "team-to-team comparisons. Week 3/4/5 only = that single week in isolation, not added to "
             "the rest of the season. Every tab uses whichever you pick.",
    )
    if SNAPSHOT != "Latest (cumulative)":
        st.caption(f"Showing: {SNAPSHOT}")

if SNAPSHOT == "Latest (cumulative)":
    OUT = os.path.join(BASE, "output")
    TEAM_STATS_DIR = BASE
else:
    wk_dir = {
        "Frozen at Week 2 (cumulative)": "wk2",
        "Frozen at Week 3 (cumulative)": "wk3",
        "Frozen at Week 4 (cumulative, complete — all 32 teams at 4 games)": "wk4",
        "Frozen at Week 5 (cumulative, partial — MNF not yet played)": "wk5",
        "Week 3 only (isolated)": "wk3only",
        "Week 4 only (isolated, complete — 16/16 games)": "wk4only",
        "Week 5 only (isolated, partial — MNF not yet played)": "wk5only",
    }[SNAPSHOT]
    OUT = os.path.join(BASE, "output", wk_dir)
    TEAM_STATS_DIR = OUT
    if not os.path.isdir(OUT):
        st.error(f"output/{wk_dir}/ not found — run each compute_*.py script with the matching week "
                 f"argument first (e.g. `python compute_team_stats.py 2026 3 only`) to build this snapshot.")
        st.stop()

# ---------------------------------------------------------------------
# Real NFL team colors (verified hex codes) + automatic symbol assignment
# that separates teams whose PRIMARY colors are genuinely too close to
# tell apart (NE and SEA are the identical #002244 navy; CIN and DEN are
# the identical #FB4F14 orange; DAL and the Rams are the identical
# #003594 blue) — color stays authentic, shape resolves the collision.
# ---------------------------------------------------------------------
TEAM_COLORS = {
    "ARI": {"primary": "#97233F", "secondary": "#000000"},
    "ATL": {"primary": "#A71930", "secondary": "#000000"},
    "BAL": {"primary": "#241773", "secondary": "#000000"},
    "BUF": {"primary": "#00338D", "secondary": "#C60C30"},
    "CAR": {"primary": "#0085CA", "secondary": "#101820"},
    "CHI": {"primary": "#0B162A", "secondary": "#C83803"},
    "CIN": {"primary": "#FB4F14", "secondary": "#000000"},
    "CLE": {"primary": "#311D00", "secondary": "#FF3C00"},
    "DAL": {"primary": "#003594", "secondary": "#869397"},
    "DEN": {"primary": "#FB4F14", "secondary": "#002244"},
    "DET": {"primary": "#0076B6", "secondary": "#B0B7BC"},
    "GB":  {"primary": "#203731", "secondary": "#FFB612"},
    "HOU": {"primary": "#03202F", "secondary": "#A71930"},
    "IND": {"primary": "#002C5F", "secondary": "#A2AAAD"},
    "JAX": {"primary": "#101820", "secondary": "#D7A22A"},
    "KC":  {"primary": "#E31837", "secondary": "#FFB81C"},
    "LA":  {"primary": "#003594", "secondary": "#FFA300"},
    "LAC": {"primary": "#0080C6", "secondary": "#FFC20E"},
    "LV":  {"primary": "#000000", "secondary": "#A5ACAF"},
    "MIA": {"primary": "#008E97", "secondary": "#FC4C02"},
    "MIN": {"primary": "#4F2683", "secondary": "#FFC62F"},
    "NE":  {"primary": "#002244", "secondary": "#C60C30"},
    "NO":  {"primary": "#D3BC8D", "secondary": "#101820"},
    "NYG": {"primary": "#0B2265", "secondary": "#A71930"},
    "NYJ": {"primary": "#125740", "secondary": "#000000"},
    "PHI": {"primary": "#004C54", "secondary": "#A5ACAF"},
    "PIT": {"primary": "#FFB612", "secondary": "#101820"},
    "SEA": {"primary": "#002244", "secondary": "#69BE28"},
    "SF":  {"primary": "#AA0000", "secondary": "#B3995D"},
    "TB":  {"primary": "#D50A0A", "secondary": "#FF7900"},
    "TEN": {"primary": "#0C2340", "secondary": "#4B92DB"},
    "WAS": {"primary": "#5A1414", "secondary": "#FFB612"},
}
TEAM_COLOR_MAP = {t: c["primary"] for t, c in TEAM_COLORS.items()}


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _color_distance(h1, h2):
    r1, g1, b1 = _hex_to_rgb(h1)
    r2, g2, b2 = _hex_to_rgb(h2)
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


_SYMBOL_POOL = ["circle", "square", "diamond", "triangle-up", "triangle-down",
                "star", "cross", "x", "hexagon", "pentagon", "triangle-left", "triangle-right"]


def build_symbol_map(teams, distance_threshold=40):
    """Walk teams in order; give each the first symbol not already used
    by another team whose primary color is within `distance_threshold`
    (Euclidean RGB distance) of it. Guarantees real clashes (identical
    or near-identical hex) get a different marker shape instead of a
    faked, less-authentic color."""
    assigned = {}
    for t in teams:
        color = TEAM_COLOR_MAP.get(t, "#888888")
        used_by_close = {assigned[o] for o in assigned if _color_distance(color, TEAM_COLOR_MAP.get(o, "#888888")) < distance_threshold}
        for sym in _SYMBOL_POOL:
            if sym not in used_by_close:
                assigned[t] = sym
                break
        else:
            assigned[t] = _SYMBOL_POOL[len(assigned) % len(_SYMBOL_POOL)]
    return assigned


TEAM_SYMBOL_MAP = build_symbol_map(sorted(TEAM_COLORS.keys()))


def team_scatter(df, x, y, team_col, text_col=None, **kwargs):
    """A px.scatter with each point in its real team color, symbol
    resolving any close-color collision. Labels each point with
    `text_col` if given (e.g. player name), otherwise the team itself."""
    d = df.copy()
    fig = px.scatter(d, x=x, y=y, text=(text_col or team_col), color=team_col, symbol=team_col,
                      color_discrete_map=TEAM_COLOR_MAP, symbol_map=TEAM_SYMBOL_MAP, **kwargs)
    fig.update_traces(textposition="top center", marker=dict(size=14, line=dict(width=1, color="#00000030")))
    fig.update_layout(showlegend=False)
    return fig


def team_bar(df, x, y, **kwargs):
    """A px.bar with each team's bar in its real primary color."""
    fig = px.bar(df, x=x, y=y, color=x, color_discrete_map=TEAM_COLOR_MAP, **kwargs)
    fig.update_layout(showlegend=False)
    return fig


def show_table(df, **kwargs):
    """st.dataframe, but the row index starts at 1, not 0."""
    d = df.reset_index(drop=True)
    d.index = d.index + 1
    st.dataframe(d, **kwargs)


@st.cache_data
def _read_csv_cached(path, _mtime):
    # _mtime is only here to bust st.cache_data's cache key when the file
    # changes on disk — st.cache_data hashes arguments, not file content, so
    # without this a running server keeps serving a stale in-memory copy of
    # a CSV after a compute_*.py script rewrites it underneath it.
    return pd.read_csv(path)


def load(name, folder=OUT):
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        return pd.DataFrame()
    return _read_csv_cached(path, os.path.getmtime(path))


team_stats = load("team_stats_2026.csv", TEAM_STATS_DIR)
team_disc = load("team_discipline_and_tackling.csv")
qb = load("qb_stats.csv")
oldl = load("ol_dl_stats.csv")
rb = load("rb_stats.csv")
wr_team = load("wr_te_team_level.csv")
wr_player = load("wr_te_player_level_ngs.csv")
drops = load("wr_te_drop_rate.csv")
lbdb_team = load("lb_db_team_level.csv")
lbdb_player = load("lb_db_player_level_pfr.csv")
special = load("special_teams.csv")
tendency = load("play_type_tendency.csv")
def_tendency = load("defense_tendency_faced.csv")
qb_player = load("qb_player_level.csv")
qb_rush_player = load("qb_rush_player_level.csv")
rb_player = load("rb_player_level.csv")
def_player = load("defense_player_level_by_position.csv")
missed_tkl_split = load("team_missed_tackle_by_position_group.csv")
hustle_team_split = load("team_hustle_stats_by_position_group.csv")
hustle_player = load("defense_hustle_stats_player_level.csv")
quarter_splits = load("quarter_splits.csv")

if team_stats.empty:
    st.error("team_stats_2026.csv not found — run compute_team_stats.py first (writes to the nfl-analytics/ root).")
    st.stop()

st.title("🏈 NFL Team Diagnostic")
st.caption(f"Real 2026 season data via nflverse — showing **{SNAPSHOT}**. Charts are hover-interactive. "
           "Team colors are each team's real primary color; where two teams' colors are genuinely "
           "identical or near-identical (e.g. NE/SEA navy, CIN/DEN orange, DAL/Rams blue), the marker "
           "shape differs instead of faking a color that isn't real.")

if SNAPSHOT == "Latest (cumulative)":
    live_path = os.path.join(BASE, "team_stats_2026.csv")
    if os.path.exists(live_path):
        age_hours = (pd.Timestamp.now() - pd.Timestamp(os.path.getmtime(live_path), unit="s")).total_seconds() / 3600
        refreshed_at = pd.Timestamp(os.path.getmtime(live_path), unit="s").strftime("%Y-%m-%d %H:%M")
        max_games = int(team_stats["games"].max()) if not team_stats.empty else None
        if age_hours > 20:
            st.warning(f"\"Latest data\" was last computed {refreshed_at} ({age_hours/24:.1f} days ago, "
                       f"furthest team at {max_games} games) — more games may have been played since. "
                       "Rerun the compute_*.py scripts (no week argument) to refresh before trusting this as current.")
        else:
            st.caption(f"Latest data last computed {refreshed_at} — furthest team at {max_games} games.")

FAMILY_TABS = ["Overview", "QB", "O-Line / D-Line", "RB", "WR / TE", "LB / DB", "Special Teams", "Play-type tendency", "By quarter", "All metrics (raw)", "Glossary"]
tabs = st.tabs(FAMILY_TABS)

# ============================================================ OVERVIEW
with tabs[0]:
    st.subheader("Point differential — ranked")
    df = team_stats.sort_values("point_diff", ascending=False)
    st.plotly_chart(team_bar(df, "team", "point_diff"), use_container_width=True)

    st.subheader("Defensive touchdowns & safeties")
    st.caption("Turnovers a defense took all the way to the house (pick-sixes, fumble-return TDs), plus safeties forced.")
    highlights = team_stats[
        (team_stats["defensive_takeaway_tds"] > 0) | (team_stats["safeties_forced"] > 0)
    ][["team", "pick_six_td", "fumble_return_td", "defensive_takeaway_tds", "safeties_forced"]].sort_values(
        "defensive_takeaway_tds", ascending=False
    )
    if len(highlights):
        show_table(highlights, use_container_width=True, hide_index=True)
    else:
        st.caption("No defensive touchdowns or safeties yet this season.")

    st.subheader("Offense vs. defense quadrant")
    st.caption("Top-right = good offense AND good defense. Bubble size = |point differential|.")
    fig2 = team_scatter(team_stats, "off_epa_play", "def_epa_play_allowed", "team",
                         size=team_stats["point_diff"].abs() + 1,
                         hover_data=["point_diff"],
                         labels={"off_epa_play": "Offensive EPA/play (higher = better)",
                                 "def_epa_play_allowed": "Defensive EPA/play allowed (lower = better)"})
    fig2.update_yaxes(autorange="reversed")
    st.plotly_chart(fig2, use_container_width=True)

    if not team_disc.empty:
        merged = team_stats.merge(team_disc, on="team", suffixes=("", "_disc"))
        st.subheader("Discipline vs. performance")
        st.caption("Locked call: penalties are a real signal — flag teams winning DESPITE high penalties (due for regression).")
        fig3 = team_scatter(merged, "penalties_per_game", "point_diff", "team",
                             hover_data=["team_missed_tackle_pct"],
                             labels={"penalties_per_game": "Penalties per game", "point_diff": "Point differential"})
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Correlation check — does each metric actually track point differential?")
    corr_source = team_stats.merge(team_disc, on="team", how="left") if not team_disc.empty else team_stats
    numeric = corr_source.select_dtypes(include=[np.number]).drop(columns=["point_diff"], errors="ignore")
    corrs = numeric.corrwith(corr_source["point_diff"]).dropna().sort_values()
    fig4 = px.bar(corrs, orientation="h", labels={"value": "Correlation with point differential", "index": ""})
    fig4.add_vline(x=0)
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("Only 3 weeks played — treat as directional, not conclusive.")

    with st.expander("Raw team table"):
        show_table(team_stats, use_container_width=True)

# ============================================================ QB
with tabs[1]:
    if qb.empty:
        st.info("qb_stats.csv not found.")
    else:
        st.subheader("EPA/dropback vs. CPOE")
        st.caption("Locked call: shown side by side, no single headline stat.")
        fig = team_scatter(qb, "epa_per_dropback", "cpoe", "team", hover_data=["int_pct"],
                            labels={"epa_per_dropback": "EPA per dropback", "cpoe": "Completion % over expected"})
        fig.add_hline(y=0, line_dash="dot")
        fig.add_vline(x=0, line_dash="dot")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("QB style — not a quality ranking")
        st.caption("Locked call: time-to-throw × depth of target describes IDENTITY (quick-game vs. down-field), not who's \"better.\"")
        fig2 = team_scatter(qb, "avg_time_to_throw", "avg_intended_air_yards", "team",
                             labels={"avg_time_to_throw": "Avg. time to throw (sec)", "avg_intended_air_yards": "Avg. intended air yards"})
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Sack rate")
        st.caption("Cross-reference with the O-Line tab — shown in both places per the locked call.")
        st.plotly_chart(team_bar(qb.sort_values("sack_rate", ascending=False), "team", "sack_rate"), use_container_width=True)

        with st.expander("Raw QB table (team level)"):
            show_table(qb, use_container_width=True)

        if not qb_player.empty:
            st.subheader("Individual QBs")
            st.caption("Computed directly from play-by-play — 10+ attempts.")
            figp = team_scatter(qb_player, "epa_per_play", "int_pct", "team", text_col="player", size="attempts",
                                 labels={"epa_per_play": "EPA per play", "int_pct": "INT %"})
            st.plotly_chart(figp, use_container_width=True, height=550)
            with st.expander("Raw individual QB table"):
                show_table(qb_player, use_container_width=True)

        if not qb_rush_player.empty:
            st.subheader("QB rushing — separate from the RB tab on purpose")
            st.caption("Designed QB runs and scrambles, computed the same way as RB rushing but kept in its own "
                       "chart — a mobile QB's carries used to leak into the RB scatter below and skew it.")
            figqr = team_scatter(qb_rush_player, "pct_carries_4plus", "explosive_rate_10plus", "team", text_col="player", size="carries",
                                  labels={"pct_carries_4plus": "% carries 4+ yards (consistency)", "explosive_rate_10plus": "% carries 10+ yards (explosive)"})
            st.plotly_chart(figqr, use_container_width=True, height=450)
            with st.expander("Raw QB rushing table"):
                show_table(qb_rush_player.sort_values("carries", ascending=False), use_container_width=True)

# ============================================================ OL/DL
with tabs[2]:
    if oldl.empty:
        st.info("ol_dl_stats.csv not found.")
    else:
        st.subheader("Sack fault split — QB vs. O-line")
        st.caption("Locked call: kept, since most public analysis just blames the O-line by default.")
        melt = oldl.melt(id_vars="team", value_vars=["qb_fault_sacks", "ol_fault_sacks"], var_name="fault", value_name="sacks")
        st.plotly_chart(px.bar(melt, x="team", y="sacks", color="fault", barmode="stack"), use_container_width=True)

        st.subheader("QB hits — allowed vs. generated")
        st.caption("Locked call: QB hits, not sacks, as the primary pressure signal.")
        melt2 = oldl.melt(id_vars="team", value_vars=["qb_hits_allowed", "qb_hits_generated"], var_name="side", value_name="hits")
        st.plotly_chart(px.bar(melt2, x="team", y="hits", color="side", barmode="group"), use_container_width=True)

        if not rb.empty:
            st.subheader("Run-blocking vs. RB talent")
            st.caption("Locked call: cross-reference O-line run yards/carry against RB explosive-run rate to separate the two.")
            cross = oldl.merge(rb, on="team", how="inner")
            fig3 = team_scatter(cross, "run_yards_per_carry_off", "explosive_run_rate_10plus", "team",
                                 labels={"run_yards_per_carry_off": "Team run yards/carry", "explosive_run_rate_10plus": "RB explosive-run rate (10+ yds)"})
            st.plotly_chart(fig3, use_container_width=True)

        with st.expander("Raw O-Line/D-Line table (team level)"):
            show_table(oldl, use_container_width=True)

        if not def_player.empty:
            st.subheader("Individual D-linemen")
            dlp = def_player[def_player["position_group"] == "DL"].sort_values("pressures", ascending=False)
            show_table(dlp, use_container_width=True, height=350)

        st.info(
            "**Honest limitation on individual O-linemen:** no free data source attributes run-blocking or "
            "pass-pro performance to a specific offensive lineman — that requires paid, per-player charting "
            "(PFF-style). The team-level proxies above are the real ceiling without buying that data."
        )

# ============================================================ RB
with tabs[3]:
    if rb.empty:
        st.info("rb_stats.csv not found.")
    else:
        st.subheader("% of carries gaining 4+ yards — the headline (not raw YPC)")
        st.caption("Locked call: consistency leads over YPC, which one long run can distort.")
        st.plotly_chart(team_bar(rb.sort_values("pct_carries_4plus_yards", ascending=False), "team", "pct_carries_4plus_yards"),
                         use_container_width=True)

        st.subheader("Consistency vs. explosiveness")
        st.caption("Locked call: explosive rate is flagged, not credited to the RB alone without film.")
        fig2 = team_scatter(rb, "pct_carries_4plus_yards", "explosive_run_rate_10plus", "team", size="carries",
                             labels={"pct_carries_4plus_yards": "% carries 4+ yards (consistency)", "explosive_run_rate_10plus": "% carries 10+ yards (explosive)"})
        st.plotly_chart(fig2, use_container_width=True)

        with st.expander("Raw RB table (team level)"):
            show_table(rb, use_container_width=True)

        if not rb_player.empty:
            st.subheader("Individual RBs")
            st.caption("Computed directly from play-by-play, 5+ carries, real RBs/FBs only — QB rushing is a separate chart on the QB tab.")
            sub = rb_player[rb_player["carries"] >= 8]
            figp = team_scatter(sub, "pct_carries_4plus", "explosive_rate_10plus", "team", text_col="player", size="carries",
                                 labels={"pct_carries_4plus": "% carries 4+ yards (consistency)", "explosive_rate_10plus": "% carries 10+ yards (explosive)"})
            st.plotly_chart(figp, use_container_width=True, height=550)

            if "efficiency" in rb_player.columns and rb_player["efficiency"].notna().any():
                st.subheader("Cutback tendency — real NGS \"efficiency\" metric")
                st.caption("NGS's own definition: yards actually traveled per rushing yard gained. Near 1.0 = runs "
                           "mostly straight downhill; well above 1.0 = a back who cuts back / dances behind the "
                           "line looking for a better lane. Useful for a defense to know what it's about to face, "
                           "and for an offense to know whether its back is leaving yards on the field by bouncing "
                           "too much. Not every back has this NGS field populated yet this early in the season.")
                sub_eff = rb_player[(rb_player["carries"] >= 8) & rb_player["efficiency"].notna()]
                fig_cut = team_scatter(sub_eff, "efficiency", "ypc", "team", text_col="player", size="carries",
                                        labels={"efficiency": "Yards traveled per yard gained (cutback tendency)", "ypc": "Yards per carry"})
                st.plotly_chart(fig_cut, use_container_width=True, height=500)

            with st.expander("Raw individual RB table"):
                show_table(rb_player.sort_values("carries", ascending=False), use_container_width=True)

# ============================================================ WR/TE
with tabs[4]:
    if wr_player.empty:
        st.info("wr_te_player_level_ngs.csv not found.")
    else:
        st.subheader("Skill (separation) vs. role/trust (air-yards share)")
        st.caption("Locked call: two different questions, deliberately not combined into one score.")
        team_filter = st.selectbox("Filter by team (optional)", ["All"] + sorted(wr_player["team_abbr"].dropna().unique().tolist()), key="wrfilter")
        wp = wr_player if team_filter == "All" else wr_player[wr_player["team_abbr"] == team_filter]
        wp = wp[wp["targets"] >= 5]
        fig = team_scatter(wp, "avg_separation", "percent_share_of_intended_air_yards", "team_abbr",
                            text_col="player_display_name", size="targets",
                            hover_data=["targets", "catch_percentage", "avg_yac_above_expectation"],
                            labels={"avg_separation": "Avg. separation (skill)", "percent_share_of_intended_air_yards": "% share of team's air yards (role/trust)"})
        st.plotly_chart(fig, use_container_width=True, height=550)

        st.subheader("YAC over expected — after-the-catch skill (separate from route-running)")
        top_yac = wr_player[wr_player["targets"] >= 8].sort_values("avg_yac_above_expectation", ascending=False).head(20)
        fig_yac = px.bar(top_yac, x="player_display_name", y="avg_yac_above_expectation", color="team_abbr",
                          color_discrete_map=TEAM_COLOR_MAP)
        fig_yac.update_layout(showlegend=False)
        st.plotly_chart(fig_yac, use_container_width=True)

        if not drops.empty:
            st.subheader("Drop rate (5+ targets, small samples — 3 weeks played)")
            show_table(drops.head(30), use_container_width=True)

        with st.expander("Raw WR/TE player table"):
            show_table(wr_player, use_container_width=True)

# ============================================================ LB/DB
with tabs[5]:
    if lbdb_team.empty:
        st.info("lb_db_team_level.csv not found.")
    else:
        st.subheader("Yards allowed per target — the CB headline (not completion %)")
        st.caption("Locked call: yards/target captures actual damage, completion% alone can mislead.")
        st.plotly_chart(team_bar(lbdb_team.sort_values("yards_allowed_per_target"), "team", "yards_allowed_per_target"),
                         use_container_width=True)

        st.subheader("Interceptions generated")
        st.caption("Note: forced fumbles aren't in any free source — showing INTs honestly, not faking the rest.")
        st.plotly_chart(team_bar(lbdb_team.sort_values("interceptions", ascending=False), "team", "interceptions"), use_container_width=True)

        if not missed_tkl_split.empty:
            st.subheader("Missed-tackle % — LB vs. DB, split by real roster position")
            fig5 = px.bar(missed_tkl_split, x="team", y="missed_tackle_pct", color="position_group", barmode="group")
            st.plotly_chart(fig5, use_container_width=True)

        if not hustle_team_split.empty:
            st.subheader("Hustle stats — LB vs. DB, split by real roster position")
            st.caption("From raw play-by-play's own charting (none of this is in the PFR table above). "
                       "\"PBU\" = pass broken up (incompletion caused); \"passes_defended\" also folds in "
                       "interceptions where the same player gets pass-defense credit too (standard box-score "
                       "convention). Fumble recoveries only count when the DEFENSE recovered — an offense "
                       "recovering its own fumble isn't a defensive stat.")
            hustle_metric = st.radio(
                "Metric", ["pbu", "passes_defended", "forced_fumbles", "fumble_recoveries"],
                horizontal=True, key="hustle_team_metric",
            )
            fig6 = px.bar(hustle_team_split, x="team", y=hustle_metric, color="position_group", barmode="group")
            st.plotly_chart(fig6, use_container_width=True)

        if not hustle_player.empty:
            st.subheader("Individual hustle stats — LB vs. DB leaders")
            hustle_pos_filter = st.radio("Position group", ["DB", "LB"], horizontal=True, key="hustle_player_pos")
            hp = hustle_player[hustle_player["position_group"] == hustle_pos_filter].sort_values(
                ["forced_fumbles", "fumble_recoveries", "pbu"], ascending=False
            )
            show_table(hp, use_container_width=True, height=400)

        if not def_player.empty:
            st.subheader("Individual defenders, by real position group (DL / LB / DB)")
            pos_group_filter = st.radio("Position group", ["DL", "LB", "DB"], horizontal=True)
            dp = def_player[def_player["position_group"] == pos_group_filter].sort_values("pressures", ascending=False)
            show_table(dp, use_container_width=True, height=400)

# ============================================================ SPECIAL TEAMS
with tabs[6]:
    if special.empty:
        st.info("special_teams.csv not found.")
    else:
        st.subheader("Field goal % by distance bucket")
        fg_buckets = ["<30", "30-39", "40-49", "50+"]
        fg_rows = []
        for b in fg_buckets:
            for _, r in special.iterrows():
                att, made = r.get(f"fg_att_{b}"), r.get(f"fg_made_{b}")
                fg_rows.append({
                    "team": r["team"], "bucket": b, "fg_pct": r.get(f"fg_pct_{b}"),
                    "label": f"{int(made)}/{int(att)}" if pd.notna(att) and att > 0 else "",
                })
        fg_melt = pd.DataFrame(fg_rows)
        fig_fg = px.bar(fg_melt, x="team", y="fg_pct", color="bucket", barmode="group", text="label")
        fig_fg.update_traces(textposition="outside")
        st.plotly_chart(fig_fg, use_container_width=True)
        st.caption("Bar labels are made/attempts for that distance bucket — a 100% or 0% on a 1-attempt "
                   "bucket means exactly that: one kick, not a real trend. ⚠ Small-sample warning: few weeks "
                   "played so far, every bucket is thin.")

        st.subheader("Punt / kickoff net average")
        melt2 = special.melt(id_vars="team", value_vars=["punt_net_avg", "kickoff_net_avg"], var_name="kick_type", value_name="net_yards")
        st.plotly_chart(px.bar(melt2, x="team", y="net_yards", color="kick_type", barmode="group"), use_container_width=True)

        with st.expander("Raw special teams table"):
            show_table(special, use_container_width=True)

# ============================================================ PLAY-TYPE TENDENCY
with tabs[7]:
    if tendency.empty:
        st.info("play_type_tendency.csv not found.")
    else:
        st.subheader("Run vs. pass split")
        st.caption("Straight from play-by-play — every called run and pass play, not the FTN-charted "
                   "subset below (so this one never has a coverage gap).")
        rp_melt = tendency.melt(id_vars="team", value_vars=["run_pct", "pass_pct"], var_name="play_type", value_name="pct")
        rp_melt["play_type"] = rp_melt["play_type"].map({"run_pct": "Run", "pass_pct": "Pass"})
        counts = tendency.melt(id_vars="team", value_vars=["run_plays", "pass_plays"], var_name="play_type", value_name="plays")
        counts["play_type"] = counts["play_type"].map({"run_plays": "Run", "pass_plays": "Pass"})
        rp_melt = rp_melt.merge(counts, on=["team", "play_type"])
        fig_rp = px.bar(rp_melt, x="team", y="pct", color="play_type", barmode="group",
                         text="plays", labels={"pct": "% of plays", "play_type": "Play type"})
        fig_rp.update_traces(textposition="outside")
        st.plotly_chart(fig_rp, use_container_width=True)

        st.subheader("Offensive identity — play-action / RPO / screen / motion / no-huddle rates")
        melt = tendency.melt(id_vars="team", value_vars=["play_action_pct", "rpo_pct", "screen_pct", "no_huddle_pct", "motion_pct"],
                              var_name="tendency_type", value_name="pct")
        st.plotly_chart(px.bar(melt, x="team", y="pct", color="tendency_type", barmode="group"), use_container_width=True)

        if not qb.empty:
            cross = tendency.merge(qb[["team", "epa_per_dropback"]], on="team", how="inner")
            st.subheader("Is the identity actually working? Motion rate vs. QB EPA/dropback")
            fig2 = team_scatter(cross, "motion_pct", "epa_per_dropback", "team",
                                 labels={"motion_pct": "Motion usage %", "epa_per_dropback": "QB EPA/dropback"})
            st.plotly_chart(fig2, use_container_width=True)

        with st.expander("Raw play-type tendency table"):
            show_table(tendency, use_container_width=True)

        st.divider()

    if def_tendency.empty:
        st.info("defense_tendency_faced.csv not found.")
    else:
        st.subheader("Defensive identity — what does this defense typically face?")
        st.caption("Same real FTN charting as above, grouped by the team ON DEFENSE instead of on offense — "
                   "this is what opposing offenses throw at this defense, not a scheme stat like blitz rate or "
                   "man/zone coverage (that's paid PFF-style charting, not in anything free pulled here).")
        melt_def = def_tendency.melt(id_vars="team", value_vars=["play_action_faced_pct", "rpo_faced_pct", "screen_faced_pct",
                                                                   "no_huddle_faced_pct", "motion_faced_pct"],
                                      var_name="tendency_type", value_name="pct")
        st.plotly_chart(px.bar(melt_def, x="team", y="pct", color="tendency_type", barmode="group"), use_container_width=True)

        if not lbdb_team.empty:
            cross_def = def_tendency.merge(lbdb_team[["team", "yards_allowed_per_target"]], on="team", how="inner")
            st.subheader("Is facing more motion actually hurting this defense? Motion faced vs. yards allowed/target")
            fig3 = team_scatter(cross_def, "motion_faced_pct", "yards_allowed_per_target", "team",
                                 labels={"motion_faced_pct": "Motion faced %", "yards_allowed_per_target": "Yards allowed/target"})
            st.plotly_chart(fig3, use_container_width=True)

        with st.expander("Raw defense-tendency-faced table"):
            show_table(def_tendency, use_container_width=True)

        st.divider()
        st.subheader("Defensive scheme — blitz rate and box count")
        st.caption("Real FTN charting of this defense's OWN behavior — not what it faces, what it does. "
                   "Restricted to plays where pass-rush/box count was actually charted, so the small-sample "
                   "warning applies even harder here than elsewhere. Man/zone coverage shell is the one real "
                   "scheme signal that's genuinely not available for free — only paid PFF-style charting has it.")
        colb1, colb2 = st.columns(2)
        with colb1:
            st.markdown("**Blitz rate %**")
            st.plotly_chart(team_bar(def_tendency.sort_values("blitz_rate_pct", ascending=False), "team", "blitz_rate_pct"),
                             use_container_width=True)
        with colb2:
            st.markdown("**Stacked-box rate % (8+ defenders)**")
            st.plotly_chart(team_bar(def_tendency.sort_values("stacked_box_pct", ascending=False), "team", "stacked_box_pct"),
                             use_container_width=True)

        if not lbdb_team.empty:
            st.subheader("Does blitzing more actually generate more pressure?")
            cross_blitz = def_tendency.merge(lbdb_team[["team", "pressures_generated"]], on="team", how="inner")
            fig_blitz = team_scatter(cross_blitz, "blitz_rate_pct", "pressures_generated", "team",
                                      labels={"blitz_rate_pct": "Blitz rate %", "pressures_generated": "Pressures generated"})
            st.plotly_chart(fig_blitz, use_container_width=True)

        st.subheader("D-line alone vs. blitz-assisted — where does the pressure actually come from?")
        st.caption("Same rush-charted plays, split by whether extra rushers were sent (blitz) or not (natural rush), "
                   "then checked against the real per-play QB-hit/sack outcome. If a team's blitz number barely beats "
                   "its natural-rush number, the blitz may be more disguise than production for that defense.")
        pr_melt = def_tendency.melt(id_vars="team", value_vars=["pressure_rate_natural_rush", "pressure_rate_blitz"],
                                     var_name="rush_type", value_name="pressure_rate_pct")
        pr_melt["rush_type"] = pr_melt["rush_type"].map({"pressure_rate_natural_rush": "Natural rush", "pressure_rate_blitz": "Blitzing"})
        st.plotly_chart(px.bar(pr_melt, x="team", y="pressure_rate_pct", color="rush_type", barmode="group"),
                         use_container_width=True)

# ============================================================ BY QUARTER
with tabs[8]:
    if quarter_splits.empty:
        st.info("quarter_splits.csv not found — run compute_quarter_splits.py first.")
    else:
        st.subheader("One team's performance, broken out by quarter")
        st.caption("Scoring, giveaways, completion %, and run/pass split — Q1 through Q4 (+ OT if played). "
                   "Small sample per quarter even this early in a season, more so than the season-long numbers elsewhere.")
        team_choice = st.selectbox("Team", sorted(quarter_splits["team"].unique()), key="quarter_team")
        qd = quarter_splits[quarter_splits["team"] == team_choice].copy()
        qd["quarter"] = pd.Categorical(qd["quarter"], categories=["Q1", "Q2", "Q3", "Q4", "OT"], ordered=True)
        qd = qd.sort_values("quarter")
        primary = TEAM_COLOR_MAP.get(team_choice, "#4477aa")

        st.markdown("**Points scored vs. allowed, by quarter**")
        score_melt = qd.melt(id_vars="quarter", value_vars=["points_scored", "points_allowed"],
                              var_name="side", value_name="points")
        score_melt["side"] = score_melt["side"].map({"points_scored": "Scored", "points_allowed": "Allowed"})
        st.plotly_chart(px.bar(score_melt, x="quarter", y="points", color="side", barmode="group",
                                color_discrete_map={"Scored": primary, "Allowed": "#999999"}),
                         use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Giveaways, by quarter**")
            st.plotly_chart(px.bar(qd, x="quarter", y="giveaways", color_discrete_sequence=[primary]),
                             use_container_width=True)
        with col2:
            st.markdown("**Completion %, by quarter**")
            st.plotly_chart(px.bar(qd, x="quarter", y="completion_pct", color_discrete_sequence=[primary]),
                             use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**Offense: run vs. pass %, by quarter**")
            rp_melt = qd.melt(id_vars="quarter", value_vars=["pass_pct", "run_pct"], var_name="play", value_name="pct")
            rp_melt["play"] = rp_melt["play"].map({"pass_pct": "Pass", "run_pct": "Run"})
            st.plotly_chart(px.bar(rp_melt, x="quarter", y="pct", color="play", barmode="stack",
                                    color_discrete_map={"Pass": primary, "Run": "#999999"}),
                             use_container_width=True)
        with col4:
            st.markdown("**Defense: run vs. pass % faced, by quarter**")
            rp_melt_def = qd.melt(id_vars="quarter", value_vars=["pass_pct_faced", "run_pct_faced"], var_name="play", value_name="pct")
            rp_melt_def["play"] = rp_melt_def["play"].map({"pass_pct_faced": "Pass faced", "run_pct_faced": "Run faced"})
            st.plotly_chart(px.bar(rp_melt_def, x="quarter", y="pct", color="play", barmode="stack",
                                    color_discrete_map={"Pass faced": primary, "Run faced": "#999999"}),
                             use_container_width=True)

        col5, col6 = st.columns(2)
        with col5:
            st.markdown("**Offense EPA/play, by quarter**")
            st.plotly_chart(px.bar(qd, x="quarter", y="epa_per_play", color_discrete_sequence=[primary]),
                             use_container_width=True)
        with col6:
            st.markdown("**Defense EPA/play allowed, by quarter**")
            st.caption("Lower (more negative) is better here — same convention as the season-long number.")
            st.plotly_chart(px.bar(qd, x="quarter", y="def_epa_per_play", color_discrete_sequence=[primary]),
                             use_container_width=True)

        if "blitz_rate_pct" in qd.columns and qd["blitz_rate_pct"].notna().any():
            st.divider()
            st.subheader("Defensive scheme calling, by quarter — and what it gets them")
            st.caption("Same real blitz/box charting as the Play-type tendency tab, broken out by quarter — "
                       "does this defense call it differently as the game goes on, and is it working (EPA that quarter)?")
            col7, col8 = st.columns(2)
            with col7:
                st.markdown("**Blitz rate %, by quarter**")
                st.plotly_chart(px.bar(qd, x="quarter", y="blitz_rate_pct", color_discrete_sequence=[primary]),
                                 use_container_width=True)
            with col8:
                st.markdown("**Stacked-box rate %, by quarter**")
                st.plotly_chart(px.bar(qd, x="quarter", y="stacked_box_pct", color_discrete_sequence=[primary]),
                                 use_container_width=True)
            fig_scheme = px.bar(qd, x="quarter", y="blitz_rate_pct", color_discrete_sequence=[primary],
                                 labels={"blitz_rate_pct": "Blitz rate %"})
            fig_scheme.add_scatter(x=qd["quarter"], y=qd["def_epa_per_play"] * 100, mode="lines+markers",
                                    name="Defense EPA/play x100 (lower=better)", yaxis="y")
            st.markdown("**Blitz rate vs. defense EPA/play that same quarter** (EPA scaled x100 to share the axis)")
            st.plotly_chart(fig_scheme, use_container_width=True)

        off_spread = round(float(qd["epa_per_play"].max() - qd["epa_per_play"].min()), 3) if qd["epa_per_play"].notna().any() else None
        def_spread = round(float(qd["def_epa_per_play"].max() - qd["def_epa_per_play"].min()), 3) if qd["def_epa_per_play"].notna().any() else None
        if off_spread is not None:
            st.info(f"**Quarter matters:** {team_choice}'s offense EPA/play swings by {off_spread} between its best and worst "
                    f"quarter this season, and defense EPA/play allowed swings by {def_spread} — on a small sample, treat any "
                    "single quarter as a data point, not a verdict, but a swing this size is exactly why teams scout quarter-by-quarter "
                    "in the first place.")

        st.warning("**Honest gap:** missed-tackle % can't be broken out by quarter — PFR's missed-tackle count is a "
                   "weekly/season charting total, never tagged to an individual play or quarter in any free data source "
                   "pulled here, unlike points/giveaways/completions/play-type which come straight from play-by-play.")

        with st.expander("Raw quarter-split table, this team"):
            show_table(qd.drop(columns=["team"]), use_container_width=True)
        with st.expander("Raw quarter-split table, all teams"):
            show_table(quarter_splits, use_container_width=True)

# ============================================================ ALL METRICS (RAW)
# Sourced from metric_glossary.py (shared with compute_team_ledger.py and the
# Glossary tab below) so this text never drifts from the other two places it's
# shown. A few extra keys used only by individual-player files (not team-level)
# are added here since metric_glossary.py covers team-level metrics only.
METRIC_RELEVANCE = dict(RELEVANCE_BY_KEY)
METRIC_RELEVANCE.update({
    "percent_share_of_intended_air_yards": "The receiver ROLE/TRUST signal — how much the offense actually goes to this player, distinct from raw skill.",
    "avg_yac_above_expectation": "A distinct after-the-catch skill, separate from route-running/separation.",
    "missed_tackle_pct": "Split LB vs. DB — same number, different diagnosis depending on which group is missing tackles.",
    "efficiency": "Real NGS field: yards traveled per rushing yard gained — the cutback/lateral-movement signal. Near 1.0 = straight downhill, well above = a back who cuts back a lot.",
    "rush_yards_over_expected_per_att": "Real NGS field: rushing yards gained vs. what an average back would gain given the blocking/box/defenders — a context-adjusted efficiency number.",
    "pct_carries_vs_stacked_box": "Real NGS field: % of carries against 8+ defenders in the box — shows how much a defense is selling out to stop the run.",
    "def_epa_per_play": "Defense EPA/play allowed, computed the same way as the season number but isolated to one quarter — negative is good.",
    "pass_pct_faced": "% of plays a defense faced that were pass plays, in one quarter — defense-side mirror of offense pass %.",
    "run_pct_faced": "% of plays a defense faced that were run plays, in one quarter — defense-side mirror of offense run %.",
})

with tabs[9]:
    st.subheader("Every computed metric, raw — table + ranked chart + relevance, no editorializing yet")
    st.caption("This is the \"see it all yourself\" tab. Insight-driven visuals live in the family tabs above; this one is exhaustive, not curated.")

    all_files = {
        "Team — core": team_stats,
        "Team — discipline & tackling": team_disc,
        "QB — team level": qb,
        "QB — individual": qb_player,
        "QB — rushing": qb_rush_player,
        "O-Line/D-Line — team level": oldl,
        "RB — team level": rb,
        "RB — individual": rb_player,
        "WR/TE — team level": wr_team,
        "WR/TE — individual (NGS)": wr_player,
        "WR/TE — drop rate": drops,
        "LB/DB — team level": lbdb_team,
        "LB/DB — individual by position": def_player,
        "Missed tackle — LB vs DB split": missed_tkl_split,
        "Special teams": special,
        "Play-type tendency (offense)": tendency,
        "Play-type tendency (defense faced)": def_tendency,
        "By-quarter splits": quarter_splits,
    }
    file_choice = st.selectbox("File", list(all_files.keys()))
    fdf = all_files[file_choice]
    if fdf.empty:
        st.warning("This file hasn't been computed yet.")
    else:
        team_col = next((c for c in ["team", "team_abbr"] if c in fdf.columns), None)
        label_col = team_col or next((c for c in ["player", "player_display_name", "pfr_player_name"] if c in fdf.columns), fdf.columns[0])
        numeric_cols = [c for c in fdf.columns if pd.api.types.is_numeric_dtype(fdf[c]) and c not in ("week", "season")]
        metric = st.selectbox("Metric", numeric_cols)

        st.markdown(f"**Relevance:** {METRIC_RELEVANCE.get(metric, 'Supporting metric — not yet individually annotated, still real computed data.')}")

        chart_df = fdf[[label_col, metric]].dropna().sort_values(metric, ascending=False)
        if len(chart_df) > 40:
            chart_df = chart_df.head(40)
            st.caption("Showing top 40 rows by this metric.")
        if team_col:
            st.plotly_chart(team_bar(chart_df, label_col, metric), use_container_width=True)
        else:
            st.plotly_chart(px.bar(chart_df, x=label_col, y=metric), use_container_width=True)

        show_table(fdf, use_container_width=True, height=350)

with tabs[10]:
    st.subheader("Glossary — every metric, in plain language")
    st.caption("What it is, in one line, and why it's worth tracking — no jargon left unexplained. "
               "Grouped the same way as the family tabs above.")
    search = st.text_input("Search a metric name", "")
    for family in FAMILIES:
        family_metrics = [m for m in METRIC_META if m[1] == family]
        if search:
            family_metrics = [m for m in family_metrics if search.lower() in m[2].lower() or search.lower() in m[0].lower()]
        if not family_metrics:
            continue
        with st.expander(f"{family} ({len(family_metrics)})", expanded=bool(search)):
            for key, fam, label, simple, explanation, relevance, source in family_metrics:
                st.markdown(f"**{label}**")
                st.markdown(f"*{simple}*")
                st.markdown(f"What it is: {explanation}")
                st.markdown(f"Why it matters: {relevance}")
                st.markdown("---")

st.divider()
st.caption("Source: nflverse (nflfastR, NGS, PFR, FTN) via nfl_data_py. Rerun the compute_*.py scripts to refresh after more games.")
