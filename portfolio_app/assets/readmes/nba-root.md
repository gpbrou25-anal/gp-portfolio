# NBA Analytics Portfolio

Donovan Mitchell averages 27.9 points per game. Against the league's five best defenses, he averages 22.3. That's a 5.6-point drop — the kind of detail that decides playoff series and max-contract decisions.

This portfolio is a collection of basketball questions answered with data. Not techniques in search of a problem, not a textbook redoing somebody else's findings — actual questions a GM, a coach, or a curious fan would ask, with the numbers underneath.

Every project here ships the same way:

- **One clear question.** Stated upfront. No abstract.
- **Real data, pulled live.** Straight from the official NBA Stats API, no scraping, no toy datasets.
- **Charts that hold up on their own.** Each one labeled so a basketball person who's never opened a Python file can read it.
- **An honest write-up.** Specific players, specific numbers, specific opinions. Caveats included.

---

## Projects

### [01 — Volume vs. Elite Defenses](projects/01-volume-vs-elite-defenses/)
*Which star scorers actually keep scoring when the defense gets serious?*

I looked at the 15 highest-volume scorers in the 2025-26 NBA regular season and split their games by opponent defense quality. The league-average drop against top-5 defenses is only about 1 point per game — boring. The variance is the story.

**The names that matter, ranked by what the data says:**

- **Donovan Mitchell drops 5.6 PPG.** The clearest contract-value flag in the dataset.
- **Shai Gilgeous-Alexander doesn't drop at all** (31.1 → 31.2). His game is matchup-proof.
- **Deni Avdija scores MORE against elite defenses** (24.2 → 26.1). The most surprising finding of the whole project — and probably an undervalued contract waiting to happen.

→ [Read the full analysis](projects/01-volume-vs-elite-defenses/README.md) (slope chart, player × tier heatmap, scoring-vs-winning scatter, eight-player breakdown)

### [02 — Are the New York Knicks Real NBA Finals Contenders in 2026?](projects/02-knicks-contender-2026/)
*Winning 50 games doesn't make you a contender. Does the way the Knicks win match the profile of teams that actually go all the way?*

I built a contender framework around the indicators that historically separate championship teams from good-but-not-enough teams — closing tight games, defending without fouling, winning on the road, holding up in Q3, not depending on one player in every big moment — and ran the Knicks through it.

**The key findings:**

- **Clutch record: 18–2.** Last 5 minutes, margin ≤5 — the NBA's own definition. The most important number in the dataset.
- **Brunson Dependency Index (BDI): 39.6.** Custom metric: (Brunson PPG / Team PPG) × (USG% / 20) × 100. Real reliance — but manageable. KAT averages 26.8 PPG when Brunson is held under 15.
- **KAT is a structural mismatch.** No opponent has a clean answer for his combination of size, positioning, and shooting range. That doesn't get solved between games in a series.
- **Q3 is their signature — and their Year 1 vulnerability.** Overall Q3 differential: +1.8. Against top-10 opponents: –0.4. The clearest argument for why this team gets better from here.
- **Mike Brown's system reaching the Finals in Year 1 is above expected trajectory.** Most new coaching systems see their largest jump in Year 2. This team arrived before that.

→ [Read the full analysis](projects/02-knicks-contender-2026/README.md) (16 charts — efficiency ratings, clutch splits, radar comparison, Finals Games 1–5 breakdown, full written report)

---

## Coming next

- **03 — Injury return curves.** When a star comes back from a 15+ game absence, how many games before their efficiency returns to baseline?
- **04 — Contract value (production per dollar).** Cross-reference cap hit with on-court impact. Who's the league's biggest bargain and the biggest overpay?

Same structure, same standard, one question at a time.

---

## How to reproduce any project

```bash
git clone https://github.com/gpbrou25-anal/NBA-Analytics-Portfolio.git
cd NBA-Analytics-Portfolio/projects/01-volume-vs-elite-defenses
pip install -r requirements.txt
python src/analysis.py
```

Every project folder has its own `README.md`, `requirements.txt`, and `src/`. Outputs land in `data/` (CSV) and `figures/` (PNG).

---

## Stack

Python, pandas, matplotlib, `nba_api`. Kept deliberately simple — the point is the basketball thinking, not the toolchain.
