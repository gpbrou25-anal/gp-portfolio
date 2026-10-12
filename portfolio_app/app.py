"""
Georges-Patrick Brou — Portfolio

Three things: video breakdown (Wyscout match/set-piece analysis), carousels,
and the real project READMEs (not just links) from GitHub.

Run locally:  streamlit run portfolio_app/app.py
Deploy:       share.streamlit.io -> New app -> this repo -> portfolio_app/app.py
"""
import os
import re
import streamlit as st

st.set_page_config(page_title="Georges-Patrick Brou — Portfolio", page_icon="🎯", layout="wide")

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
VIDEO_DIR = os.path.join(ASSETS, "videos")
CAROUSEL_DIR = os.path.join(ASSETS, "carousel")
README_DIR = os.path.join(ASSETS, "readmes")
NFL_README = os.path.join(os.path.dirname(__file__), "..", "projects", "nfl-analytics", "README.md")
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
.slide-counter { font-family: monospace; font-size: 13px; color: #8ea3b3; text-align: center; margin-top: 10px; }
.readme-box { background: #101e29; border: 1px solid #25394c; border-radius: 8px; padding: 18px 22px; }
.readme-box h1, .readme-box h2, .readme-box h3 { border-bottom: none; margin-top: 0.8rem !important; font-family: 'Georgia', serif; }
[data-testid="stExpander"] { background: #101e29; border: 1px solid #25394c; border-radius: 8px; }
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
st.markdown(
    '<span class="tag">Wyscout</span><span class="tag">Clip tagging</span>'
    '<span class="tag">Set-piece analysis</span><span class="tag">Opposition scouting</span>',
    unsafe_allow_html=True,
)

video_files = []
if os.path.isdir(VIDEO_DIR):
    video_files = sorted(
        f for f in os.listdir(VIDEO_DIR) if f.lower().endswith((".mp4", ".mov", ".webm"))
    )

if video_files:
    vcols = st.columns(min(3, len(video_files)))
    for i, vf in enumerate(video_files):
        with vcols[i % len(vcols)]:
            st.video(os.path.join(VIDEO_DIR, vf))
            st.caption(vf)
else:
    st.info(
        "No video uploaded yet. Put your real clip at "
        "`portfolio_app/assets/videos/` in the repo (any `.mp4`, `.mov`, or `.webm` file), commit "
        "and push — it plays here automatically, no code changes needed."
    )

st.divider()

# ---------------------------------------------------------------------------
# 02 — Carousels
# ---------------------------------------------------------------------------
st.markdown("## 02 · Carousels")

carousels = []
if os.path.isdir(CAROUSEL_DIR):
    for name in sorted(os.listdir(CAROUSEL_DIR)):
        folder = os.path.join(CAROUSEL_DIR, name)
        if os.path.isdir(folder):
            slides = sorted(
                f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))
            )
            if slides:
                carousels.append((name, folder, slides))

CAROUSEL_LABELS = {
    "nfl-overview": "Four Games In — NFL season overview",
    "setpiece-analysis": "Set-piece analysis — LinkedIn carousel",
}

if carousels:
    labels = [CAROUSEL_LABELS.get(name, name) for name, _, _ in carousels]
    picked_label = st.radio("Which carousel", labels, horizontal=True, label_visibility="collapsed")
    name, folder, slides = carousels[labels.index(picked_label)]

    state_key = f"slide_idx_{name}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 0
    st.session_state[state_key] %= len(slides)

    nav1, nav2, nav3 = st.columns([1, 6, 1])
    with nav1:
        if st.button("← Prev", use_container_width=True, key=f"prev_{name}"):
            st.session_state[state_key] = (st.session_state[state_key] - 1) % len(slides)
    with nav3:
        if st.button("Next →", use_container_width=True, key=f"next_{name}"):
            st.session_state[state_key] = (st.session_state[state_key] + 1) % len(slides)
    with nav2:
        st.image(os.path.join(folder, slides[st.session_state[state_key]]), use_container_width=True)

    st.markdown(
        f'<div class="slide-counter">Slide {st.session_state[state_key] + 1} / {len(slides)}</div>',
        unsafe_allow_html=True,
    )
else:
    st.info("No carousel slides yet.")

st.caption(
    "To add a carousel: create a folder under `portfolio_app/assets/carousel/<name>/` and drop the "
    "slide images in it (in the order they should play), commit and push. A second carousel folder, "
    "`setpiece-analysis/`, is already there and ready for your set-piece LinkedIn carousel — just add "
    "the images to it."
)

st.divider()

# ---------------------------------------------------------------------------
# 03 — Projects (real READMEs, not just links)
# ---------------------------------------------------------------------------
st.markdown("## 03 · Projects")
st.write("The actual project write-ups, pulled straight from each project's own README.")


def show_readme(title, path, repo_link, figures_dir=None):
    with st.expander(title, expanded=False):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # drop inline markdown images — their relative paths don't resolve here;
            # the real charts render separately below via st.image instead
            content = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", content)
            st.markdown(f'<div class="readme-box">\n\n{content}\n\n</div>', unsafe_allow_html=True)
        else:
            st.caption("README not found locally yet.")

        if figures_dir and os.path.isdir(figures_dir):
            figs = sorted(
                f for f in os.listdir(figures_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))
            )
            if figs:
                st.markdown("**Charts**")
                fcols = st.columns(2)
                for i, fig in enumerate(figs):
                    with fcols[i % 2]:
                        st.image(os.path.join(figures_dir, fig), use_container_width=True)
                        st.caption(fig.rsplit(".", 1)[0].replace("_", " ").lstrip("0123456789 "))

        st.caption(f"[View on GitHub →]({repo_link})")


show_readme(
    "NFL Performance Analytics",
    NFL_README,
    f"https://github.com/{GITHUB_USER}/{THIS_REPO}/tree/main/projects/nfl-analytics",
)
show_readme(
    "Volume vs. Elite Defenses",
    os.path.join(README_DIR, "nba-01.md"),
    f"https://github.com/{GITHUB_USER}/NBA-Analytics-Portfolio/tree/main/projects/01-volume-vs-elite-defenses",
    figures_dir=os.path.join(README_DIR, "figures-01"),
)
show_readme(
    "Knicks 2026 Contender Analysis",
    os.path.join(README_DIR, "nba-02.md"),
    f"https://github.com/{GITHUB_USER}/NBA-Analytics-Portfolio/tree/main/projects/02-knicks-contender-2026",
    figures_dir=os.path.join(README_DIR, "figures-02"),
)

st.divider()
st.caption("Georges-Patrick Brou · Barcelona, Spain · gbottobrou@gmail.com · +34 667 405 535")
