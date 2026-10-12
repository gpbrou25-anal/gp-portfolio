# Team Scouting Form & Metric Hierarchy

**What this is:** a reference you read before you look at a team, not a tool that outputs a verdict. It exists to answer one question every time you sit down with the data: *what am I actually focusing my analysis on, and how much should I trust each number I'm looking at.* It is built from how real scouting departments and analytics groups actually work — not a generic "top 10 stats" list.

**How to use it — the one rule that matters:** every section ends in a **judgment call that's yours to make**, not a score the data hands you. That's deliberate. The whole point of combining data with scouting is that neither one alone is trustworthy. Treat every number below as evidence for a case you're building, not a verdict.

---

## 1. The three inputs real evaluators combine

Every level of football scouting — high school, NCAA, NFL — runs on some version of the same three-legged stool. Weight shifts by level, but none of the three ever disappears.

| Input | What it is | HS | NCAA | NFL |
|---|---|---|---|---|
| **The Eye** | Traits-based film grading — a human watching and rating specific physical/technical/mental traits | Dominant — almost the only input; measurables (40 time, camps like Rivals/Under Armour) + live evaluation | Still dominant, now paired with more film volume and recruiting-service composites (247Sports, Rivals star ratings blend multiple scouts) | Formalized into departments — area scouts file written reports, cross-checked by regional and national scouts before the GM sees them |
| **The Data** | Aggregated statistical performance, adjusted for context | Minimal — small sample, poor competition-level data, rarely trustworthy on its own | Real but noisy — PFF College grades exist, but competition level varies enormously between conferences | Mature — PFF grades every player on every play; EPA, DVOA, NGS all exist and are trusted enough to sit in the same room as scouts |
| **Context** | Scheme fit, competition level, sample size, injury/role history | Everything is context here — a HS stat line means almost nothing without knowing who they played | Conference strength, scheme, teammates around them | Opponent adjustment (this is literally what DVOA does — more on that below), scheme change, coordinator continuity |

**The judgment call:** the earlier in a player's/team's career you are, the more weight The Eye and Context carry over The Data, because the data simply isn't reliable yet. You're building an NFL-level diagnostic (mature data), so the temptation is to over-trust the numbers — the discipline is remembering PFF and DVOA both exist *because* raw stats weren't good enough on their own, and even they get contradicted by film sometimes.

---

## 2. How the pros actually grade — the two real scales worth knowing

You don't need to invent a grading system. Two real ones already exist, and knowing how they work tells you what "good analysis" looks like structurally.

**PFF's grading scale** (per-play, then aggregated): every player gets **-2.0 to +2.0** on every single play relative to what was *expected* given the situation — 0 is "did your job," not "did nothing." These get normalized to a 0-100 season grade: **90+ = elite, 85-89 = Pro Bowl caliber, 70-84 = solid starter, 60-69 = backup quality, below 60 = replaceable**, with 60 as the average baseline. The core idea worth stealing: **grade relative to what the situation demanded, not the raw outcome.** A 2-yard gain on 3rd-and-1 and a 2-yard gain on 3rd-and-10 are not the same play, even though the stat line looks identical.

**The 20-80 scouting scale** (traits, not plays — baseball's scale, adopted by football scouts): 20=poor, 40=below average, **50=average**, 60=plus, 70=plus-plus, 80=elite. Real scouting departments break each position into ~8 graded traits and weight them differently — e.g., **explosiveness is weighted heavily because it can't be developed; processing/instincts get weighted lower because a player can actually improve there over time.** The idea worth stealing: **not every trait matters equally, and some are coachable while others aren't** — your metric hierarchy below follows the same logic.

**Football Outsiders' DVOA** (team/unit level): every play is compared to a league-average baseline **for that specific situation** — down, distance, score, opponent quality. It's a percentage: +10.0% DVOA = 10% better than average; -20.0% = 20% worse. This is the origin of the same idea already locked into your build: **raw yards or raw EPA without opponent adjustment can be misleading — a good number against a bad defense isn't the same as a good number against a good one.**

---

## 3. Metric hierarchy — what to trust first, by family

This is the "standings" — synthesized directly from the grill decisions already locked into `METRICS_CATALOG.md`, not a new invented ranking. When two metrics disagree, this is the order to resolve the conflict in.

| Family | Trust first | Trust second | Treat as descriptive only (not a grade) |
|---|---|---|---|
| **QB** | EPA/dropback (situation-adjusted, the real headline) | CPOE (isolates accuracy from throw difficulty) | Time-to-throw, intended air yards — this is *style*, quick-game vs. down-field, never a quality signal |
| **O-Line** | QB hits allowed/generated (happens far more often than sacks, better protection-quality proxy) | Sack-fault split (QB vs. O-line) | Raw sacks allowed alone — too rare an event, too noisy |
| **RB** | % carries 4+ yards (consistency) | Explosive-run rate — flag it, don't credit the RB alone without film, a busted defensive assignment looks identical in the box score | Raw YPC — one long run distorts it completely |
| **WR/TE** | Separation % (the actual skill signal) | Air-yards share (role/trust — a *different* question, not a better or worse one) | YAC-over-expected — a third, separate skill (after-the-catch), don't blend it into the other two |
| **CB/Secondary** | Yards allowed per target (captures real damage) | Completion % allowed (more intuitive, less precise) | — |
| **Team overall** | Turnover margin, EPA differential (offense minus defense) | Point differential (the results-level summary) | Penalties/game — real signal, but pair with record before concluding anything (a penalty-heavy team that's still winning is a different story than one that's losing because of it) |

**The judgment call this table doesn't make for you:** what happens when the "trust first" metric and the "trust second" metric point in *opposite* directions for the same team? That disagreement is usually the most interesting thing in the whole report — it's exactly the kind of thing worth watching on film before writing anything down.

---

## 4. The scouting form itself

One of these per team, per week you check in. Deliberately short — a form you can actually fill out in ten minutes while looking at the dashboard, not a report that takes an hour to produce.

```
TEAM: ______________          WEEK: _____          RECORD: _____

IDENTITY
  Offensive scheme / philosophy: ___________________________
  Defensive scheme / philosophy: ___________________________
  Head coach tenure / new-system year?  Y / N
  Notable injuries (starter → backup at):  ___________________

STATISTICAL PROFILE  (fill from the "trust first" column, section 3)
  Offense:  EPA/play ____   Success rate ____   Trend (↑/↓/flat)
  Defense:  EPA/play allowed ____   Success rate allowed ____
  Turnover margin: ____        Point differential: ____
  Where does the correlation check (Overview tab) say this team is
  over- or under-performing its underlying numbers?  ___________

TRAITS ASSESSMENT  (this is where you write, not the data)
  What did you actually SEE on film that the stats don't capture?
  _____________________________________________________________
  Does play-calling tendency (motion/RPO/play-action %) match what
  you'd expect from the stated offensive identity above?  Y / N
  If not, why not?  ___________________________________________

SITUATIONAL FLAGS
  Hot/cold start — is the trend real or a schedule artifact?
  _____________________________________________________________
  Any metric here still running on a small sample (<5 attempts)?
  _____________________________________________________________

CONFIDENCE LEVEL ON THIS READ:  Low / Medium / High
  Why: _________________________________________________________
```

---

## 5. What to actually focus on first (so you're not staring at 60 columns)

In order, every time:

1. **Point differential + turnover margin** — is this team's record earned or lucky, in one glance
2. **Offense EPA vs. Defense EPA allowed** (the Overview quadrant) — which side of the ball is actually carrying this team
3. **The one "trust first" metric** for whichever position group prompted you to look in the first place
4. **The correlation check** — is anything you're about to rely on this week actually tracking results, or still noise
5. *Only then* — the deeper individual player cuts (QB/RB/WR/DB tabs), once the team-level picture already makes sense

If you find yourself scrolling the "All metrics (raw)" tab before doing 1-4, that's the analysis-paralysis trap this whole form exists to prevent.

---

*Reminder from the top: this is a helper. If the form and the film disagree, the film is not automatically wrong — that disagreement is the actual scouting job.*
