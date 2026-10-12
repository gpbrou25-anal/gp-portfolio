"""
Georges-Patrick Brou — Portfolio

Three things: video breakdown (Wyscout match/set-piece analysis), carousels,
and the real project READMEs (not just links) from GitHub.

Run locally:  streamlit run portfolio_app/app.py
Deploy:       share.streamlit.io -> New app -> this repo -> portfolio_app/app.py
"""
import base64
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

WATERMARK_B64 = ""
_wm_path = os.path.join(ASSETS, "logo-watermark.png")
if os.path.exists(_wm_path):
    with open(_wm_path, "rb") as f:
        WATERMARK_B64 = base64.b64encode(f.read()).decode("ascii")

# ---------------------------------------------------------------------------
# Brand styling — white, with the A'eye logo as a repeating wallpaper pattern
# ---------------------------------------------------------------------------
_CSS = """
<style>
.stApp {
    color: #1b2630;
    background:
        url("data:image/png;base64,__WATERMARK_B64__") repeat;
    background-size: 340px;
    background-color: #ffffff;
}
.block-container { max-width: 1400px; padding-top: 1.2rem; padding-left: 2.5rem; padding-right: 2.5rem; }
.hero-banner {
    position: relative; border-radius: 12px; overflow: hidden; margin-bottom: 1.5rem;
    border: 1px solid #dfe6ec; padding: 40px 40px 32px;
    background: rgba(255,255,255,0.86);
    box-shadow: 0 2px 10px rgba(20,40,60,0.06);
}
h1, h2, h3 { font-family: 'Georgia', serif; letter-spacing: 0.01em; }
h1 { color: #1b2630 !important; }
h2 { color: #1b2630 !important; border-bottom: 1px solid #dfe6ec; padding-bottom: 10px; margin-top: 2.2rem !important; }
p, li, span, div { color: #33424e; }
.eyebrow { font-family: monospace; font-size: 12px; letter-spacing: 0.14em; color: #1f8f85; text-transform: uppercase; }
.sub { color: #5c6b78; font-size: 16px; max-width: 60ch; }
.meta-row { font-family: monospace; font-size: 13px; color: #5c6b78; margin-top: 10px; }
.meta-row b { color: #1b2630; }
.tag { display:inline-block; font-family: monospace; font-size: 11px; padding: 4px 9px; margin: 3px 4px 0 0;
       border-radius: 4px; background: #f0f4f7; color: #5c6b78; border: 1px solid #dfe6ec; }
figcaption, .stCaption, [data-testid="stCaptionContainer"] { color: #5c6b78 !important; }
a { color: #1f8f85; }
hr { border-color: #dfe6ec; }
.slide-counter { font-family: monospace; font-size: 13px; color: #5c6b78; text-align: center; margin-top: 10px; }
.readme-box { background: rgba(255,255,255,0.92); border: 1px solid #dfe6ec; border-radius: 8px; padding: 18px 22px; box-shadow: 0 1px 6px rgba(20,40,60,0.05); }
.readme-box h1, .readme-box h2, .readme-box h3 { border-bottom: none; margin-top: 0.8rem !important; font-family: 'Georgia', serif; }
[data-testid="stExpander"] { background: rgba(255,255,255,0.92); border: 1px solid #dfe6ec; border-radius: 8px; }
.analysis-block { background: rgba(255,255,255,0.92); border: 1px solid #dfe6ec; border-radius: 8px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 1px 6px rgba(20,40,60,0.05); }
.analysis-block h3 { margin: 0 0 4px 0 !important; font-size: 19px; color: #1b2630; }
.analysis-score { font-family: monospace; font-size: 12.5px; color: #a97c23; letter-spacing: 0.04em; margin-bottom: 14px; }
.analysis-block p { margin: 0 0 12px 0; line-height: 1.6; }
.analysis-sub { font-family: monospace; font-size: 11.5px; letter-spacing: 0.1em; text-transform: uppercase; color: #1f8f85; margin: 16px 0 8px; }
ul.analysis-bullets { list-style: none; margin: 0 0 14px 0; padding: 0; }
ul.analysis-bullets li { position: relative; padding-left: 18px; margin-bottom: 9px; line-height: 1.55; color: #33424e; }
ul.analysis-bullets li::before { content: "•"; position: absolute; left: 0; color: #1f8f85; }
ul.analysis-arrows { list-style: none; margin: 0 0 14px 0; padding: 0; }
ul.analysis-arrows li { position: relative; padding-left: 22px; margin-bottom: 9px; line-height: 1.55; color: #33424e; }
ul.analysis-arrows li::before { content: "→"; position: absolute; left: 0; color: #a97c23; }
</style>
"""
_css_final = _CSS.replace("__WATERMARK_B64__", WATERMARK_B64)
st.markdown(_css_final, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
with open(os.path.join(ASSETS, "logo.png"), "rb") as f:
    _logo_b64 = base64.b64encode(f.read()).decode("ascii")

st.markdown(
    '<div class="hero-banner">'
    f'<img src="data:image/png;base64,{_logo_b64}" style="height:96px;width:auto;margin-bottom:18px;" alt="A\'eye logo">'
    '<div class="eyebrow">Multisport analyst</div>'
    '<h1 style="font-size:46px;margin:6px 0 14px;">Georges-Patrick Brou</h1>'
    '<p class="sub">Master\'s student in Sport Management and Legal Skills at ISDE Barcelona, built in '
    'partnership with Barça Innovation Hub, on top of an MSc in Big Data &amp; Analytics. Sport is the '
    'thread through both, I\'m genuinely passionate about more than one of them, and I\'m building real '
    'skills in data analysis, performance scouting, and video analysis to go with it. What I bring is '
    'an eye for detail and for the pattern other people miss. I\'m looking for an environment where '
    'that\'s actually useful: adding value for a team, finding solutions, helping improve recruitment '
    'and performance, and sharpening what I know inside a structured setup.</p>'
    '<p class="sub">Below is my portfolio, bringing together everything I\'ve worked on so far. Enjoy '
    'a quick look at how I see sport, I\'d genuinely like the chance to talk more and go deeper into '
    'it.</p>'
    '<div class="meta-row">MSc <b>Big Data &amp; Analytics</b> &nbsp;·&nbsp; Sport Management &amp; '
    'Legal Skills, <b>ISDE Barcelona</b> &nbsp;·&nbsp; <b>Barça Innovation Hub</b> &nbsp;·&nbsp; '
    '<b>Barcelona</b>, Spain</div>'
    '</div>',
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

# YouTube links — one per line in youtube_links.txt: "group | title | url"
yt_by_group = {}
yt_path = os.path.join(VIDEO_DIR, "youtube_links.txt")
if os.path.exists(yt_path):
    with open(yt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) == 3:
                group, title, url = parts
            elif len(parts) == 2:
                group, title, url = "corners", parts[0], parts[1]
            else:
                group, title, url = "corners", None, parts[0]
            yt_by_group.setdefault(group, []).append((title, url))

# local files always go under "corners" by default
video_files = []
if os.path.isdir(VIDEO_DIR):
    video_files = sorted(
        f for f in os.listdir(VIDEO_DIR) if f.lower().endswith((".mp4", ".mov", ".webm"))
    )
for vf in video_files:
    yt_by_group.setdefault("corners", []).append((vf, os.path.join(VIDEO_DIR, vf)))


def bullets(items, arrows=False):
    cls = "analysis-arrows" if arrows else "analysis-bullets"
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="{cls}">{lis}</ul>'


def show_clips(group):
    clips = yt_by_group.get(group, [])
    if not clips:
        st.caption(
            f"No clip yet for this one — add a line to `portfolio_app/assets/videos/youtube_links.txt` "
            f"as `{group} | Title | https://youtu.be/...`."
        )
        return
    cols = st.columns(min(2, len(clips)))
    for i, (title, url) in enumerate(clips):
        with cols[i % len(cols)]:
            st.video(url)
            if title:
                st.caption(title)


# --- Analysis 1: Saka's corners from the right -----------------------------
st.markdown(
    '<div class="analysis-block">'
    '<h3>Saka\'s corners from the right</h3>'
    '<div class="analysis-score">PREMIER LEAGUE 2026/27 · ARSENAL · SET-PIECE ANALYSIS</div>'
    "<p>Arsenal haven't scored from a right-side corner yet this season, but watching some of "
    "Saka's deliveries from the right, that won't last long.</p>"
    "<p>Same formation almost every time: a group anchored at the back post, a guy crowding the "
    "goalkeeper's zone, and a runner arriving at pace. What changes is the execution depending on "
    "where the ball's going.</p>"
    '<div class="analysis-sub">Near post</div>'
    + bullets([
        "The group overloads the near-post zone and sets blocks, players like Hincapié and Calafiori "
        "doing the screening, stopping defenders from attacking the ball and creating space for the "
        "targets",
        "Gabriel is usually the one running the wide receiver route off the underlap, arriving at pace "
        "to meet it free, though sometimes he's the one crowding the keeper's zone instead",
        "White covers the keeper job too, Saliba would normally be in that mix but he's out right now",
    ])
    + '<div class="analysis-sub">Far post</div>'
    + bullets([
        "Same group, different job, they can attack the middle instead or hold their position at the "
        "back post",
        "When they turn to face the ball, it's Konsa or Havertz set up for the flick-on",
        "The blockers aren't screening for someone else anymore, they're the ones contesting the "
        "second ball at the back post",
        "Gabriel isn't locked into the near-post route either, he can run it to the back post just as "
        "easily",
    ])
    + "<p>It's basically one formation with multiple reads built in, like an NFL playbook, the picture "
    "changes depending on whether the defense sits zonal at the near post or goes man-to-man at the "
    "back.</p>"
    "<p>Not really a coincidence either. Arteta and LA Rams head coach Sean McVay talk regularly "
    "(same owner, Stan Kroenke), and McVay's own line is that every NFL play is basically a "
    "set-piece. That's the exact mindset showing up in these corners.</p>"
    "<p>Clips below (3 near, 3 far post), zero goals so far, but the spacing and the variety are "
    "still clean for that to hold much longer.</p>"
    '<span class="tag">Built in Wyscout</span>'
    "</div>",
    unsafe_allow_html=True,
)
show_clips("corners")

# --- Analysis 2: Brighton 3-0 Arsenal, the first goal -----------------------
st.markdown(
    '<div class="analysis-block">'
    "<h3>Brighton 3-0 Arsenal — the first goal</h3>"
    '<div class="analysis-score">MATCHWEEK 5 · PREMIER LEAGUE 2026/27 · BRIGHTON 3–0 ARSENAL</div>'
    "<p>Arsenal had just survived their hardest 20 minutes against Brighton. Then one patient "
    "Brighton possession undid it.</p>"
    "<p>The first goal, 31st minute, from outside the box.</p>"
    + bullets([
        "Arsenal sat deep in 4-4-2, no real pressure on the ball, settled enough to switch off for a "
        "second",
        "Guimarães gets drawn in by the ball and presses a man who's already covered, the pass behind "
        "him goes unnoticed",
        "Ayari drifts inside and drags Calafiori out with him, Gabriel drops in just to help behind",
        "Calafiori recovers and tries to force the shot away, reading it like Raya already has it "
        "covered",
        "Raya's expecting something else, and by the time that gap shows, Groß has already finished "
        "near post, from outside the box",
    ])
    + "<p>It wasn't poor defending by Arsenal. For one phase, nobody was sure who had what: Guimarães "
    "drawn out, Calafiori covering, Gabriel helping, Raya searching. That's all it takes at this "
    "level to punish little mistakes, even from distance.</p>"
    '<span class="tag">Built in Wyscout</span>'
    "</div>",
    unsafe_allow_html=True,
)
show_clips("brighton")

st.divider()

def render_carousel(name):
    """Render one named carousel folder in place, wherever it's called from."""
    folder = os.path.join(CAROUSEL_DIR, name)
    if not os.path.isdir(folder):
        return
    slides = sorted(f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    if not slides:
        return

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


# ---------------------------------------------------------------------------
# 02 — Projects (real READMEs, not just links)
# ---------------------------------------------------------------------------
st.markdown("## 02 · Projects")
st.write("The actual project write-ups, pulled straight from each project's own README.")


def _inline_image_tag(fname, figures_dir, alt):
    """Base64-embed a local chart image so it can sit inline inside st.markdown HTML."""
    fpath = os.path.join(figures_dir, fname)
    if not os.path.exists(fpath):
        return f"\n\n*(chart not found: {fname})*\n\n"
    ext = fname.rsplit(".", 1)[-1].lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    with open(fpath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return (
        f'\n\n<img src="data:image/{mime};base64,{b64}" alt="{alt}" '
        f'style="max-width:100%;border-radius:6px;margin:10px 0;border:1px solid #dfe6ec;"/>'
        f'\n\n<div style="font-size:12.5px;color:#5c6b78;margin:-6px 0 10px;">{alt}</div>\n\n'
    )


def show_readme(title, path, repo_link, figures_dir=None):
    with st.expander(title, expanded=False):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if figures_dir and os.path.isdir(figures_dir):
                # replace each inline ![alt](figures/xxx.png) with the real chart,
                # embedded right where the write-up already places it
                def _sub(m):
                    alt, ref = m.group(1), m.group(2)
                    fname = ref.rsplit("/", 1)[-1]
                    return _inline_image_tag(fname, figures_dir, alt or fname)

                content = re.sub(r"!\[([^\]]*)\]\(([^)]*)\)", _sub, content)
            else:
                content = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", content)
            st.markdown(f'<div class="readme-box">\n\n{content}\n\n</div>', unsafe_allow_html=True)
        else:
            st.caption("README not found locally yet.")

        st.caption(f"[View on GitHub →]({repo_link})")


with st.expander("NFL Performance Analytics", expanded=False):
    st.markdown(
        '<div class="readme-box">'
        "<p>Four games into the 2026 NFL season, so I pulled the numbers and broke down what's "
        "actually happening.</p>"
        "<p>Built through \"Analytics eye,\" my multisport analytics project covering football, "
        "basketball, and American football for this one. I pulled real play-by-play data "
        "(nflverse/nflfastR), Next Gen Stats, PFR, and FTN charting, ran it through my own Streamlit "
        "app, and turned it into the carousel above.</p>"
        '<div class="analysis-sub">What\'s in it</div>'
        + bullets([
            "Teams that changed coaches this offseason — who's actually winning with the new staff, "
            "who isn't",
            "Teams playing well right now: explosive run games, defenses taking the ball away",
            "Teams showing both sides: strong in one area, exposed in the other",
            "Teams still searching for their first win",
        ], arrows=True)
        + "<p>Every number here is pulled straight from the data, nothing guessed or estimated.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    render_carousel("nfl-overview")
    _diag_path = os.path.join(README_DIR, "nfl-diagnostic-screen.jpg")
    if os.path.exists(_diag_path):
        st.image(_diag_path, use_container_width=True)
        st.caption(
            "The full diagnostic behind the carousel — point differential, defensive touchdowns, "
            "offense/defense quadrants and more, all 32 teams, refreshed every week. There's a lot "
            "more to explore here as the season goes on, this overview is just the entry point."
        )
    st.caption(
        f"[View the full project on GitHub →]"
        f"(https://github.com/{GITHUB_USER}/{THIS_REPO}/tree/main/projects/nfl-analytics)"
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
