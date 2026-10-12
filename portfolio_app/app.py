"""
Georges-Patrick Brou — Portfolio

Real, deployable Streamlit portfolio: match & set-piece analysis (Wyscout),
NFL performance analytics, the tools built to produce both, and links out to
the real GitHub repos behind every project.

Run locally:  streamlit run portfolio_app/app.py
Deploy:       share.streamlit.io -> New app -> this repo -> portfolio_app/app.py
"""
import os
import streamlit as st

st.set_page_config(page_title="Georges-Patrick Brou — Portfolio", page_icon="🎯", layout="wide")

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
VIDEO_DIR = os.path.join(ASSETS, "videos")
GITHUB_USER = "gpbrou25-anal"
THIS_REPO = "gp-portfolio"

# ---------------------------------------------------------------------------
# Brand styling — dark navy / teal / gold, matching the A'eye visual identity
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.stApp { background: #0a131c; color: #eaf2f6; }
.block-container { max-width: 980px; padding-top: 2rem; }
h1, h2, h3 { font-family: 'Georgia', serif; letter-spacing: 0.01em; }
h1 { color: #eaf2f6 !important; }
h2 { color: #eaf2f6 !important; border-bottom: 1px solid #25394c; padding-bottom: 10px; margin-top: 2.2rem !important; }
p, li, span, div { color: #cdd9e1; }
.eyebrow { font-family: monospace; font-size: 12px; letter-spacing: 0.14em; color: #45b0a8; text-transform: uppercase; }
.sub { color: #8ea3b3; font-size: 16px; max-width: 60ch; }
.meta-row { font-family: monospace; font-size: 13px; color: #8ea3b3; margin-top: 10px; }
.meta-row b { color: #eaf2f6; }
.tag { display:inline-block; font-family: monospace; font-size: 11px; padding: 4px 9px; margin: 3px 4px 0 0;
       border-radius: 4px; background: #17293a; color: #8ea3b3; border: 1px solid #25394c; }
figcaption, .stCaption, [data-testid="stCaptionContainer"] { color: #8ea3b3 !important; }
a { color: #45b0a8; }
hr { border-color: #25394c; }
.tool-card { background: #101e29; border: 1px solid #25394c; border-radius: 8px; padding: 16px 18px; margin-bottom: 14px; }
.tool-card h4 { margin: 0 0 6px 0; color: #eaf2f6; }
.gh-row a { font-family: monospace; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image(os.path.join(ASSETS, "logo.png"), use_container_width=True)
with col_title:
    st.markdown('<div class="eyebrow">Match &amp; data analyst</div>', unsafe_allow_html=True)
    st.markdown("# Georges-Patrick Brou")
    st.markdown(
        '<p class="sub">MSc Big Data &amp; Analytics student who also breaks down match footage in '
        'Wyscout — set-piece patterns, player roles, zone occupation — and backs that reading with '
        'real data work in Python and SQL.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="meta-row">MSc <b>Big Data &amp; Analytics</b> &nbsp;·&nbsp; Football <b>Coach</b> '
        '&nbsp;·&nbsp; <b>Wyscout</b> match analysis &nbsp;·&nbsp; <b>Barcelona</b>, Spain</div>',
        unsafe_allow_html=True,
    )

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    st.link_button("gbottobrou@gmail.com", "mailto:gbottobrou@gmail.com", use_container_width=True)
with c2:
    st.link_button("GitHub profile", f"https://github.com/{GITHUB_USER}", use_container_width=True)

cv_path = os.path.join(ASSETS, "CV.pdf")
with c3:
    if os.path.exists(cv_path):
        with open(cv_path, "rb") as f:
            st.download_button("Download CV (PDF)", f, file_name="Georges-Patrick_Brou_CV.pdf", use_container_width=True)
    else:
        st.caption("CV download will appear here once assets/CV.pdf is added to the repo.")

st.divider()

# ---------------------------------------------------------------------------
# 01 — Match & set-piece analysis
# ---------------------------------------------------------------------------
st.markdown("## 01 · Match & set-piece analysis")
st.write(
    "I break down match footage in Wyscout on my own time. Right now it's a Premier League team's "
    "right-side corners under their primary taker this season — mapping the recurring formation and "
    "splitting it by near-post vs. far-post execution, with specific player roles named rather than "
    "one-off commentary."
)

gcol1, gcol2 = st.columns(2)
with gcol1:
    st.image(os.path.join(ASSETS, "corner-1.jpg"), use_container_width=True)
    st.caption(
        "**Near post.** The back-post group screens the defenders, clearing a header for the target "
        "or the runner arriving at pace. A second player occupies the goalkeeper's zone throughout."
    )
with gcol2:
    st.image(os.path.join(ASSETS, "corner-2.jpg"), use_container_width=True)
    st.caption(
        "**Far post.** Same formation, different job — the group attacks the middle or holds the "
        "back post, then contests the second ball once play turns to face the delivery."
    )

st.markdown(
    '<span class="tag">Wyscout</span><span class="tag">Clip tagging</span>'
    '<span class="tag">Set-piece analysis</span><span class="tag">Opposition scouting</span>',
    unsafe_allow_html=True,
)

video_files = []
if os.path.isdir(VIDEO_DIR):
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith((".mp4", ".mov", ".webm"))]

if video_files:
    st.markdown("**Clips**")
    vcols = st.columns(min(3, len(video_files)))
    for i, vf in enumerate(video_files):
        with vcols[i % len(vcols)]:
            st.video(os.path.join(VIDEO_DIR, vf))
            st.caption(vf)
else:
    st.caption(
        "To add video clips: drop .mp4/.mov files into `portfolio_app/assets/videos/`, commit and "
        "push — they'll appear here automatically, no code changes needed."
    )

st.divider()

# ---------------------------------------------------------------------------
# 02 — NFL performance analytics
# ---------------------------------------------------------------------------
st.markdown("## 02 · NFL performance analytics")
st.write(
    "A season-long NFL analytics project: a data pipeline pulling play-by-play data, computing "
    "efficiency and explosive-play metrics for all 32 teams, refreshed weekly and presented through "
    "two Streamlit apps — a full diagnostic view and a narrative overview for a quick read."
)

ncol1, ncol2 = st.columns(2)
with ncol1:
    st.image(os.path.join(ASSETS, "nfl-1.jpg"), use_container_width=True)
    st.caption("**League overview** — new-coach risers, early strugglers, and a week-by-week narrative read.")
with ncol2:
    st.image(os.path.join(ASSETS, "nfl-2.jpg"), use_container_width=True)
    st.caption("**Efficiency charts** — rushing and defensive performance plotted against the league median.")

st.markdown(
    '<span class="tag">Python</span><span class="tag">Pandas</span><span class="tag">SQL</span>'
    '<span class="tag">Streamlit</span><span class="tag">Data visualization</span><span class="tag">KPI tracking</span>',
    unsafe_allow_html=True,
)
st.markdown(
    f"**Code:** [github.com/{GITHUB_USER}/{THIS_REPO}/tree/main/projects/nfl-analytics]"
    f"(https://github.com/{GITHUB_USER}/{THIS_REPO}/tree/main/projects/nfl-analytics) — "
    "run locally with `streamlit run projects/nfl-analytics/league_overview_app.py`."
)

st.divider()

# ---------------------------------------------------------------------------
# 03 — Tools built
# ---------------------------------------------------------------------------
st.markdown("## 03 · Tools built")
st.write("I don't just analyze — I build the tools that make the analysis repeatable instead of starting from zero every time.")

st.markdown(
    f"""
<div class="tool-card">
<h4>Sports job application tailor</h4>
A rule-based tool that rebuilds the application angle (About, skills order, featured project, cover
letter) for each specific job posting — Analytics, Management, or Law/Governance track — instead of
sending the same generic CV to every role.<br><br>
<a href="https://github.com/{GITHUB_USER}/{THIS_REPO}/tree/main/projects/job-application-tailor">View code →</a>
</div>
<div class="tool-card">
<h4>NFL data refresh pipeline</h4>
A one-command script that keeps three separate data snapshots in sync across a full season, so the
dashboards above never show stale numbers after a week's games finish.<br><br>
<a href="https://github.com/{GITHUB_USER}/{THIS_REPO}/tree/main/projects/nfl-analytics/refresh_all_data.py">View code →</a>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# 04 — Background
# ---------------------------------------------------------------------------
st.markdown("## 04 · Background")
b1, b2 = st.columns(2)
with b1:
    st.markdown("**Data & Analytics**")
    st.caption("MSc Big Data & Analytics · SQL · Python (Pandas, NumPy) · Power BI · Excel · Data visualization")
    st.markdown("**Sport**")
    st.caption("Football coaching — player development, team leadership · match analysis in Wyscout")
with b2:
    st.markdown("**Commercial**")
    st.caption("Primark — sales, customer flow, store performance under operational pressure")
    st.markdown("**Foundation**")
    st.caption("Economics & Applied Data Analysis — quantitative reasoning behind every project above")

st.divider()

# ---------------------------------------------------------------------------
# 05 — More on GitHub
# ---------------------------------------------------------------------------
st.markdown("## 05 · More on GitHub")
st.markdown(
    f"""
<div class="gh-row">
<a href="https://github.com/{GITHUB_USER}">github.com/{GITHUB_USER}</a> — full profile<br>
<a href="https://github.com/{GITHUB_USER}/NBA-Analytics-Portfolio">github.com/{GITHUB_USER}/NBA-Analytics-Portfolio</a>
— opponent-adjusted scoring, clutch impact, injury recovery curves, contract value<br>
<a href="https://github.com/{GITHUB_USER}/{THIS_REPO}">github.com/{GITHUB_USER}/{THIS_REPO}</a>
— this portfolio's own source, including every project above
</div>
""",
    unsafe_allow_html=True,
)

st.divider()
st.caption("Georges-Patrick Brou · Barcelona, Spain · gbottobrou@gmail.com · +34 667 405 535")
