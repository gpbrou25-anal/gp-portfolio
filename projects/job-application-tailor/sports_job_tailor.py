"""
Sports Job Application Tailor — Georges-Patrick Brou

Paste a sports-industry job description (Analytics / Management / Law/Governance),
get a tailored About Me, skills list, experience framing, project pick, and
cover letter draft built from his real background — following the Dynamic
Adaptation Engine rules in this folder's CLAUDE.md (never one generic CV for
every job; the positioning angle changes per role).

This is a rule-based generator (keyword matching + content blocks), not an
AI call, so it keeps working offline, instantly, every time you reopen it.
Nothing it produces claims experience Georges-Patrick doesn't have — the
Sports Law track leans on real governance/analytical exposure and leaves
explicit placeholders for anything that needs a real credential added by hand.

Run with: streamlit run sports_job_tailor.py
"""
import re
import streamlit as st

st.set_page_config(page_title="Sports Job Application Tailor", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1100px;}
h1 {font-size: 1.6rem !important;}
h2 {font-size: 1.2rem !important; margin-top: 1rem !important;}
.gp-block {background:#f7f7f4; border-left:4px solid #0b3d2e; padding:14px 18px; margin-bottom:14px; border-radius:4px;}
.gp-track {display:inline-block; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold; color:white;}
</style>
""", unsafe_allow_html=True)

TRACK_COLOR = {"Sports Analytics": "#1a5276", "Sports Management": "#7d6608", "Sports Law & Governance": "#641e16"}

# =====================================================================================
# Keyword signals used to suggest a track from the pasted job description.
TRACK_KEYWORDS = {
    "Sports Analytics": [
        "data", "sql", "python", "analytics", "analyst", "statistics", "statistical",
        "performance analysis", "scouting", "xg", "xpts", "model", "dashboard",
        "visualization", "metrics", "kpi", "power bi", "tableau", "r&d", "research analyst",
    ],
    "Sports Management": [
        "management", "manager", "operations", "strategy", "stakeholder", "leadership",
        "coordinator", "coordination", "project management", "club", "federation",
        "commercial", "partnerships", "sponsorship", "events", "administration",
    ],
    "Sports Law & Governance": [
        "law", "legal", "compliance", "regulation", "regulatory", "governance", "contract",
        "dispute", "fifa", "uefa", "arbitration", "policy", "integrity", "anti-doping",
        "disciplinary", "statutes", "eligibility",
    ],
}

def suggest_track(jd_text: str) -> str:
    text = jd_text.lower()
    scores = {t: sum(text.count(k) for k in ks) for t, ks in TRACK_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Sports Analytics"

def matched_keywords(jd_text: str, track: str) -> list:
    text = jd_text.lower()
    return [k for k in TRACK_KEYWORDS[track] if k in text]

def md_bold(s: str) -> str:
    """Convert markdown **bold** to HTML <b>bold</b> for use inside raw-HTML divs."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)

# =====================================================================================
# Content blocks per track, built from Georges-Patrick's real, verified background.

CONTENT = {
    "Sports Analytics": {
        "title_line": "Football Video & Data Analyst | Wyscout | MSc Big Data & Analytics",
        "about": (
            "MSc Big Data & Analytics student who also breaks down match footage in Wyscout, mostly "
            "set-piece patterns: who's occupying which zone, who's screening, who the delivery is "
            "actually meant for. I back that up with real data work in Python and SQL, so what I see "
            "on video and what the numbers say line up."
        ),
        "skills": [
            ("Video & Match Analysis", ["Wyscout", "Set-Piece Analysis", "Opposition Scouting", "Tactical Pattern Recognition", "Clip Tagging & Breakdown"]),
            ("Sports Analytics", ["Performance KPIs", "Player Development Tracking", "Match/Training Data Analysis", "Scouting Support"]),
            ("Analytics & Technical", ["SQL", "Python (Pandas, NumPy)", "Power BI", "Excel (Advanced)", "Data Visualization", "Streamlit"]),
            ("Football Background", ["Coaching", "Player Development", "Team Leadership", "Tactical Analysis"]),
        ],
        "ats_line": (
            "Wyscout, video analysis, set-piece analysis, opposition scouting, tactical analysis, "
            "performance analytics, SQL, Python, Pandas, Power BI, Excel, data visualization, Streamlit, "
            "KPI tracking, player development, football coaching, team leadership"
        ),
        "experience": (
            "**Match Analysis (Wyscout)** — I clip and tag matches on my own time, right now it's a Premier "
            "League team's corner routines from one side: who's in the back-post group, who's on the keeper, "
            "who's the runner arriving at pace, and how that changes between near post and far post. I write "
            "it up properly, player roles named, patterns tracked across several matches, not just a one-off "
            "take.\n\n"
            "**Football Coaching** — Worked directly on player development and performance, tracking fitness, "
            "consistency, decision-making under pressure. Same eye I now use on video and data.\n\n"
            "**Primark (Sales)** — Not a data role, but reading what's working and what isn't under pressure, "
            "with real customers and real numbers, carries over directly."
        ),
        "project": (
            "**Project 1 — Corner-routine breakdown (Wyscout).** Clipped and mapped a Premier League team's "
            "right-side corners across several matches this season: the recurring formation (back-post group, "
            "a player on the keeper, a runner arriving at pace), split by near-post vs far-post execution, "
            "with specific player roles named. Published, not kept as private notes.\n\n"
            "**Project 2 — NFL performance dashboard.** A Streamlit app I built and keep updated through the "
            "season, computing team and player performance metrics from raw play-by-play data. Shows the "
            "other half of this: building and maintaining the pipeline, not just reading someone else's numbers.\n\n"
            "Lead with Project 1 for a scouting or match-analysis posting, Project 2 for anything more "
            "data/BI-leaning. Worth mentioning both where there's room, they cover different ends of the job."
        ),
        "cover_opening": (
            "I'm applying because this is pretty much exactly what I already do on my own time: I coach, I "
            "break matches down in Wyscout, and I'm doing an MSc in Big Data & Analytics on top of it. Reading "
            "a corner routine on video and reading a dataset come from the same instinct for me."
        ),
    },
    "Sports Management": {
        "title_line": "Football Coaching & Team Leadership | MSc Big Data & Analytics | Sports Management",
        "about": (
            "I've led from both sides of sport: as a football coach responsible for player development and "
            "team performance, and now as an MSc Big Data & Analytics student bringing a structured, "
            "data-informed approach to the business and operational side of the game. I combine direct "
            "leadership experience with the analytical discipline to back decisions with evidence, not just instinct."
        ),
        "skills": [
            ("Sports Management", ["Team Leadership", "Player Development", "Sports Governance", "Performance Management", "Stakeholder Communication"]),
            ("Video & Performance Review", ["Wyscout", "Match Review", "Performance Tracking"]),
            ("Operations & Commercial", ["Retail Operations", "Customer-Facing Experience", "Operational Pressure", "KPI Monitoring"]),
            ("Analytics Foundation", ["SQL", "Python", "Power BI", "Excel", "Data-Backed Decision Making"]),
        ],
        "ats_line": (
            "team leadership, player development, sports governance, performance management, "
            "stakeholder communication, Wyscout, match review, retail operations, KPI monitoring, "
            "SQL, Python, Power BI, Excel, data-backed decision making, football coaching"
        ),
        "experience": (
            "**Football Coaching** — Full responsibility for player development, team leadership, and "
            "performance decisions under real competitive and time pressure — the same pressure that defines "
            "sports management at any level.\n\n"
            "**Primark (Sales)** — Direct, frontline exposure to operational pressure, staffing, customer "
            "flow, and store performance: the commercial and operational instincts that sports management "
            "roles need outside of the purely technical side."
        ),
        "project": (
            "**Project to feature: Commercial/Operations Performance Dashboard** — a club- or team-level "
            "operations view (attendance, commercial KPIs, or a simplified club performance dashboard) that "
            "shows you can bring structure and data to the business side of a sports organization, not just "
            "the playing side."
        ),
        "cover_opening": (
            "I'm applying because this role needs someone who has actually led people in a sporting "
            "environment and can also back decisions with data, not just one or the other. My coaching "
            "background gave me the leadership and governance exposure; my MSc is giving me the analytical "
            "rigor to support it."
        ),
    },
    "Sports Law & Governance": {
        "title_line": "Sports Governance Background | MSc Big Data & Analytics | [ADD: specific legal credential/coursework]",
        "about": (
            "My background in football, including exposure to sports governance structures and the "
            "regulatory side of player development, gives me a practical understanding of how rules, "
            "contracts, and compliance actually shape decisions in sport. [ADD: your specific legal "
            "education, certification, or coursework here — this section must not claim formal legal "
            "training you haven't completed]. I'm combining that with an MSc in Big Data & Analytics, "
            "which lets me support governance and compliance work with structured, evidence-based analysis."
        ),
        "skills": [
            ("Sports Governance", ["Sports Governance Exposure", "Regulatory Awareness", "Player Development Context", "Disciplinary/Eligibility Familiarity (sport-side)"]),
            ("Analytical Support", ["SQL", "Python", "Excel", "Data Documentation", "Structured Reporting"]),
            ("ADD YOUR OWN", ["[Law degree / certification]", "[Relevant legal coursework]", "[Compliance training]", "[Internship or clerkship, if any]"]),
        ],
        "ats_line": (
            "sports governance, regulatory awareness, player development, SQL, Python, Excel, "
            "structured reporting, compliance, [ADD: legal credential], [ADD: certification]"
        ),
        "experience": (
            "**Football Coaching** — Direct exposure to sports governance in practice: player eligibility, "
            "development pathways, and the structures clubs and federations operate under, seen from inside "
            "the sport rather than only in theory.\n\n"
            "**IMPORTANT:** this track is the weakest-supported of the three right now. Rule 51 of your "
            "playbook (Transferable Skills) says to never present transferable experience as direct "
            "experience. Before using this track for a real application, add your actual legal background "
            "(degree, coursework, certifications, internships) below so the tool can build a credible, "
            "honest positioning instead of leaning only on governance-adjacent football exposure."
        ),
        "project": (
            "**Project to feature:** [ADD a project once you have one — e.g. a sports-governance case study, "
            "a regulatory comparison across leagues/federations, or a compliance-focused data project. Do not "
            "ship this track without one; it currently has the thinnest evidence base of the three.]"
        ),
        "cover_opening": (
            "I'm applying because I bring a practical, inside-the-sport understanding of governance and "
            "regulation from my football background, and I'm building the analytical and [ADD: legal] "
            "foundation to support it formally. [This opening needs your specific legal credential to be "
            "fully credible — see the note in Experience above.]"
        ),
    },
}

HEADER = {
    "name": "Georges-Patrick Brou",
    "location": "Barcelona, Spain",
    "phone": "+34 667 405 535",
    "email": "gbottobrou@gmail.com",
}

# =====================================================================================
st.title("Sports Job Application Tailor")
st.caption(
    "Paste a sports job description (Analytics, Management, or Law/Governance). "
    "Built from the Dynamic Adaptation Engine in this folder's CLAUDE.md — the angle "
    "changes per job, never one generic CV for everything."
)

jd = st.text_area("Job description", height=220, placeholder="Paste the full job posting here...")

st.caption("Portfolio screenshots for this application (Wyscout clips, the NFL dashboard, the LinkedIn post...) — optional, nothing is saved once you close the app.")
shots = st.file_uploader("Add screenshots", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
if shots:
    shot_cols = st.columns(4)
    for i, f in enumerate(shots):
        with shot_cols[i % 4]:
            st.image(f, use_container_width=True, caption=f.name)

col1, col2 = st.columns([2, 1])
with col1:
    if jd.strip():
        suggested = suggest_track(jd)
        st.caption(f"Suggested track based on the text: **{suggested}**")
    else:
        suggested = "Sports Analytics"

track = st.radio("Track", list(CONTENT.keys()), index=list(CONTENT.keys()).index(suggested), horizontal=True)

go = st.button("Generate application", type="primary")

if go:
    if not jd.strip():
        st.warning("Paste a job description first so the output can actually be tailored, not generic.")
    else:
        c = CONTENT[track]
        kws = matched_keywords(jd, track)
        color = TRACK_COLOR[track]

        st.markdown(f'<span class="gp-track" style="background:{color};">{track}</span>', unsafe_allow_html=True)
        if kws:
            st.caption("Matched from the job description: " + ", ".join(sorted(set(kws))))

        st.header("CV Header")
        st.markdown(
            f'<div class="gp-block"><b>{HEADER["name"]}</b><br>{HEADER["location"]} · {HEADER["phone"]} · '
            f'{HEADER["email"]}<br><br>{c["title_line"]}</div>',
            unsafe_allow_html=True,
        )

        st.header("About Me")
        st.markdown(f'<div class="gp-block">{md_bold(c["about"])}</div>', unsafe_allow_html=True)

        st.header("Skills (grouped, for the CV body)")
        skills_html = ""
        for group, items in c["skills"]:
            skills_html += f"<b>{group}:</b> {' • '.join(items)}<br><br>"
        st.markdown(f'<div class="gp-block">{skills_html}</div>', unsafe_allow_html=True)

        st.header("ATS Keyword Line (paste into \"Skills\" fields / keyword scanners)")
        st.caption(
            "Plain comma-separated list, no bullets or pipes — this is the format ATS parsers and "
            "online application \"skills\" text boxes actually expect."
        )
        st.code(c["ats_line"], language=None)

        st.header("Experience (framed for this track)")
        st.markdown(f'<div class="gp-block">{md_bold(c["experience"])}</div>', unsafe_allow_html=True)

        st.header("Project to Feature")
        st.markdown(f'<div class="gp-block">{md_bold(c["project"])}</div>', unsafe_allow_html=True)

        st.header("Cover Letter")
        cover = (
            f"Dear Hiring Manager,\n\n"
            f"{c['cover_opening']}\n\n"
            f"{c['about']}\n\n"
            f"I would welcome the opportunity to bring this combination to your team.\n\n"
            f"Kind regards,\n{HEADER['name']}"
        )
        st.text_area("Draft (copy/edit freely)", value=cover, height=260)

        if track == "Sports Law & Governance":
            st.error(
                "This track has placeholders. Do not send an application built from it until you've "
                "added your real legal background where marked above — sending it as-is would overstate "
                "your experience, which the playbook explicitly forbids (Rule 51)."
            )
else:
    st.info("Paste a job description above, pick or confirm the track, then generate.")
