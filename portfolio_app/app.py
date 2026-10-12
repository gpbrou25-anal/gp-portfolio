"""
Georges-Patrick Brou — Portfolio

Three things: video breakdown (Wyscout match/set-piece analysis), the NFL
carousel deck, and links to the real analysis repos on GitHub.

Run locally:  streamlit run portfolio_app/app.py
Deploy:       share.streamlit.io -> New app -> this repo -> portfolio_app/app.py
"""
import os
import streamlit as st

st.set_page_config(page_title="Georges-Patrick Brou — Portfolio", page_icon="🎯", layout="wide")

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
VIDEO_DIR = os.path.join(ASSETS, "videos")
CAROUSEL_DIR = os.path.join(ASSETS, "carousel")
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
.gh-card { background: #101e29; border: 1px solid #25394c; border-radius: 8px; padding: 16px 18px; margin-bottom: 14px; }
.gh-card h4 { margin: 0 0 6px 0; color: #eaf2f6; }
.gh-card a { font-family: monospace; font-size: 13px; }
.slide-counter { font-family: monospace; font-size: 13px; color: #8ea3b3; text-align: center; margin-top: 10px; }
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

c1, c2 = st.columns([1, 1])
with c1:
    st.link_button("gbottobrou@gmail.com", "mailto:gbottobrou@gmail.com", use_container_width=True)
with c2:
    st.link_button("GitHub profile", f"https://github.com/{GITHUB_USER}", use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# 01 — Video breakdown
# ---------------------------------------------------------------------------
st.markdown("## 01 · Video breakdown")
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
    video_files = sorted(f for f in os.listdir(VIDEO_DIR) if f.lower().endswith((".mp4", ".mov", ".webm")))

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
# 02 — Carousel
# ---------------------------------------------------------------------------
st.markdown("## 02 · Carousel")
st.write("Four Games In — the NFL season-overview carousel, built from the full analytics pipeline below.")

slides = []
if os.path.isdir(CAROUSEL_DIR):
    slides = sorted(f for f in os.listdir(CAROUSEL_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png")))

if slides:
    if "slide_idx" not in st.session_state:
        st.session_state.slide_idx = 0
    st.session_state.slide_idx %= len(slides)

    nav1, nav2, nav3 = st.columns([1, 6, 1])
    with nav1:
        if st.button("← Prev", use_container_width=True):
            st.session_state.slide_idx = (st.session_state.slide_idx - 1) % len(slides)
    with nav3:
        if st.button("Next →", use_container_width=True):
            st.session_state.slide_idx = (st.session_state.slide_idx + 1) % len(slides)
    with nav2:
        st.image(os.path.join(CAROUSEL_DIR, slides[st.session_state.slide_idx]), use_container_width=True)

    st.markdown(
        f'<div class="slide-counter">Slide {st.session_state.slide_idx + 1} / {len(slides)}</div>',
        unsafe_allow_html=True,
    )
else:
    st.caption(
        "To add carousel slides: drop image files into `portfolio_app/assets/carousel/`, commit and "
        "push — they'll appear here automatically, in alphabetical order."
    )

st.divider()

# ---------------------------------------------------------------------------
# 03 — GitHub analysis
# ---------------------------------------------------------------------------
st.markdown("## 03 · GitHub analysis")
st.markdown(
    f"""
<div class="gh-card">
<h4>NFL Performance Analytics</h4>
Full data pipeline pulling play-by-play data, computing efficiency and explosive-play metrics for all
32 teams, refreshed weekly, presented through two Streamlit apps. Source of the carousel above.<br><br>
<a href="https://github.com/{GITHUB_USER}/{THIS_REPO}/tree/main/projects/nfl-analytics">github.com/{GITHUB_USER}/{THIS_REPO}/tree/main/projects/nfl-analytics →</a>
</div>
<div class="gh-card">
<h4>NBA Analytics Portfolio</h4>
Opponent-adjusted scoring, clutch impact, injury recovery curves, contract value.<br><br>
<a href="https://github.com/{GITHUB_USER}/NBA-Analytics-Portfolio">github.com/{GITHUB_USER}/NBA-Analytics-Portfolio →</a>
</div>
<div class="gh-card">
<h4>This portfolio</h4>
The source behind this page itself.<br><br>
<a href="https://github.com/{GITHUB_USER}/{THIS_REPO}">github.com/{GITHUB_USER}/{THIS_REPO} →</a>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()
st.caption("Georges-Patrick Brou · Barcelona, Spain · gbottobrou@gmail.com · +34 667 405 535")
