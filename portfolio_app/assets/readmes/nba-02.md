# Project 02 — Are the New York Knicks a Real NBA Finals Contender in 2026?

**Season:** 2025–26 NBA · **Coach:** Mike Brown (Year 1) · **Data:** NBA.com/stats, Basketball-Reference, Cleaning the Glass

---

## The Question

The Knicks entered the 2025–26 season with real championship expectations — a new head coach in Mike Brown, an upgraded roster built around Jalen Brunson and Karl-Anthony Towns, and a fanbase that hadn't seen a title in over 50 years. The question this project investigates is not whether they're good. It's whether the *way* they win matches the profile of teams that actually go all the way.

---

## Objective

Winning 50 games doesn't make you a contender. Plenty of 50-win teams lose in round two. The goal was to identify whether the Knicks showed the specific characteristics that championship teams share — closing tight games, defending without fouling, winning on the road, holding up in the third quarter, and not depending on one player in every big moment.

---

## Data & Metrics

| Category | Metrics |
|---|---|
| Record & Efficiency | Win %, Net Rating, Home/Away splits |
| Offense | Offensive Rating, True Shooting %, Half-Court ORtg, Shot Zone Efficiency |
| Defense | Defensive Rating, Individual FG% Suppression, Opponent FT Rate, Q3 DRtg |
| Clutch | Last-5-min ≤5 pts record, Clutch FG%, Forced Turnover Rate |
| Star Reliance | Brunson Dependency Index (BDI) = (Brunson PPG / Team PPG) × (USG% / 20) × 100 |
| Situational | Q-by-Q shooting splits, Record after losses, H2H data (3 seasons) |
| Rebounding | Total Reb %, KAT matchup data vs. every opponent |
| Bench | Second-unit Net Rating, Bench scoring share, Playoff +/- |
| Turnovers | TO%, Live-ball turnover rate, Correlation with win/loss outcomes |

---

## Key Findings

- **Clutch record: 18–2.** Last 5 minutes, margin ≤5 — the NBA's own definition. The most predictive number in the dataset for a Finals run.

- **Brunson Dependency is real but manageable.** BDI of 39.6. Undefeated when Brunson scores 20+. KAT averages 26.8 PPG in games where Brunson is held under 15.

- **KAT is a structural mismatch.** No opponent has a clean answer for his combination of size, positioning, and shooting range. He posted double-double numbers against San Antonio in every significant matchup this season.

- **The defense is built on discipline.** Opponent FT rate below league average. San Antonio players shot 2–5% below their season averages when guarded by Knicks defenders. Wembanyama shot 29% in Finals Game 1.

- **Q3 is their signature — and their vulnerability.** Overall Q3 differential: +1.8. Against top-10 opponents: –0.4. A Year 1 system still calibrating. The clearest argument for why this team gets better from here.

- **Road performance exceeded the baseline.** Documented road win rate: 55%. Finals road record in San Antonio: 1–1 — the loss came in Game 3, directly reflecting the road vulnerability this project flagged as the team's biggest structural concern.

- **Run-stopping at 64% by the 5th possession** is positive but created real late-game exposure in multiple Finals games.

- **7–1 combined H2H record over the last three seasons** against San Antonio (8–1 including the NBA Cup Final). Point differential compressed from +20 in Wembanyama's first two seasons to approximately –5 this year, reflecting the Spurs' genuine development.

- **Mike Brown's Year 1 system reaching the Finals is above expected trajectory.** Most new coaching systems see their largest jump in Year 2. This team arrived before that.

---

## Charts

### Standing & Efficiency

![Win % vs. League](figures/01_win_pct_standings.png)

![Net Rating — Full League](figures/08_net_rating_league.png)

![Net Rating Among Contenders](figures/11_net_rating_contenders.png)

---

### Offense

![Offensive Rating](figures/03_offensive_rating.png)

![Offensive Profile](figures/05_offensive_profile.png)

![True Shooting %](figures/04_true_shooting.png)

![Pace vs. Net Rating](figures/14_pace_net_rating.png)

---

### Defense

![Defensive Rating](figures/06_defensive_rating.png)

![Defensive Activity](figures/07_defensive_activity.png)

---

### Situational

![Four Factors](figures/13_four_factors.png)

![Home vs. Away](figures/02_home_away_splits.png)

![Clutch Performance](figures/12_clutch_performance.png)

---

### The Full Picture

![ORtg vs. DRtg Scatter](figures/09_ortg_drtg_scatter.png)

![Radar Comparison](figures/10_radar_chart.png)

![Rankings Summary](figures/15_nyk_rankings.png)

![Final Dashboard](figures/16_final_dashboard.png)

---

## NBA Finals — All Five Games

*The Knicks entered the 2026 NBA Finals against the San Antonio Spurs as the higher seed. Games 1–2 at MSG, Games 3–4 in San Antonio, Game 5 back at MSG. Here is how the analytical indicators from this project tracked across the series.*

**Game 1 — Knicks 105, Spurs 95 · MSG**

San Antonio came out aggressive and built a 14-point first-half lead. The Knicks didn't panic — they ran their half-court actions, got stops in Q3, and took the lead for good in the fourth. Brunson finished with 30 points on efficient shooting, controlling pace throughout. KAT posted a double-double; his rebounding advantage over San Antonio's interior was the size mismatch this project flagged all season. Wembanyama shot 29% from the field — not luck, the result of a defensive scheme built around his left-hand drive tendency and specific help rotation timing. The Q3 comeback and the clutch-time execution in Q4 confirmed two of the project's core indicators simultaneously: the third-quarter defensive identity and the 18–2 closing record aren't regular-season noise.

**Game 2 — Knicks 105, Spurs 104 · MSG**

The best game of the series. Wembanyama was extraordinary — 27 points, 9 rebounds, 4 blocks, the best individual performance of the Finals. The Knicks won anyway. That's the story. Brunson: 20 points, 6 assists, 5 steals — not gambling steals, positioning steals, the same read-the-passing-lane discipline that showed up in the defensive activity data all season. Bridges: 20 points. Towns: 21 and 13. Three players at 20+ in a one-possession game is the multi-star distribution model in action. The BDI analysis showed Brunson's reliance was real at 39.6, but also that Bridges and Towns were credible co-producers when the moment demanded. Game 2 was the hardest test of that claim. All three delivered.

**Game 3 — Spurs Win · San Antonio**

The road vulnerability this project identified as the team's biggest structural concern showed up directly. San Antonio's crowd, full film review of the Knicks' rotation patterns, and Wembanyama's rapid adjustment from his 29% Game 1 performance combined to produce a different game entirely. Live-ball turnovers against his length created transition opportunities that didn't exist at MSG. The Q3 defensive identity — the Knicks' +1.8 differential that held all season — cracked in a hostile road environment against a top-10 opponent (the project's documented –0.4 Q3 differential against elite competition). Spurs won. The analytical framework's most clearly stated limitation was confirmed in the same game it mattered most.

**Game 4 — Knicks Win · San Antonio, Series 3–1**

The bounce-back pattern activated immediately. The project documented the Knicks going 2–0 in the game immediately following a postseason loss — a behavioral signal built on Brunson raising his decision rate and the bench producing its cleanest stretches in response games. Both teams had fully neutralized transition by Game 4. The series became what the pace data predicted it would become: 95.5 possessions per 48 minutes, every possession equal weight, half-court execution deciding everything. The turnover control stat — 31–4 when winning the TO battle by 3 or more — was the most predictive single number in the dataset for exactly this environment, and Brunson's ball security kept the differential in the Knicks' favor. KAT's rebounding edge compounded across four games; San Antonio adjusted coverages between games but could not adjust personnel.

**Game 5 — Knicks Win, NBA Champions · MSG**

Back at MSG with a 3–1 series lead. Brunson's 100% win rate when scoring 20+ is the most direct statistical predictor for a clinching game, and he delivered again. Bridges was tasked with San Antonio's second-best offensive option and held him all night — no fouls, no gambles, no fatigue-driven positioning errors. That's what the opponent FT rate data described all season: disciplined positioning, not variance. The 18–2 clutch record meant the Knicks had already been in final-five-minutes, ≤5-point situations twenty times this year before the Finals even started. The muscle memory of that record doesn't disappear because the setting is June. The Knicks closed it out the same way they closed everything else.

---

## Conclusion

**The Knicks are a legitimate contender, built the right way.**

The defense is elite. The closer is proven. The system under Mike Brown — in Year 1 — is coherent and hard to game-plan against across a long series. KAT creates a rebounding and scoring mismatch that cannot be solved between games. Brunson is a reliable closer. Bridges is one of the best wing defenders in the league. The bench produces when it matters. And this team closes tight games — 18–2, confirmed across five Finals games.

The honest limitations: offensive rating gap against the top tier is real; Q3 vulnerability against elite opponents persists in Year 1; run-stopping at 64% creates late-game exposure. None of them disqualifying. Every championship team has limitations. The question is whether yours are manageable in the specific series you're playing. Against San Antonio in 2026, the Knicks showed they are.

---

## Files

| File | Description |
|---|---|
| `src/analysis.py` | Full Python script — all 16 charts generated here |
| `data/master.csv` | Raw team stats dataset |
| `data/contenders.csv` | Contender comparison dataset |
| `figures/` | All 16 charts (PNG) |
| `Knicks_2026_Finals_Report_v10.docx` | Full written analytical report |

---

## Data Sources

| Source | Purpose |
|---|---|
| [NBA.com/stats](https://www.nba.com/stats) | Advanced metrics, Clutch splits, Tracking, Lineups, On/Off |
| [Basketball-Reference](https://www.basketball-reference.com) | Game logs, quarterly splits, H2H game finder, shooting tables |
| [Cleaning the Glass](https://cleaningtheglass.com) | Half-court efficiency, possession-type filters |

*BDI (Brunson Dependency Index) is a custom metric derived from publicly available PPG and USG% data from NBA.com.*
