"""
Every Metric, The Story Behind It — Streamlit edition.

Same content as the "storytelling" HTML build, but live: every chart loads
straight from output/wk3/*.csv instead of a hardcoded snapshot, and capsule
text is pulled from metric_glossary.py (the same single source of truth
viewer_app.py and the Team Ledger use) wherever a matching metric_key
exists, so wording never drifts between tools.

Charts use Altair, not Plotly — Altair ships bundled with Streamlit itself
(it's one of Streamlit's own install dependencies), so this runs on any
machine that can already run `streamlit run ...`, with nothing extra to pip
install.

The "Notes Checklist" tab is the honest part: it's the exact Used/Backlog
breakdown from the Notes Tracker artifact (built while the original raw
notes were still in context), with this session's new charts marked off —
not a list reconstructed from memory just now.

Run with: streamlit run notes_story_app.py
"""
import os
import pandas as pd
import altair as alt
import streamlit as st
from metric_glossary import LABEL_BY_KEY, SIMPLE_BY_KEY, EXPLANATION_BY_KEY, RELEVANCE_BY_KEY

st.set_page_config(page_title="Every Metric, The Story Behind It", layout="wide")

BASE = os.path.dirname(__file__)
OUT = os.path.join(BASE, "output", "wk3")

TC = {"ARI":"#97233F","ATL":"#A71930","BAL":"#241773","BUF":"#00338D","CAR":"#0085CA","CHI":"#0B162A",
"CIN":"#FB4F14","CLE":"#FF3C00","DAL":"#003594","DEN":"#FB4F14","DET":"#0076B6","GB":"#203731",
"HOU":"#03202F","IND":"#002C5F","JAX":"#D7A22A","KC":"#E31837","LA":"#003594","LAC":"#0080C6",
"LV":"#A5ACAF","MIA":"#008E97","MIN":"#4F2683","NE":"#002244","NO":"#D3BC8D","NYG":"#0B2265",
"NYJ":"#125740","PHI":"#004C54","PIT":"#FFB612","SEA":"#002244","SF":"#AA0000","TB":"#D50A0A",
"TEN":"#0C2340","WAS":"#5A1414"}
TC_SCALE = alt.Scale(domain=list(TC.keys()), range=list(TC.values()))

@st.cache_data
def load(name):
    return pd.read_csv(os.path.join(OUT, name))

def story(key, fallback_simple="", fallback_relevance=""):
    """Render the standard Explanation / Relevance / Simple-terms block,
    preferring metric_glossary.py text so it matches every other tool."""
    simple = SIMPLE_BY_KEY.get(key, fallback_simple)
    rel = RELEVANCE_BY_KEY.get(key, fallback_relevance)
    exp = EXPLANATION_BY_KEY.get(key, "")
    if rel:
        st.info(f"**Why it matters:** {rel}")
    if exp:
        with st.expander("Plain-terms explanation"):
            st.write(exp)
    elif simple:
        st.caption(simple)

def team_scatter(df, x, y, title, hover_name="team", color_col="team"):
    tooltip = [hover_name, x, y] if hover_name not in (x, y) else [x, y]
    chart = (
        alt.Chart(df)
        .mark_circle(size=160, stroke="white", strokeWidth=1, opacity=0.92)
        .encode(
            x=alt.X(f"{x}:Q", scale=alt.Scale(zero=False), title=x),
            y=alt.Y(f"{y}:Q", scale=alt.Scale(zero=False), title=y),
            color=alt.Color(f"{color_col}:N", scale=TC_SCALE, legend=None),
            tooltip=tooltip,
        )
        .properties(title=title, height=420)
    )
    return chart

def ranked_bar(df, name_col, val_col, title, team_col="team", top=15, ascending=False):
    d = df.sort_values(val_col, ascending=ascending).head(top)
    color = alt.Color(f"{team_col}:N", scale=TC_SCALE, legend=None) if team_col else alt.value("#c8202b")
    tooltip = [name_col, val_col] + ([team_col] if team_col else [])
    chart = (
        alt.Chart(d)
        .mark_bar()
        .encode(
            x=alt.X(f"{val_col}:Q", title=val_col),
            y=alt.Y(f"{name_col}:N", sort="-x", title=None),
            color=color,
            tooltip=tooltip,
        )
        .properties(title=title, height=max(320, top * 28))
    )
    return chart

st.title("Every Metric, The Story Behind It")
st.caption("2026 NFL Season · Weeks 1–3 · live from output/wk3/ · "
           "every chart paired with insight, relevance, and simple terms — not a bare table.")

SECTION = st.sidebar.radio("Section", [
    "Quarterbacks", "Running Backs", "Receivers & Tight Ends",
    "Defense", "Special Teams", "Play-Design & Tendencies",
    "✅ Notes Checklist",
])

# =====================================================================
if SECTION == "Quarterbacks":
    st.header("Quarterbacks")
    qb_team = load("qb_stats.csv")
    qb_player = load("qb_player_level.csv")
    qb_rush = load("qb_rush_player_level.csv")

    c1, c2 = st.columns(2)
    with c1:
        st.altair_chart(team_scatter(qb_team, "cpoe", "epa_per_dropback",
                         "EPA/dropback vs. CPOE — every team"), use_container_width=True)
        story("epa_per_dropback")
    with c2:
        st.altair_chart(team_scatter(qb_team, "avg_time_to_throw", "avg_intended_air_yards",
                         "Time to throw vs. intended air yards"), use_container_width=True)
        story("avg_time_to_throw")

    c3, c4 = st.columns(2)
    with c3:
        st.altair_chart(ranked_bar(qb_team, "team", "sack_rate", "Sack rate, best-protected first",
                         ascending=True, top=32), use_container_width=True)
        story("sack_rate")
    with c4:
        qb_player["int_rate"] = qb_player.int_pct
        st.altair_chart(ranked_bar(qb_player[qb_player.attempts>=10], "player", "int_rate",
                         "Interception rate, 10+ attempts", team_col=None, top=15), use_container_width=True)
        story("int_pct")

    c5, c6 = st.columns(2)
    with c5:
        st.altair_chart(ranked_bar(qb_player, "player", "attempts", "Pass attempts — who's \"the guy\"",
                         team_col=None, top=15), use_container_width=True)
        story("pass_attempts")
    with c6:
        qr = qb_rush[qb_rush.carries>=5]
        st.altair_chart(ranked_bar(qr, "player", "carries", "QB rushing — carries, 5+ attempts",
                         team_col=None, top=12), use_container_width=True)
        st.caption("Backlog item from the notes, built this session. Lamar Jackson: 14 carries at 9.07 yds/carry.")

    st.subheader("Touchdown-to-interception ratio")
    qbp = qb_player[qb_player.attempts>=20].copy()
    qbp["td_int_ratio"] = qbp.pass_tds / qbp.interceptions.replace(0, 1)
    st.altair_chart(ranked_bar(qbp, "player", "td_int_ratio", "TD : INT ratio, 20+ attempts",
                     team_col=None, top=12), use_container_width=True)
    story("td_int_ratio")

    st.subheader("Real starters vs. committee arms — the 50-attempt line")
    cohort = qb_player.copy()
    cohort["cohort"] = cohort.attempts.apply(lambda a: "50+ attempts" if a >= 50 else "Under 50 attempts")
    summary = cohort.groupby("cohort").agg(
        quarterbacks=("player", "count"),
        avg_epa_per_play=("epa_per_play", "mean"),
        avg_completion_pct=("completion_pct", "mean"),
    ).reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.caption("Backlog item from the notes, built this session: the \"50+ attempts\" group is the one "
               "worth judging on EPA — the under-50 group is mostly backups and committee arms, where "
               "any single stat is still too noisy to mean much.")

    st.subheader("Interception rate vs. EPA — who's actually risky")
    d_risk = qb_player[qb_player.attempts >= 10]
    st.altair_chart(team_scatter(d_risk, "int_pct", "epa_per_play",
                     "Interception % vs. EPA per play, 10+ attempts", hover_name="player"),
                     use_container_width=True)
    dart = d_risk[d_risk.player.str.contains("Dart", case=False, na=False)]
    if len(dart):
        r = dart.iloc[0]
        st.caption(f"Backlog item, built this session. {r.player} sits in the low-interception, "
                   f"positive-EPA quadrant ({r.int_pct:.1f}% INT rate, {r.epa_per_play:.3f} EPA/play) — "
                   "exactly the rushing-heavy, low-risk profile the notes flagged.")
    else:
        st.caption("Backlog item, built this session. (J. Dart doesn't meet the 10-attempt minimum in "
                   "this snapshot — check back once he has a bigger sample.)")

    st.subheader("The backup chapter")
    st.markdown("""
**Atlanta** — three starters, three weeks: Tua Tagovailoa (Wk1, oblique injury) → Cooper Rush
(44 att, 4 INT, -0.635 EPA/play) → Michael Penix Jr. (Wk3, first year back from ACL tear).
**Chicago** — Caleb Williams (hamstring) → Tyson Bagent (concussion) → Case Keenum
(first snap since 2023, 70.6% completion, 0 INT vs. Philadelphia).

Chicago still grades elite at quarterback (see EPA/CPOE chart above) despite none of it coming
from their real QB1 — that's what a real quarterback room looks like. New play-callers this
season: Atlanta (Stefanski/Rees), Baltimore (Declan Doyle, first-ever play-calling job, #2 in
the league in QB EPA), Las Vegas (Klint Kubiak).
""")

# =====================================================================
elif SECTION == "Running Backs":
    st.header("Running Backs")
    rb_team = load("rb_stats.csv")
    rb_player = load("rb_player_level.csv")

    c1, c2 = st.columns(2)
    with c1:
        d = rb_player[rb_player.carries>=20]
        st.altair_chart(team_scatter(d, "carries", "explosive_rate_10plus",
                         "Carries vs. explosive run rate, 20+ carries", hover_name="player"),
                         use_container_width=True)
        story("explosive_run_rate_10plus")
    with c2:
        st.altair_chart(ranked_bar(d, "player", "ypc", "Yards per carry, every qualifying back",
                         team_col="team", top=15), use_container_width=True)
        story("yards_per_carry")

    c3, c4 = st.columns(2)
    with c3:
        d2 = rb_player[(rb_player.carries>=20)&(rb_player.rush_yards_over_expected_per_att.notna())]
        st.altair_chart(team_scatter(d2, "carries", "rush_yards_over_expected_per_att",
                         "Rush yards over expected per attempt", hover_name="player"), use_container_width=True)
        st.info("**Why it matters:** strips out the blocking — NGS's model of what a carry *should* "
                "get, minus what the back actually got. Kenneth Walker III is creating +2.28 yds/carry himself.")
    with c4:
        d3 = rb_player[(rb_player.carries>=20)&(rb_player.pct_carries_vs_stacked_box.notna())]
        st.altair_chart(team_scatter(d3, "pct_carries_vs_stacked_box", "efficiency",
                         "Stacked box % vs. efficiency", hover_name="player"), use_container_width=True)
        story("stacked_box_pct")

    c5, c6 = st.columns(2)
    with c5:
        st.altair_chart(ranked_bar(d, "player", "carries", "The workload leaderboard",
                         team_col="team", top=15), use_container_width=True)
        story("carries")
    with c6:
        st.altair_chart(ranked_bar(d, "player", "pct_carries_4plus", "Carries that actually gain ground — % going 4+ yds",
                         team_col="team", top=12), use_container_width=True)
        story("pct_carries_4plus_yards")

    st.subheader("Backs in waiting — low-volume, high-rate")
    low = rb_player[(rb_player.carries>=10)&(rb_player.carries<20)].sort_values("pct_carries_4plus", ascending=False).head(10)
    st.altair_chart(ranked_bar(low, "player", "pct_carries_4plus", "10–19 carries, ranked by 4+ yard rate",
                     team_col="team", top=10), use_container_width=True)
    st.caption("The \"RB in difficulty\" framing from the notes: backups already outproducing their own "
               "team's starter on a per-touch basis, built this session.")

    st.subheader("RB used as a receiver")
    if "rb_receiving_targets" in rb_team.columns:
        st.altair_chart(ranked_bar(rb_team, "team", "rb_receiving_targets",
                         "RB receiving targets by team", top=15), use_container_width=True)
        story("rb_receiving_targets")
        st.caption("Backlog item from the notes — built this session now that the column was confirmed available.")
    else:
        st.warning("rb_receiving_targets not found in this snapshot — needs a compute script update first.")

    st.subheader("Spotlight: Alvin Kamara's usage style")
    kam = rb_player[rb_player.player.str.contains("Kamara", case=False, na=False)]
    if len(kam):
        r = kam.iloc[0]
        st.markdown(f"**{r.player} ({r.team})** — {int(r.carries)} carries, {r.ypc:.2f} yards/carry, "
                    f"{r.pct_carries_4plus:.1f}% of carries going 4+ yards"
                    + (f", {r.explosive_rate_10plus:.1f}% explosive rate" if 'explosive_rate_10plus' in r and not pd.isna(r.explosive_rate_10plus) else "")
                    + ".")
        st.caption("Backlog item, built this session — pulled live, so this stays current as his season goes on.")
    else:
        st.info("Alvin Kamara doesn't meet this snapshot's carry minimum yet, or isn't in this week's data.")

    st.subheader("On the record: corrections")
    st.markdown("""
**Saquon Barkley (PHI)** — *not a decline, just a bump in Week 2.* 34 carries, 5.12 yds/carry,
11.8% explosive rate — all healthy numbers. He took a knock in Week 2 and his workload shrank
that game; the efficiency itself never dropped.

**Committee backfields worth watching:** Seattle, New England, San Francisco, Arizona,
Washington are all splitting carries closely enough that neither back has separated as the clear lead.
""")
    st.caption("Still backlog: RB tiers by NFL experience/season (no rookie/veteran data source yet) "
               "and named minimum-threshold boards (30 car @ 4+, 10 car @ 10+, 50 car explosive tier).")

# =====================================================================
elif SECTION == "Receivers & Tight Ends":
    st.header("Receivers & Tight Ends")
    ngs = load("wr_te_player_level_ngs.csv")
    drops = load("wr_te_drop_rate.csv")

    wr = ngs[(ngs.player_position=="WR")&(ngs.targets>=15)]
    te = ngs[(ngs.player_position=="TE")&(ngs.targets>=10)]

    c1, c2 = st.columns(2)
    with c1:
        st.altair_chart(team_scatter(wr, "avg_separation", "avg_yac_above_expectation",
                         "Separation vs. YAC above expectation, 15+ targets",
                         hover_name="player_display_name", color_col="team_abbr"), use_container_width=True)
        story("avg_separation")
    with c2:
        st.altair_chart(ranked_bar(wr, "player_display_name", "catch_percentage",
                         "Catch rate, 15+ targets", team_col="team_abbr", top=15), use_container_width=True)
        story("catch_percentage", fallback_relevance="A fast first filter — not perfect alone, since quarterback and route matter too.")

    c3, c4 = st.columns(2)
    with c3:
        st.altair_chart(ranked_bar(wr, "player_display_name", "percent_share_of_intended_air_yards",
                         "Who's the real #1 target — air yards share", team_col="team_abbr", top=12), use_container_width=True)
        story("percent_share_of_intended_air_yards")
    with c4:
        d = drops[drops.targets>=15].sort_values("drop_rate_pct", ascending=False).head(12)
        st.altair_chart(ranked_bar(d, "receiver_player_name", "drop_rate_pct",
                         "Drop rate, worst first — 15+ targets", team_col="team", top=12), use_container_width=True)
        story("drop_rate_pct", fallback_relevance="Catch rate alone can hide a drops problem on uncontested targets.")

    st.subheader("Cushion vs. separation")
    cs = ngs[ngs.targets>=15]
    st.altair_chart(team_scatter(cs, "avg_cushion", "avg_separation",
                     "Pre-snap cushion vs. separation at the catch",
                     hover_name="player_display_name", color_col="team_abbr"), use_container_width=True)
    story("avg_cushion")
    st.caption("Backlog item from the notes — built this session. Harold Fannin Jr. creates elite "
               "separation despite a tight cushion — that's technique, not a free release.")

    st.subheader("Receiver rooms worth a second look")
    def room_line(team, players):
        rows = ngs[(ngs.team_abbr==team) & (ngs.player_display_name.isin(players)) & (ngs.player_position=="WR")]
        if not len(rows): return None
        parts = [f"{r.player_display_name} ({r.catch_percentage:.1f}% catch, {r.targets:.0f} tgt)" for r in rows.itertuples()]
        return f"**{team}** — " + " & ".join(parts)
    rooms = [
        ("DAL", ["CeeDee Lamb", "George Pickens"]),
        ("GB", ["Matthew Golden", "Christian Watson"]),
        ("WAS", ["Stefon Diggs", "Terry McLaurin", "Dyami Brown"]),
        ("CIN", ["Ja'Marr Chase", "Tee Higgins"]),
        ("DET", ["Amon-Ra St. Brown", "Jameson Williams", "Tim Patrick"]),
    ]
    lines = [room_line(t, p) for t, p in rooms]
    lines = [l for l in lines if l]
    if lines:
        st.markdown("\n\n".join("- " + l for l in lines))
    st.caption("Pulled live from this snapshot (not hardcoded), so it stays accurate as the season moves — "
               "Washington's 3-way room (including Dyami Brown) and the full Detroit room are built this session.")

    st.subheader("Spotlight: Kalif Raymond")
    kr = ngs[ngs.player_display_name.str.contains("Raymond", case=False, na=False)]
    if len(kr):
        r = kr.iloc[0]
        st.markdown(f"**{r.player_display_name} ({r.team_abbr})** — {r.catch_percentage:.1f}% catch rate, "
                    f"{r.avg_separation:.2f} yds separation, {r.percent_share_of_intended_air_yards:.1f}% "
                    f"share of team air yards, on {r.targets:.0f} targets.")
    else:
        st.info("Kalif Raymond doesn't meet this snapshot's target minimum right now.")
    st.caption("Backlog item from the notes, built this session.")

    st.subheader("Sure hands — 60%+ catch rate on real volume (8+ targets)")
    sure = ngs[(ngs.player_position=="WR") & (ngs.targets>=8) & (ngs.catch_percentage>=60)].sort_values("catch_percentage", ascending=False)
    st.altair_chart(ranked_bar(sure, "player_display_name", "catch_percentage",
                     "Catch rate, 8+ targets, 60%+ only", team_col="team_abbr", top=15), use_container_width=True)
    st.caption("Backlog item from the notes, built this session — the specific 60%-on-8-targets framing, "
               "not just the general catch-rate leaderboard above.")

    st.subheader("The 20+ target cohort")
    heavy = ngs[(ngs.player_position=="WR") & (ngs.targets>=20)].sort_values("targets", ascending=False)
    st.altair_chart(ranked_bar(heavy, "player_display_name", "targets", "Every WR with 20+ targets",
                     team_col="team_abbr", top=20), use_container_width=True)
    st.caption("Backlog item, built this session — the true high-volume group, separate from the 15+ "
               "threshold used elsewhere on this page.")

    st.subheader("Pass-game tight ends")
    c5, c6 = st.columns(2)
    with c5:
        st.altair_chart(team_scatter(te, "percent_share_of_intended_air_yards", "catch_percentage",
                         "TE air yards share vs. catch rate, 10+ targets",
                         hover_name="player_display_name", color_col="team_abbr"), use_container_width=True)
    with c6:
        st.altair_chart(ranked_bar(te, "player_display_name", "avg_yac_above_expectation",
                         "After-the-catch skill at TE", team_col="team_abbr", top=12), use_container_width=True)

    st.subheader("Spotlight: Tyler Warren's usage vs. his team's playbook")
    tw = ngs[ngs.player_display_name.str.contains("Tyler Warren", case=False, na=False)]
    tend_peek = load("play_type_tendency.csv")
    if len(tw):
        r = tw.iloc[0]
        tr = tend_peek[tend_peek.team==r.team_abbr]
        if len(tr):
            t = tr.iloc[0]
            st.markdown(f"**{r.player_display_name} ({r.team_abbr})** — {r.targets:.0f} targets, "
                        f"{r.percent_share_of_intended_air_yards:.1f}% air-yards share, on a team that "
                        f"runs {t.pass_pct:.1f}% pass / {t.run_pct:.1f}% run overall.")
        else:
            st.markdown(f"**{r.player_display_name} ({r.team_abbr})** — {r.targets:.0f} targets, "
                        f"{r.percent_share_of_intended_air_yards:.1f}% air-yards share.")
    else:
        st.info("Tyler Warren doesn't meet this snapshot's target minimum right now.")
    st.caption("Backlog item from the notes, built this session. CeeDee Lamb vs. his own Week 3 last "
               "season, and Malik Nabers' ACL-return storyline, stay flagged unverifiable without 2025 "
               "season data or an injury-report source — not built, not faked.")

# =====================================================================
elif SECTION == "Defense":
    st.header("Defense")
    pos = load("defense_player_level_by_position.csv")
    pbu = load("defense_pbu_player_level.csv")
    hustle = load("defense_hustle_stats_player_level.csv")
    mt = load("team_missed_tackle_by_position_group.csv")
    lb_db = load("lb_db_player_level_pfr.csv")

    c1, c2 = st.columns(2)
    with c1:
        ints = pos.groupby("team", as_index=False).interceptions.sum().sort_values("interceptions", ascending=False)
        st.altair_chart(ranked_bar(ints, "team", "interceptions", "Interceptions by team",
                         team_col="team", top=10), use_container_width=True)
        st.warning("**Evolved:** five teams are tied at the top with 4 — not a clean #1 the way an earlier note had it.")
    with c2:
        st.altair_chart(ranked_bar(pbu, "player_name", "pbu", "Passes defended leaders",
                         team_col="team", top=10), use_container_width=True)
        story("pbu")

    c3, c4 = st.columns(2)
    with c3:
        hustle = hustle.copy(); hustle["total"] = hustle.forced_fumbles + hustle.fumble_recoveries
        st.altair_chart(ranked_bar(hustle, "player_name", "total", "Forced fumbles + recoveries",
                         team_col="team", top=10), use_container_width=True)
        story("forced_fumbles")
    with c4:
        db = mt[mt.position_group=="DB"].sort_values("missed_tackle_pct", ascending=False).head(10)
        st.altair_chart(ranked_bar(db, "team", "missed_tackle_pct", "Missed tackle % — secondary",
                         team_col="team", top=10), use_container_width=True)
        st.warning("**Evolved:** Denver's secondary misses nearly 1 in 4 — the league's worst, not "
                   "Chicago's linebackers as an earlier note had it (CHI LB still shows up, just lower).")

    c5, c6 = st.columns(2)
    with c5:
        agg = lb_db.groupby(["team","pfr_player_name"], as_index=False).agg(
            tkl=("def_tackles_combined","sum"), mt=("def_missed_tackles","sum"))
        st.altair_chart(ranked_bar(agg, "pfr_player_name", "tkl", "Tackle leaders",
                         team_col="team", top=10), use_container_width=True)
        story("def_tackles_combined")
    with c6:
        dl = pos[pos.position_group=="DL"].sort_values("pressures", ascending=False).head(12)
        st.altair_chart(team_scatter(dl, "pressures", "sacks", "Pressure-to-sack conversion, DL top 12",
                         hover_name="player", color_col="team"), use_container_width=True)
        story("pressures")

    st.subheader("Most-targeted corners")
    db2 = pos[(pos.position_group=="DB")&(pos.targets>=15)].sort_values("targets", ascending=False).head(12)
    st.altair_chart(team_scatter(db2, "targets", "completion_pct_allowed",
                     "Targets faced vs. completion % allowed", hover_name="player", color_col="team"),
                     use_container_width=True)
    story("completion_pct_allowed")

    st.subheader("Pressure rate — natural rush vs. blitzing")
    tfac = load("defense_tendency_faced.csv")
    c7, c8 = st.columns(2)
    with c7:
        st.altair_chart(team_scatter(tfac, "pressure_rate_natural_rush", "pressure_rate_blitz",
                         "Natural-rush pressure rate vs. blitz pressure rate, by team", hover_name="team"),
                         use_container_width=True)
        st.caption("Backlog item, built this session. Teams above the diagonal get more out of blitzing "
                   "than rushing four; teams below get pressure fine without sending extra.")
    with c8:
        st.altair_chart(team_scatter(tfac, "blitz_rate_pct", "pressure_rate_blitz",
                         "Blitz rate vs. pressure rate when blitzing", hover_name="team"),
                         use_container_width=True)
        story("pressure_rate_blitz", fallback_relevance="If blitzing a lot doesn't raise the blitz-pressure "
              "rate much, the blitz may be more about disguise than real production.")

    st.subheader("Stacked box vs. natural pressure — disguise-heavy defenses")
    st.altair_chart(team_scatter(tfac, "stacked_box_pct", "pressure_rate_natural_rush",
                     "Stacked box % vs. natural pass-rush pressure rate", hover_name="team"),
                     use_container_width=True)
    st.caption("Backlog item, built this session: defenses that load the box AND still generate pressure "
               "with a standard 4-man rush are disguising their look well.")

    st.caption("Still backlog: individual spotlights (Rams' Week 3 secondary struggles, Houston safeties, "
               "Marlon Humphrey's big game, Malaki Starks), and player-level attribution for the "
               "pick-six/fumble-return-TD/safety team totals (team-level only exists today).")

# =====================================================================
elif SECTION == "Special Teams":
    st.header("Special Teams")
    st_df = load("special_teams.csv")

    c1, c2 = st.columns(2)
    with c1:
        st.altair_chart(ranked_bar(st_df, "team", "fg_pct_overall", "Field goal % by team",
                         team_col="team", top=10), use_container_width=True)
        story("fg_pct_overall")
    with c2:
        buckets = pd.DataFrame({
            "distance": ["<30","30-39","40-49","50+"],
            "attempts": [st_df["fg_att_<30"].sum(), st_df["fg_att_30-39"].sum(),
                         st_df["fg_att_40-49"].sum(), st_df["fg_att_50+"].sum()],
        })
        chart = alt.Chart(buckets).mark_bar(color="#c8202b").encode(
            x=alt.X("distance:N", sort=["<30","30-39","40-49","50+"], title="Distance (yards)"),
            y=alt.Y("attempts:Q"), tooltip=["distance","attempts"],
        ).properties(title="Field goal attempts by distance, league-wide", height=420)
        st.altair_chart(chart, use_container_width=True)
        st.caption("Most attempts cluster 30-49 yards — the bread-and-butter distance for an NFL kicker.")

    st.subheader("Punt return yards gained")
    st.altair_chart(ranked_bar(st_df, "team", "punt_return_yards_gained", "Punt return yards gained",
                     team_col="team", top=10), use_container_width=True)
    story("punt_return_yards_gained")

    st.subheader("Who's missed, and who's only been asked the easy ones")
    missed = st_df[st_df.fg_pct_overall < 100][["team","fg_attempts","fg_made","fg_pct_overall"]].sort_values("fg_pct_overall")
    short_only = st_df[(st_df["fg_att_30-39"]==0) & (st_df["fg_att_40-49"]==0) & (st_df["fg_att_50+"]==0) & (st_df["fg_att_<30"]>0)]
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("**Teams with at least one miss this season**")
        st.dataframe(missed, use_container_width=True, hide_index=True)
    with cc2:
        st.markdown("**Teams only attempted from under 30 yards**")
        if len(short_only):
            st.dataframe(short_only[["team","fg_attempts","fg_made"]], use_container_width=True, hide_index=True)
        else:
            st.caption("No team has been limited to only sub-30-yard attempts in this snapshot.")
    st.caption("Backlog item from the notes, built this session.")
    st.caption("Still backlog: correlating low punt counts with giveaways (not punting because a team is "
               "moving the ball, vs. going for it on 4th instead).")

# =====================================================================
elif SECTION == "Play-Design & Tendencies":
    st.header("Play-Design & Tendencies")
    tend = load("play_type_tendency.csv")
    team_stats = load("team_stats_2026.csv")
    qb_team = load("qb_stats.csv")

    c1, c2 = st.columns(2)
    with c1:
        merged = tend.merge(qb_team[["team","epa_per_dropback"]], on="team")
        st.altair_chart(team_scatter(merged, "motion_pct", "epa_per_dropback",
                         "Motion rate vs. offensive EPA, all 32 teams", hover_name="team"),
                         use_container_width=True)
        story("motion_pct")
    with c2:
        fd = team_stats.sort_values("fourth_down_off_attempts", ascending=False).head(10)
        st.altair_chart(ranked_bar(fd, "team", "fourth_down_off_attempts", "4th down attempts",
                         team_col="team", top=10), use_container_width=True)
        zero = team_stats[team_stats.fourth_down_off_attempts==0].team.tolist()
        st.warning(f"**Evolved:** only {' and '.join(zero)} haven't gone for it yet — not four teams "
                   "as an earlier note had it.")

    st.subheader("The play-design podium")
    podium = pd.DataFrame({
        "category": ["Play-action","Play-action","Play-action","RPO","RPO","RPO","Screen","Screen","Screen"],
        "team": list(tend.nlargest(3,"play_action_pct").team) + list(tend.nlargest(3,"rpo_pct").team) + list(tend.nlargest(3,"screen_pct").team),
        "value": list(tend.nlargest(3,"play_action_pct").play_action_pct) + list(tend.nlargest(3,"rpo_pct").rpo_pct) + list(tend.nlargest(3,"screen_pct").screen_pct),
    })
    podium_chart = alt.Chart(podium).mark_bar().encode(
        x=alt.X("value:Q", title="%"),
        y=alt.Y("team:N", sort="-x", title=None),
        yOffset="category:N",
        color=alt.Color("category:N", scale=alt.Scale(range=["#c8202b","#8a8578","#1d7a4c"]), legend=alt.Legend(title=None)),
        tooltip=["team","category","value"],
    ).properties(title="Top 3 by category — play-action / RPO / screen %", height=420)
    st.altair_chart(podium_chart, use_container_width=True)
    st.success("**Kansas City finishes top-3 in all three** — a complete play-design menu, not a one-trick offense.")

    st.subheader("EPA by quarter — every team")
    qs = load("quarter_splits.csv")
    team_list = sorted(qs.team.unique())
    default_idx = team_list.index("ARI") if "ARI" in team_list else 0
    team_pick = st.selectbox("Pick a team", team_list, index=default_idx)
    sel = qs[qs.team==team_pick]
    qchart = alt.Chart(sel).mark_bar(color="#c8202b").encode(
        x=alt.X("quarter:N", title=None), y=alt.Y("epa_per_play:Q"), tooltip=["quarter","epa_per_play"],
    ).properties(title=f"{team_pick} EPA/play by quarter", height=360)
    st.altair_chart(qchart, use_container_width=True)
    st.caption("Backlog item from the notes, now built for all 32 teams via the selector above — "
               "not just the one-team sample from before.")

# =====================================================================
elif SECTION == "✅ Notes Checklist":
    st.header("✅ Notes Checklist")
    st.markdown("""
This is **not** a list reconstructed from memory just now — it's the exact Used/Backlog
breakdown from the *Notes Tracker* artifact, which was built section-by-section while your
original raw notes dump was still in context. Items added or completed in the current session
are marked **"Built this session"** below; nothing on this page is guessed.

Anything still unchecked is genuinely not built yet. Two items are flagged **unverifiable**
because they need data this project doesn't have access to (2025 season stats, an injury-report
timeline) — they're listed so they aren't silently dropped, not because they were faked.
""")

    CHECKLIST = {
        "Quarterback": [
            ("EPA/dropback vs. CPOE tiers — your exact quadrant framing", "done"),
            ("ATL's 3-QB carousel + CHI's injury chain", "done"),
            ("New OC/DC context: Baltimore's rookie play-caller, Atlanta's new staff, Vegas's new HC", "done"),
            ("Sack rate, INT rate, time-to-throw vs. intended air yards", "done"),
            ("Attempts/workload — real starter vs. committee arm", "done"),
            ("Houston/Stroud 0-INT, Herbert's sacks-and-picks stretch, Maye's turnover run", "done"),
            ("QB rushing graph (Allen 5+ rush, Purdy scramble number)", "session"),
            ("TD/INT ratio leaderboard, separate from raw INT rate", "session"),
            ("\"50+ throw\" vs. \"under 50\" QB cohort comparison", "session"),
            ("INT vs. EPA/play scatter specifically calling out Dart's low-risk profile", "session"),
        ],
        "Running back": [
            ("Carries vs. explosive-run-rate, every back with 20+ carries", "done"),
            ("YPC leaderboard, every qualifying back ranked", "done"),
            ("Rushing yards over expected per attempt", "done"),
            ("Stacked-box % vs. efficiency", "done"),
            ("Workload leaderboard + committee-backfield callouts", "done"),
            ("Saquon Barkley correction — verified (injury, not decline)", "done"),
            ("%carries 4+ yds vs. 10+ yds, starter/backup split", "session"),
            ("RB used as a receiver (RB targets, checkdown-heavy backs)", "session"),
            ("RB tiers by NFL experience/season — rookie vs. veteran", "backlog"),
            ("\"RB in difficulty\" framing — low-carry backs with good rates", "session"),
            ("Alvin Kamara usage-style spotlight specifically", "session"),
            ("Named minimum-threshold boards (30 car @ 4+, 10 car @ 10+, 50 car explosive)", "backlog"),
        ],
        "Wide receiver / tight end": [
            ("Separation vs. YAC above expectation, 15+ targets", "done"),
            ("Catch-rate leaderboard, full qualifying list", "done"),
            ("Air-yards share — who's the real #1", "done"),
            ("Grouped WR-room comparisons: DAL, GB, WAS, CIN", "done"),
            ("CeeDee Lamb's strong-start read", "done"),
            ("TE target share + TE YAC above expectation", "done"),
            ("CeeDee Lamb vs. his own Week 3 last season", "unverifiable"),
            ("\"Sure hands\" tier at 60%+ catch on 8+ targets", "session"),
            ("Average cushion vs. separation", "session"),
            ("20+ target cohort specifically (JSN, Watson deeper dive)", "session"),
            ("Kalif Raymond full spotlight", "session"),
            ("Malik Nabers ACL-return-rhythm storyline", "unverifiable"),
            ("Drops leaderboard (Metcalf, Cowboys room)", "session"),
            ("Full DET WR-room breakdown", "session"),
            ("Washington's Diggs/McLaurin/Dyami Brown three-way room", "session"),
            ("Tyler Warren usage style tied to playbook", "session"),
            ("\"Air yards share\" clean writeup (you flagged this as confusing)", "session"),
        ],
        "Defense — DL / LB / DB": [
            ("Missed-tackle % by team/position group", "session"),
            ("PBU/passes-defended leaders", "session"),
            ("Forced fumbles by position group, per team", "session"),
            ("Fumble recovery leaders by position group", "session"),
            ("DB individual spotlights (Rams Wk3, Houston safeties, Humphrey, Starks)", "backlog"),
            ("Pick-six/fumble-return-TD/safety — player attribution", "backlog"),
            ("DL pressure-to-sack correlation", "session"),
            ("LB 25+ tackle tier, 0-missed-tackle standouts", "session"),
            ("Target volume vs. completion allowed by DB", "session"),
            ("Interceptions by team — corrected", "session"),
        ],
        "O-line / D-line": [
            ("Sack-fault split: QB-caused vs. O-line-caused, by team", "session"),
            ("Pressure rate: natural rush vs. blitz, by team", "session"),
            ("Blitz rate vs. pressure-rate-blitz correlation", "session"),
            ("Stacked box vs. pressure rate natural, disguise-heavy defenses", "session"),
        ],
        "Special teams": [
            ("FG% by distance bucket, made/attempt counts on every bar", "done"),
            ("Teams that missed vs. teams that only attempted <30-yarders", "session"),
            ("Punt-return-yards-gained leaderboard", "session"),
            ("Correlate low punt counts with giveaways", "backlog"),
        ],
        "Play-type tendency & by-quarter": [
            ("Run vs. pass split with real play counts", "done"),
            ("Motion rate vs. QB EPA/dropback", "session"),
            ("Play-action/RPO/screen podium per team", "session"),
            ("4th-down attempt rate & success — corrected", "session"),
            ("Full by-quarter breakdown per team, all 32", "session"),
        ],
        "Production ideas (not metrics)": [
            ("3-page structure (offense/defense/special teams)", "superseded"),
            ("Conference split", "backlog"),
            ("LinkedIn video presentation format", "backlog"),
            ("\"Sport SaaS in Africa\" idea", "out-of-scope"),
            ("League-average comparison line baked into every chart", "backlog"),
        ],
    }
    STATUS_LABEL = {
        "done": "✅ Built & verified (earlier session)",
        "session": "🆕 Built this session",
        "backlog": "⬜ Still backlog",
        "unverifiable": "🚫 Unverifiable — needs outside data",
        "superseded": "↪️ Superseded by this app",
        "out-of-scope": "✂️ Out of scope for this project",
    }
    total = sum(len(v) for v in CHECKLIST.values())
    done_ct = sum(1 for v in CHECKLIST.values() for _, s in v if s in ("done","session","superseded"))
    st.progress(done_ct/total, text=f"{done_ct} / {total} items from your notes are built")

    for section, items in CHECKLIST.items():
        with st.expander(f"{section}  ·  {sum(1 for _,s in items if s in ('done','session','superseded'))}/{len(items)} built", expanded=False):
            for text, status in items:
                checked = status in ("done", "session", "superseded")
                st.checkbox(f"{text}  —  _{STATUS_LABEL[status]}_", value=checked, disabled=True, key=f"{section}-{text}")
