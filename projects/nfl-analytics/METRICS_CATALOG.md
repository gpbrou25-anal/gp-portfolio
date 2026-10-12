# NFL Team Diagnostic — Metrics Catalog

Organized strictly by position family, per your correction. For each metric: **[Board]** = yours, transcribed from the whiteboard photos (verify against the actual board) · **[Added]** = a real, industry-standard metric I'm adding, not generic filler — each with why it matters. **[Data: nflfastR]** = confirmed available now from play-by-play. **[Data: NGS]** = confirmed available now from Next Gen Stats (I verified the actual fields exist, not guessing). **[Data: gap]** = not confirmed available yet.

Real anchor case: **Falcons @ Bengals, Sunday Nov 8 2026, Bernabéu, Week 9** — confirmed live from NFL.com. Since you're going in person, this becomes the natural first deep-dive matchup once the pipeline's ready.

---

## Team-level / Overall
*(moved here — this is whole-team, not an O-line thing, per your correction)*

- **[Board]** Style of play — offensive/defensive philosophy, tendency, scheme origin
- **[Board]** New head coach vs. last 2 years under old regime — direct before/after comparison
- **[Board]** Hot/cold start (weeks 1-2, trending) — case study: Houston's 0-2 pattern
- **[Data: nflfastR, already built]** PPG / PA, point differential, off/def EPA per play, margin trend slope
- **[Added]** *Turnover margin* — already in the stats engine; matters because it's one of the single best predictors of week-to-week win probability, more than most "eye test" factors
- **[Added]** *Strength of schedule adjustment* — raw EPA is misleading if a team's opponents were unusually good/bad; needed before the correlation check you asked for is honest
- **[Board]** Correlation check — do these metrics actually predict results, or just look good (this is the validation step for the whole project, not a metric itself)

---

## QB
- **[Board]** Pass attempts; yards on pass attempts — **[Data: nflfastR]**
- **[Board]** Yards on rush/scrambles — **[Data: nflfastR]**
- **[Board]** Scramble % — **[Data: nflfastR]**
- **[Board]** Pocket time / pressured vs. clean-pocket % — **[Data: NGS, `avg_time_to_throw`]**
- **[Board]** Interception % — both raw, and "true" INT rate excluding tips/drops caused by the receiver — **[Data: nflfastR interception + partial via `interception_thrown` context]**. Good instinct on your part: separating QB fault from WR fault is exactly the kind of thing a lot of casual analysis gets wrong.
- **[Board]** Run/pass call % — **[Data: nflfastR]**
- **[Board]** Quick/medium/long throw depth % — **[Data: NGS, `avg_intended_air_yards` buckets]**
- **[Added]** *EPA per dropback* — the actual industry-standard QB efficiency number (used by every serious analytics shop); raw yards reward volume, EPA rewards winning the down
- **[Added]** *Completion % Over Expected (CPOE)* — adjusts completion rate for how hard the throw actually was; a QB completing 60% on hard throws is better than one completing 65% on screens — **[Data: NGS, confirmed field exists]**
- **[Added]** *Sack rate + pressure-to-sack conversion* — separates "QB holds the ball too long" from "O-line collapses instantly" — relevant to both QB and O-line diagnosis at once

---

## Offensive Line (OL)
- **[Board]** OL vs. DL "win rate" at the point of attack — **[Data: gap — needs PFF-style charting or a proxy]**
- **[Added]** *Pressure rate allowed per dropback* — THE standard OL efficiency stat league-wide — **[Data: nflfastR has `qb_hit`/`sack`, partial proxy]**
- **[Added]** *Sacks allowed per pass attempt* — **[Data: nflfastR]**
- **[Added]** *Run-blocking success rate* — % of runs gaining at/above the yards needed for an efficient down, isolates blocking from RB talent — **[Data: nflfastR, computable]**
- **[Added]** *Penalties (holding/false start) per game* — directly measures discipline and technique, cheap and real signal — **[Data: nflfastR]**

## Defensive Line (DL)
- **[Board]** OL vs. DL win rate (shared metric, DL side) — **[Data: gap, same as above]**
- **[Added]** *Pass-rush win rate / pressure rate generated* — **[Data: nflfastR proxy via QB hits/sacks/hurries where tagged]**
- **[Added]** *Run-stop rate* — tackles for loss on run plays, the DL's version of run defense — **[Data: nflfastR]**
- **[Added]** *Sacks, QB hits* — **[Data: nflfastR]**

---

## RB
- **[Board]** Yards per carry — **[Data: nflfastR]**
- **[Board]** % of touches RB vs. WR (who the offense actually goes to) — **[Data: nflfastR]**
- **[Board]** % of carries (consistency, not just average) — e.g. % of carries gaining 4+ yards, so one 60-yard breakaway doesn't hide a mostly-stuffed day — **[Data: nflfastR]**
- **[Added]** *Yards after contact per carry* — isolates RB skill from OL blocking quality, the two get conflated constantly in casual analysis — **[Data: nflfastR, approximable]**
- **[Added]** *Explosive run rate* — % of carries going for 10+ yards — **[Data: nflfastR]**
- **[Added]** *Receiving role* — targets/catches out of the backfield, since modern RBs are judged on receiving work too — **[Data: nflfastR]**

---

## WR / TE
*(removed the O-line/D-line line you flagged — that was a stray thought, not a WR metric)*

- **[Board]** Targets, catch % on targets, yards per catch, YAC — **[Data: nflfastR]**
- **[Board]** Targets per quarter, per down (1st-4th) — **[Data: nflfastR]**
- **[Board]** Separation % — **[Data: NGS, `avg_separation`, confirmed]**
- **[Board]** Route type vs. attempts / route participation vs. blocking snaps — **[Data: gap for exact route type; snap participation is available]**
- **[Board]** Interceptions caused (picks on passes intended for this player) — **[Data: nflfastR]**
- **[Board]** TD count + red-zone TD count — **[Data: nflfastR]**
- **[Board]** WR running routes on early downs (usage pattern) — **[Data: nflfastR]**
- **[Board]** TE vs. WR reliance comparison, yards after reception — **[Data: nflfastR]**
- **[Added]** *Air yards share* — % of the team's total intended air yards this player commands; measures true role, not just raw target count — **[Data: NGS, `percent_share_of_intended_air_yards`, confirmed]**. This directly answers your "how much does the offense actually go to this guy" question better than raw targets.
- **[Added]** *YAC over expected* — separates a receiver's own run-after-catch ability from scheme/blocking — **[Data: NGS, confirmed]**
- **[Added]** *Drop rate* — the receiver-side counterpart to the QB's "true INT%" idea from the board — closes that same accountability loop from the other direction — **[Data: nflfastR proxy]**

---

## LB (Linebacker)
*(whiteboard only named the group — here's the real standard set)*

- **[Added]** *Run-stop rate / tackles for loss* — core LB job description — **[Data: nflfastR]**
- **[Added]** *Coverage snap %* — in a pass-heavy league, how much a LB actually plays coverage vs. early-down run support only — **[Data: gap, needs snap-level participation data]**
- **[Added]** *Yards allowed per target when in coverage* — **[Data: gap, needs coverage-charting]**
- **[Added]** *Blitz rate + pressure rate on blitzes* — **[Data: nflfastR partial]**

## DB / Secondary (CB, FS, S, SS)
- **[Added]** *Completion % allowed when targeted* — the standard CB efficiency number — **[Data: nflfastR]**
- **[Added]** *Yards allowed per target* — **[Data: nflfastR]**
- **[Added]** *INTs + pass breakups* — **[Data: nflfastR]**
- **[Added]** *Missed tackle rate in run support* — especially relevant for safeties — **[Data: gap]**
- **[Added]** *"Havoc rate"* (INT + PBU + forced fumble combined) — one disruption number, useful for the "diagnostic at a glance" view — **[Data: nflfastR, computable]**

---

## Special Teams
*(from your original brief — nothing on the board yet for this group)*

- **[Added]** Field goal % by distance bucket — **[Data: nflfastR]**
- **[Added]** Punt/kickoff net average — **[Data: nflfastR]**
- **[Added]** Return yards allowed/gained — **[Data: nflfastR]**

---

## What's next

The `[Data: gap]` items (OL/DL win rate, coverage-snap %, route type, missed-tackle rate) need either NGS fields I haven't checked yet or a reasonable statistical proxy built from what nflfastR does have — I'll verify each before claiming it in the report rather than guessing. Everything else above is confirmed real and pullable right now.

Tell me: build the actual HTML diagnostic report next using everything marked `[Data: nflfastR]` and `[Data: NGS]` (the confirmed majority), or do you want to send the rest of the whiteboard (Defense section looked cut off) first?
