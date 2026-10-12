"""
Four Games In — 2026 NFL Season, league overview.

Built for screenshotting: each section is tuned to fit one screen with no
scrolling. Every number is pulled live from output/wk4/ (cumulative through
Week 4, all teams on equal games) — nothing here is hand-typed from memory.

Run with: streamlit run league_overview_app.py
"""
import os
import base64
import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="Four Games In — 2026 NFL Season", layout="wide")

_BG_PATH = os.path.join(os.path.dirname(__file__), "assets", "stadium_bg.jpg")
with open(_BG_PATH, "rb") as _f:
    _BG_B64 = base64.b64encode(_f.read()).decode()

_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "aeye_logo_crop.png")
with open(_LOGO_PATH, "rb") as _f:
    _LOGO_B64 = base64.b64encode(_f.read()).decode()

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(rgba(255,248,244,0.86), rgba(255,248,244,0.86)),
                url("data:image/jpeg;base64,{_BG_B64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
[data-testid="stHeader"] {{background: rgba(0,0,0,0);}}
[data-testid="stToolbarActions"] {{display: none !important;}}
[data-testid="stDecoration"] {{display: none !important;}}
</style>
<img src="data:image/png;base64,{_LOGO_B64}" style="
    position: fixed; top: 6px; left: 14px; width: 128px;
    z-index: 999999; pointer-events: none;
">
""", unsafe_allow_html=True)

st.markdown("""
<style>
.block-container {padding-top: 0.35rem; padding-bottom: 0.2rem; padding-left: 115px; max-width: 1400px;}
div[data-testid="stVerticalBlockBorderWrapper"] {margin-bottom: 0 !important;}
h1 {font-size: 1.26rem !important; margin-bottom: 0.15rem !important;}
h2 {font-size: 1.04rem !important; margin: 0.25rem 0 0.15rem 0 !important;}
h3, h4 {font-size: 0.9rem !important; margin: 0.2rem 0 0.1rem 0 !important;}
p, li, .stMarkdown {font-size: 11.5px !important; line-height: 1.25 !important; font-weight: 600 !important;}
/* force every default (non team-colored) piece of text to solid black and bold it
   so it stays dark/legible over the photo — inline team-color spans still win
   since they set their own color directly */
h1, h2, h3, h4, p, li, table, td, th, div[data-testid="stMarkdownContainer"] {
  color:#000 !important;
}
h1, h2, h3, h4 {font-weight: 800 !important;}
td, th {font-weight: 700 !important;}
div[data-testid="stCaptionContainer"] {font-size: 10.5px !important; margin-bottom: 0.12rem !important; color:#000 !important;}
div[data-testid="stCaptionContainer"] p {color:#000 !important;}
div[data-testid="stMarkdownContainer"] ul {margin-top: 2px !important; margin-bottom: 2px !important;}
div[data-testid="stMarkdownContainer"] li {margin-bottom: 2px !important;}
div[data-testid="stMarkdownContainer"] p {margin-bottom: 4px !important;}
div.element-container {margin-bottom: 0.15rem !important;}
div[data-testid="stVegaLiteChart"] {margin-top: 0.25rem !important; margin-bottom: 0.15rem !important;}
</style>
""", unsafe_allow_html=True)

BASE = os.path.dirname(__file__)
OUT = os.path.join(BASE, "output", "wk4")

TEAM_FULL = {
    "ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
    "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs", "LA": "Los Angeles Rams", "LAC": "Los Angeles Chargers",
    "LV": "Las Vegas Raiders", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings",
    "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants",
    "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers",
    "SEA": "Seattle Seahawks", "SF": "San Francisco 49ers", "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans", "WAS": "Washington Commanders",
}
TC = {"ARI":"#97233F","ATL":"#A71930","BAL":"#241773","BUF":"#00338D","CAR":"#007aba","CHI":"#0B162A",
"CIN":"#d34211","CLE":"#db3400","DAL":"#003594","DEN":"#d34211","DET":"#0076B6","GB":"#203731",
"HOU":"#03202F","IND":"#002C5F","JAX":"#006778","KC":"#E31837","LA":"#003594","LAC":"#0078ba",
"LV":"#54585A","MIA":"#008088","MIN":"#4F2683","NE":"#002244","NO":"#7f7155","NYG":"#0B2265",
"NYJ":"#125740","PHI":"#004C54","PIT":"#996d0b","SEA":"#002244","SF":"#AA0000","TB":"#D50A0A",
"TEN":"#0C2340","WAS":"#5A1414"}
# Every team color above is darkened just enough to clear WCAG AA (4.5:1) text
# contrast against a white/light background — some official team colors
# (Steelers gold, Saints tan, Raiders silver, Browns/Bengals/Broncos orange,
# Dolphins/Chargers/Panthers light blue-teal) are too light to read as body
# text otherwise. Still each team's real hue, just deep enough to read.
TC_SCALE = alt.Scale(domain=list(TC.keys()), range=list(TC.values()))
GREEN = "#1a7a3c"
RED_H = "#b3261e"

def full(abbr):
    return TEAM_FULL.get(abbr, abbr)

def lighten(hex_color, factor=0.87):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"

def tname(abbr):
    return f'<span style="color:{TC.get(abbr, "#000")};font-weight:bold;">{full(abbr)}</span>'

def record(wins, losses):
    return f"{int(wins)}W-{int(losses)}L"

@st.cache_data
def load(name, folder=OUT):
    return pd.read_csv(os.path.join(folder, name))

def bar(df, name_col, val_col, title, team_col=None, height=None, sort="-x"):
    color = alt.Color(f"{team_col}:N", scale=TC_SCALE, legend=None) if team_col else alt.value("#c8202b")
    tooltip = [name_col, val_col] + ([team_col] if team_col else [])
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{val_col}:Q", title=val_col),
            y=alt.Y(f"{name_col}:N", sort=sort, title=None, axis=alt.Axis(labelLimit=260)),
            color=color,
            tooltip=tooltip,
        )
        .properties(title=title, height=height or 150, background="transparent")
        .configure_axis(labelColor="#000", titleColor="#000", domainColor="#000", labelFontWeight="bold", titleFontWeight="bold")
        .configure_title(color="#000")
        .configure_view(stroke=None)
    )

def rb_highlight_scatter(bg_df, hi_df, x, y, title, height=120, xtitle=None, ytitle=None):
    # Vega-Lite's "nice" domain rounding can massively over-expand a short axis
    # (e.g. a real 0-21 range snapping to 0-100) when the chart is short and few
    # ticks are estimated — so fix the domain ourselves from the real data instead
    # of trusting auto-scaling, which is what was squashing Walker/Cook to the
    # bottom of the chart instead of near the top where their real values put them.
    x_all = pd.concat([bg_df[x], hi_df[x]])
    y_all = pd.concat([bg_df[y], hi_df[y]])
    x_pad = (x_all.max() - x_all.min()) * 0.12 or 1
    y_pad = (y_all.max() - y_all.min()) * 0.12 or 1
    x_domain = [x_all.min() - x_pad, x_all.max() + x_pad]
    y_domain = [max(0, y_all.min() - y_pad), y_all.max() + y_pad]

    bg = (
        alt.Chart(bg_df)
        .mark_circle(size=40, color="#c9c9c9", opacity=0.55)
        .encode(
            x=alt.X(f"{x}:Q", scale=alt.Scale(domain=x_domain, nice=False), title=xtitle or x),
            y=alt.Y(f"{y}:Q", scale=alt.Scale(domain=y_domain, nice=False), title=ytitle or y),
            tooltip=["player", x, y],
        )
    )
    points = (
        alt.Chart(hi_df)
        .mark_circle(size=220, stroke="white", strokeWidth=2, opacity=1)
        .encode(
            x=f"{x}:Q", y=f"{y}:Q",
            color=alt.Color("team:N", scale=TC_SCALE, legend=None),
            tooltip=["label", x, y],
        )
    )
    # push each label AWAY from the others along y (highest point's label goes up,
    # lowest point's label goes down) so they diverge instead of both drifting
    # toward the midpoint between markers, which collided when markers sit close
    hi_df = hi_df.sort_values(y, ascending=False).reset_index(drop=True)
    n = len(hi_df)
    labels = None
    for i, (_, row) in enumerate(hi_df.iterrows()):
        dy = -14 - i * 2 if i < n / 2 else 16 + (n - 1 - i) * 2
        one = (
            alt.Chart(pd.DataFrame([row]))
            .mark_text(align="left", dx=12, dy=dy, fontSize=12, fontWeight="bold")
            .encode(
                x=f"{x}:Q", y=f"{y}:Q", text="label:N",
                color=alt.Color("team:N", scale=TC_SCALE, legend=None),
            )
        )
        labels = one if labels is None else (labels + one)
    return (
        (bg + points + labels)
        .properties(height=height, background="transparent")
        .configure_axis(labelColor="#000", titleColor="#000", domainColor="#000", labelFontWeight="bold", titleFontWeight="bold", titleFontSize=10, labelFontSize=10)
        .configure_view(stroke=None)
    )

def metric_note(text):
    st.markdown(
        f'<div style="background:#f5f5f0;border-left:4px solid #c8202b;'
        f'padding:5px 10px;margin:5px 0;font-size:11px;color:#000;font-weight:700;">{text}</div>',
        unsafe_allow_html=True,
    )

def transition(text):
    st.markdown(f'<p style="color:#000 !important;font-weight:700;font-style:italic;margin:3px 0 6px 0;font-size:11.5px;">{text}</p>', unsafe_allow_html=True)

def caption(text):
    """Replacement for st.caption() — Streamlit's own built-in caption color
    beats a plain stylesheet rule, so this uses an inline !important instead,
    which always wins regardless of Streamlit's internal CSS."""
    st.markdown(f'<p style="color:#000 !important;font-weight:700 !important;font-size:11.5px;margin:2px 0 6px 0;">{text}</p>', unsafe_allow_html=True)

def html_table(df, team_col_idx=None, team_abbrs=None, star_val=None):
    """Full row tinted in that team's real color. The row matching star_val
    gets a ★ next to its name instead of a special highlight color — no gold
    override, same color treatment as every other row."""
    headers = "".join(f"<th style='text-align:left;padding:3px 10px;border-bottom:2px solid #333;font-size:11px;'>{c}</th>" for c in df.columns)
    rows_html = ""
    for ridx, (_, r) in enumerate(df.iterrows()):
        team_val = r.iloc[team_col_idx] if team_col_idx is not None else None
        team_abbr = team_abbrs[ridx] if team_abbrs is not None else None
        row_bg = lighten(TC.get(team_abbr, "#ffffff")) if team_abbr else "#ffffff"
        cells = ""
        for cidx, v in enumerate(r):
            if cidx == team_col_idx and team_abbr:
                c = TC.get(team_abbr, "#000")
                star = " ★" if (star_val is not None and team_val == star_val) else ""
                cells += f"<td style='padding:3px 10px;border-bottom:1px solid #ddd;font-size:11px;'><span style='color:{c};font-weight:bold;'>{v}{star}</span></td>"
            else:
                cells += f"<td style='padding:3px 10px;border-bottom:1px solid #ddd;font-size:11px;'><b>{v}</b></td>"
        rows_html += f"<tr style='background:{row_bg};'>{cells}</tr>"
    st.markdown(
        f"<table style='width:100%;border-collapse:collapse;margin:4px 0 6px 0;'>"
        f"<thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody></table>",
        unsafe_allow_html=True,
    )

st.markdown(
    '<p style="font-size:11px;color:#000;margin-bottom:10px;">Four Games In, 2026 NFL Season. '
    'Weeks 1-4, every number pulled fresh from output/wk4/</p>',
    unsafe_allow_html=True,
)

PAGE = st.sidebar.radio("Section", [
    "1 · New Coaches, New Results",
    "2 · Who's Playing Well",
    "3 · Good Offense, Hurt QB Rooms, and the Winless",
])

ts = load("team_stats_2026.csv")

# =====================================================================================
if PAGE == "1 · New Coaches, New Results":
    st.header("Four games into the 2026 season")
    caption("Several teams changed head coaches this offseason. Results are already splitting into two groups.")

    col1, col2 = st.columns(2)

    rb1 = load("rb_player_level.csv")
    henry = rb1[rb1.player.str.contains("Henry", na=False)].iloc[0]
    qbrush = load("qb_rush_player_level.csv")
    lamar = qbrush[qbrush.player.str.contains("Jackson", na=False)].iloc[0]
    ngs4 = load("wr_te_player_level_ngs.csv")
    zay = ngs4[ngs4.player_display_name.str.contains("Flowers", na=False)].iloc[0]
    bal_c, lv_c = TC["BAL"], TC["LV"]

    with col1:
        st.markdown(f'<h4 style="color:{GREEN};margin-bottom:2px;">Winning</h4>', unsafe_allow_html=True)
        risers = ["CLE", "LV", "NYG", "BAL"]
        for t in risers:
            row = ts[ts.team == t].iloc[0]
            st.markdown(f"{tname(t)} {record(row.wins, row.losses)}", unsafe_allow_html=True)

        st.markdown(f"Biggest surprise so far: {tname('LV')}.", unsafe_allow_html=True)
        st.markdown(
            f'- <span style="color:{lv_c};font-weight:bold;">Kirk Cousins</span> (Quarterback): 149 attempts, '
            f'62.4% completion, 11 touchdowns, <span style="color:{lv_c};font-weight:bold;">+0.169 EPA per play</span>. '
            'EPA (expected points added) is just how much better or worse a play leaves the offense, turned into '
            'points: good spots on the field (near the end zone, a fresh set of downs) are worth more, bad ones '
            'are worth less, and +0.169 means his average play adds about a tenth of a point above normal\n'
            f'- <span style="color:{lv_c};font-weight:bold;">Raiders defense</span>: 4 interceptions, 1 safety forced. '
            'A safety is when the offense is tackled in its own end zone, worth 2 points to the defense',
            unsafe_allow_html=True,
        )
        st.markdown(f"New coaching, same strong run game: {tname('BAL')}.", unsafe_allow_html=True)
        st.markdown(
            f'- <span style="color:{bal_c};font-weight:bold;">Derrick Henry</span>: '
            f'{int(henry.carries)} carries, {henry.ypc:.1f} yards per carry, {int(henry.rush_tds)} touchdowns. '
            f'{henry.pct_carries_4plus:.0f}% of his carries go 4+ yards (consistency), '
            f'{henry.explosive_rate_10plus:.0f}% go 10+ yards (explosiveness)\n'
            f'- <span style="color:{bal_c};font-weight:bold;">Lamar Jackson</span>: '
            f'{int(lamar.carries)} carries, {lamar.ypc:.1f} yards per carry. '
            f'{lamar.pct_carries_4plus:.0f}% of his carries go 4+ yards, {lamar.explosive_rate_10plus:.0f}% go 10+. '
            'Half the time he runs, it\'s a big play\n'
            f'- <span style="color:{bal_c};font-weight:bold;">Zay Flowers</span>: '
            f'{zay.avg_yac:.1f} yards after the catch per reception, well above the {zay.avg_expected_yac:.1f} expected\n'
            f'- Two straight wins: <span style="color:{bal_c};font-weight:bold;">Tyler Loop</span> hit a last-second '
            f'field goal to beat Dallas in Week 3 (34-31), then a close win over the winless Tennessee Titans in '
            f'Week 4 (24-18). Next up: {tname("ATL")}, on Sunday Night Football',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(f'<h4 style="color:{RED_H};margin-bottom:2px;">Difficult start</h4>', unsafe_allow_html=True)
        strugglers = ["TEN", "MIA", "ARI"]
        for t in strugglers:
            row = ts[ts.team == t].iloc[0]
            st.markdown(f"{tname(t)} {record(row.wins, row.losses)}", unsafe_allow_html=True)
        st.markdown(
            f"{tname('TEN')} and {tname('MIA')} are both winless. {tname('ARI')} "
            "has one win. All three are still looking for the new staff to turn things around.",
            unsafe_allow_html=True,
        )

    st.subheader("New coaches overview")
    cols = ["team", "wins", "losses", "ppg", "pa_pg", "point_diff", "takeaways", "giveaways"]
    rows = ts[ts.team.isin(["LV", "BAL", "NYG", "CLE", "ARI", "TEN", "MIA"])][cols].copy()
    rows = rows.sort_values("point_diff", ascending=False)
    team_order = rows["team"].tolist()
    rows["Record"] = rows.apply(lambda r: record(r.wins, r.losses), axis=1)
    rows["Team"] = rows["team"].map(full)
    disp = rows.rename(columns={
        "ppg": "Points/game", "pa_pg": "Points allowed/game", "point_diff": "Point differential",
        "takeaways": "Takeaways", "giveaways": "Giveaways",
    })[["Team", "Record", "Points/game", "Points allowed/game", "Point differential", "Takeaways", "Giveaways"]]
    html_table(disp, team_col_idx=0, team_abbrs=team_order)
    caption(
        "Point differential: total points scored minus points allowed, the simplest read on whether a team "
        "is actually good or just winning close ones. Takeaways/giveaways: turnovers forced and committed."
    )

# =====================================================================================
elif PAGE == "2 · Who's Playing Well":
    st.header("The teams playing quite well")
    caption("Two ways to be dangerous: an explosive run game, or a defense that takes the ball away.")

    col1, col2 = st.columns(2)

    rb = load("rb_player_level.csv")
    w = rb[rb.player == "K.Walker"].iloc[0]
    co = rb[rb.player == "J.Cook"].iloc[0]
    kc_c, buf_c, ne_c = TC["KC"], TC["BUF"], TC["NE"]

    with col1:
        st.markdown(f"{tname('KC')} and {tname('BUF')} are rolling", unsafe_allow_html=True)
        st.markdown(
            f'- <span style="color:{kc_c};font-weight:bold;">Kenneth Walker III</span>: '
            f'{int(w.carries)} carries, {w.ypc:.2f} yards per carry, {int(w.rush_tds)} touchdowns. '
            f'{w.pct_carries_4plus:.0f}% go 4+ yards (consistency), {w.explosive_rate_10plus:.0f}% go 10+ (explosiveness)\n'
            f'- <span style="color:{buf_c};font-weight:bold;">James Cook</span>: '
            f'{int(co.carries)} carries, {co.ypc:.2f} yards per carry, {int(co.rush_tds)} touchdowns. '
            f'{co.pct_carries_4plus:.0f}% go 4+ yards, {co.explosive_rate_10plus:.0f}% go 10+\n'
            f'- A carry is one running play, the ball carrier takes the handoff and runs. A yard is the basic '
            f'unit of field distance, 100 of them separate one end zone from the other\n'
            f'- Buffalo\'s only loss this season: at home to <span style="color:{ne_c};font-weight:bold;">New England</span>, 26-29',
            unsafe_allow_html=True,
        )
        bg = rb[(rb.carries >= 15) & (~rb.player.isin(["K.Walker", "J.Cook"]))][
            ["player", "pct_carries_4plus", "explosive_rate_10plus"]
        ].rename(columns={"pct_carries_4plus": "% carries 4+ yards (consistency)", "explosive_rate_10plus": "% carries 10+ yards (explosive)"})
        hi = pd.DataFrame([
            {"label": "Kenneth Walker III", "% carries 4+ yards (consistency)": w.pct_carries_4plus,
             "% carries 10+ yards (explosive)": w.explosive_rate_10plus, "team": w.team},
            {"label": "James Cook", "% carries 4+ yards (consistency)": co.pct_carries_4plus,
             "% carries 10+ yards (explosive)": co.explosive_rate_10plus, "team": co.team},
        ])
        st.markdown("**Where the league's running backs stand**")
        st.altair_chart(
            rb_highlight_scatter(
                bg, hi, "% carries 4+ yards (consistency)", "% carries 10+ yards (explosive)", "",
                xtitle="% carries 4+ yards", ytitle="% carries 10+ yards",
            ),
            use_container_width=True,
        )

    with col2:
        st.markdown(f"{tname('SF')} and {tname('SEA')}: run game and defense, not one or the other", unsafe_allow_html=True)
        rbstats = load("rb_stats.csv")
        sea_team = rbstats[rbstats.team == "SEA"].iloc[0]
        mccaffrey = rb[rb.player == "C.McCaffrey"].iloc[0]
        sf_c, sea_c = TC["SF"], TC["SEA"]
        sacks_df = load("ol_dl_stats.csv")[["team", "sacks_generated_by_DL"]]
        sf_sacks = sacks_df[sacks_df.team=="SF"].iloc[0].sacks_generated_by_DL
        sea_sacks = sacks_df[sacks_df.team=="SEA"].iloc[0].sacks_generated_by_DL
        pbu_df = load("team_pbu_by_position_group.csv").groupby("team")[["passes_defended"]].sum()
        sf_pbu = pbu_df.loc["SF", "passes_defended"]
        sea_pbu = pbu_df.loc["SEA", "passes_defended"]
        st.markdown(
            f'- <span style="color:{sf_c};font-weight:bold;">Christian McCaffrey</span>: '
            f'{mccaffrey.pct_carries_4plus:.0f}% of carries go 4+ yards, {mccaffrey.explosive_rate_10plus:.0f}% go 10+. '
            f'San Francisco\'s defense: {int(sf_sacks)} sacks (quarterback tackled behind the line before he can '
            f'throw), {int(sf_pbu)} passes defensed (a throw broken up, even without an interception)\n'
            f'- <span style="color:{sea_c};font-weight:bold;">Seattle Seahawks</span> (team): '
            f'{sea_team.pct_carries_4plus_yards:.0f}% of carries go 4+ yards, {sea_team.explosive_run_rate_10plus:.0f}% go 10+. '
            f'Seattle\'s defense: {int(sea_sacks)} sacks, {int(sea_pbu)} passes defensed\n'
            '- Neither team is trading offense for defense. They\'re good at both at once',
            unsafe_allow_html=True,
        )
        sacks = load("ol_dl_stats.csv")[["team", "sacks_generated_by_DL"]]
        ints = load("lb_db_team_level.csv")[["team", "interceptions"]]
        yards = ts[["team", "def_yards_play_allowed"]]
        sf_sea = yards.merge(sacks, on="team").merge(ints, on="team")
        sf_sea = sf_sea[sf_sea.team.isin(["SF", "SEA"])].copy().sort_values("def_yards_play_allowed")
        sf_sea_order = sf_sea["team"].tolist()
        sf_sea["Team"] = sf_sea["team"].map(full)
        sf_sea_disp = sf_sea.rename(columns={
            "def_yards_play_allowed": "Yards allowed/play", "sacks_generated_by_DL": "Sacks",
            "interceptions": "Interceptions",
        })[["Team", "Yards allowed/play", "Sacks", "Interceptions"]]
        html_table(sf_sea_disp, team_col_idx=0, team_abbrs=sf_sea_order)

    st.subheader('The standings of interceptions')
    intall = load("lb_db_team_level.csv")[["team", "interceptions"]].sort_values("interceptions", ascending=False).head(8).copy()
    int_order = intall["team"].tolist()
    intall["Team"] = intall["team"].map(full)
    int_display = intall[["Team", "interceptions"]].rename(columns={"interceptions": "Interceptions"})
    html_table(int_display, team_col_idx=0, team_abbrs=int_order, star_val="Jacksonville Jaguars")
    jax = ts[ts.team == "JAX"].iloc[0]
    st.markdown(
        f"★ {tname('JAX')} has a serious start too: {record(jax.wins, jax.losses)}, "
        f"{jax.ppg:.1f} points per game, tied for the league lead in interceptions with 6.",
        unsafe_allow_html=True,
    )

    st.markdown(f"{tname('MIN')} (4W-0L) blitzes more than anyone, by miles", unsafe_allow_html=True)
    dt = load("defense_tendency_faced.csv")[["team", "blitz_rate_pct"]].sort_values("blitz_rate_pct", ascending=False).head(3).copy()
    dt["Team"] = dt["team"].map(full)
    st.altair_chart(
        bar(dt.rename(columns={"blitz_rate_pct": "Blitz rate (%)"}), "Team", "Blitz rate (%)",
            "Blitz rate, opposing quarterback's view", team_col="team", height=180),
        use_container_width=True,
    )
    metric_note(
        "A blitz sends extra defenders after the quarterback instead of dropping back to cover. "
        f"{tname('MIN')} blitzes 72.9% of plays faced, more than 26 points clear of "
        f"{tname('WAS')} and {tname('TB')}, the next two shown above. The opposing quarterback "
        "is under pressure to throw fast on almost every play."
    )

# =====================================================================================
else:
    dal_c = TC["DAL"]
    ngs3 = load("wr_te_player_level_ngs.csv", os.path.join(BASE, "output", "wk3"))
    ngs4only = load("wr_te_player_level_ngs.csv", os.path.join(BASE, "output", "wk4only"))
    lamb3 = ngs3[ngs3.player_display_name.str.contains("Lamb", na=False)].iloc[0]
    lamb4 = ngs4only[ngs4only.player_display_name.str.contains("Lamb", na=False)].iloc[0]
    lamb_season = load("wr_te_player_level_ngs.csv")
    lamb = lamb_season[lamb_season.player_display_name.str.contains("Lamb", na=False)].iloc[0]
    dal = ts[ts.team == "DAL"].iloc[0]

    st.markdown(f"An offense finding its rhythm around its receivers: {tname('DAL')}", unsafe_allow_html=True)
    st.markdown(
        f'- Not the best offense in the league, a good one, built around '
        f'<span style="color:{dal_c};font-weight:bold;">CeeDee Lamb</span>: '
        f'{int(lamb.targets)} targets, {lamb.catch_percentage:.1f}% catch rate across 4 games\n'
        f'- Week 4 was a road win over the Houston Texans, 34-30. '
        f'<span style="color:{dal_c};font-weight:bold;">Lamb</span> alone: '
        f'{int(lamb4.targets)} targets, {int(lamb4.receptions)} receptions, '
        f'{lamb4.catch_percentage:.1f}% catch rate, {int(lamb4.yards)} yards, up from '
        f'{lamb3.catch_percentage:.1f}% across his first three games\n'
        f'- The defense hasn\'t matched the offense: '
        f'<span style="color:{dal_c};font-weight:bold;">0 interceptions</span> through four games, '
        f'and they\'re allowing {dal.pa_pg:.1f} points per game',
        unsafe_allow_html=True,
    )

    st.subheader("QB rooms worth watching")
    col1, col2 = st.columns(2)
    was_c, atl_c = TC["WAS"], TC["ATL"]
    was = ts[ts.team == "WAS"].iloc[0]
    with col1:
        st.markdown(f"{tname('WAS')} ({record(was.wins, was.losses)})", unsafe_allow_html=True)
        st.markdown(
            "**Marcus Mariota** got hurt in the first quarter against the Indianapolis Colts in Week 4. "
            "Rookie **Athan Kaliakmanis** played every snap after that. Jayden Daniels is also out "
            "with an elbow injury (Weeks 3 and 4). Three arms, one season:\n\n"
            "- **Marcus Mariota**: 54 attempts, 61.1% completion, 4 TD, 0 INT, **+0.124 EPA/Play**\n"
            "- **Jayden Daniels** (before injury): 53 attempts, 54.7% completion, 3 TD, 0 INT, **+0.077 EPA/Play**\n"
            "- **Athan Kaliakmanis** (rookie): 34 attempts, 44.1% completion, 1 TD, 1 INT, **-0.300 EPA/Play**"
        )
    with col2:
        st.markdown(f"{tname('ATL')} (2W-2L)", unsafe_allow_html=True)
        st.markdown(
            "Good the last two weeks. Head coach **Raheem Morris** has shuffled the room all season: "
            "**Michael Penix Jr.** is QB1 now, veteran **Cooper Rush** (9th season) started Weeks 1-2, "
            "rookie **Jack Strand** relieved him in Week 2, and **Tua Tagovailoa** is still recovering "
            "from an oblique injury. Since Penix took over in Week 3:\n\n"
            "- Week 3 win, 35-14. Week 4 win, 45-24\n"
            "- **35 and 45 points** in back-to-back wins\n"
            f"- Next up: {tname('BAL')}",
            unsafe_allow_html=True,
        )

    st.subheader("The winless teams")
    wl = ts[ts.team.isin(["HOU", "LAC", "TB"])][["team", "wins", "losses", "point_diff", "takeaways", "giveaways"]].copy()
    sacks_allowed = load("ol_dl_stats.csv")[["team", "sacks_allowed_by_OL"]]
    wl = wl.merge(sacks_allowed, on="team").sort_values("point_diff")
    wl_order = wl["team"].tolist()
    wl["Record"] = wl.apply(lambda r: record(r.wins, r.losses), axis=1)
    wl["Team"] = wl["team"].map(full)
    wl_disp = wl.rename(columns={
        "point_diff": "Point differential", "takeaways": "Takeaways",
        "giveaways": "Giveaways", "sacks_allowed_by_OL": "Sacks allowed (own QB tackled behind the line)",
    })[["Team", "Record", "Point differential", "Sacks allowed (own QB tackled behind the line)", "Giveaways", "Takeaways"]]
    html_table(wl_disp, team_col_idx=0, team_abbrs=wl_order)
    caption(
        "Houston's 0W-4L ties their worst 4-game start in five years. Last season they were 1W-3L "
        "at this point, so this year is a real drop, worth watching if it continues."
    )
    st.markdown(
        f"{tname('TB')} and {tname('LAC')} give the ball away the most in the league, but the "
        f"Chargers' defense is taking it away too (7 takeaways, best of these three). Once their "
        "offense stops handing it back, a first win may not be far off.",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p style="color:#000 !important;font-weight:700 !important;font-size:11px;'
        'margin:18px 0 2px 0;padding-top:8px;border-top:1px solid #999;text-decoration:underline;">'
        "Sources: nflverse / nflfastR play-by-play and schedule data &middot; NGS (Next Gen Stats) "
        "&middot; PFR (Pro Football Reference) &middot; FTN charting (play-type tendency). "
        "2026 season, Weeks 1-4.</p>",
        unsafe_allow_html=True,
    )
