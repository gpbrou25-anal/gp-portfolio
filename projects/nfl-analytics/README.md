# NFL Team Diagnostic

Everything built so far, in one place — this got scattered across a lot of files, this is the map back to all of it.

## How to see everything (the one command that matters)

```powershell
cd "C:\Users\User\Documents\Claude\Projects\GP PATH TO DREAM JOB\Antigravity\nfl-analytics"
..\.venv\Scripts\python.exe -m streamlit run viewer_app.py
```

Opens in your browser. 10 tabs: Overview, QB, O-Line/D-Line, RB, WR/TE, LB/DB, Special Teams, Play-type tendency, By quarter, All metrics (raw), Glossary. Every family tab has curated charts (not raw CSV dumps) plus a "Raw table" expander if you want the numbers directly.

**Sidebar toggle — "With Week 3 data":** off freezes every tab at the Week 2 snapshot (`output/wk2/`), on shows the latest data available right now. Flip it back and forth on any chart to see how much a single extra game moves these small-sample numbers — that's the point of it, not just a filter.

## What each file actually is

**Reference**
- `METRICS_CATALOG.md` — every metric, organized by position family, tagged with whether it's confirmed real data, and *why* it's relevant (this is the output of the metrics grill)
- `SCOUTING_FORM.md` — the three inputs real evaluators combine, the two real grading scales (PFF, 20-80, DVOA), the metric-trust hierarchy by family, the actual per-team scouting form template, and the priority checklist for what to look at first
- `metric_glossary.py` — single source of truth for every team-level metric's plain explanation + relevance. Imported by `compute_team_ledger.py`, `viewer_app.py`'s Glossary and "All metrics" tabs, and `generate_glossary_pdf.py`, so the wording never drifts between them. Edit metrics here only.

**Compute scripts** (run any of these to refresh data after more games are played — all take an optional season argument, default 2026, and an optional second `through_week` argument that freezes a snapshot as of that week into `output/wk<N>/` instead of overwriting the live data — that's what powers the viewer's "With Week 3 data" toggle)
- `compute_team_stats.py` — team-level core: record, PPG/PA, EPA/play, turnover margin (writes to the root, not `output/`, unless snapshotting)
- `compute_full_catalog.py` — the big one: QB/OL-DL/RB/WR-TE/LB-DB team-level tables, play-type tendency, discipline & tackling
- `compute_drop_rate.py` — per-player WR/TE drop rate
- `compute_special_teams.py` — FG% by distance, punt/kickoff net, returns
- `compute_player_level.py` — individual QB/RB stats (computed directly from play-by-play, since nflverse's weekly/seasonal player file 404s for this in-progress season) + real position-split defense (DL/LB/DB via roster join). RB rushing is joined against real roster position data so mobile QBs' designed runs/scrambles land in their own `qb_rush_player_level.csv` instead of contaminating the RB file. Also pulls real NGS rushing `efficiency` (yards traveled per yard gained — the cutback/lateral-movement signal) onto the RB file.
- `compute_quarter_splits.py` — points scored/allowed, giveaways, completion % (thrown and allowed), run/pass split (offense AND what the defense faces), and EPA/play (offense AND defense allowed), each broken out Q1-Q4 (+ OT), computed directly from scoring plays and pbp. Missed-tackle % is NOT in here — PFR's missed-tackle charting is a weekly/season total, never tagged to a play or quarter, an honest gap flagged in the viewer.
- `compute_league_standings.py` — ranks all 32 teams on the six "trust first" metrics from `SCOUTING_FORM.md` §3, with the real player behind each best/worst team; feeds the **Power Sheet** artifact
- `compute_team_ledger.py` — every team-level metric across every family, flattened per team; feeds the **Team Ledger** artifact
- `generate_glossary_pdf.py` — renders `metric_glossary.py` into `METRIC_GLOSSARY.pdf`

**Viewer**
- `viewer_app.py` — the Streamlit dashboard described above. This is genuinely the only file you need to run to see everything.

**Data** (`output/` folder, plus a few generated files in the root)
- Team level: `team_discipline_and_tackling.csv`, `ol_dl_stats.csv`, `rb_stats.csv`, `wr_te_team_level.csv`, `lb_db_team_level.csv`, `special_teams.csv`, `play_type_tendency.csv` (offense identity), `defense_tendency_faced.csv` (same tags, what a defense faces), `qb_stats.csv`, `quarter_splits.csv`, `league_standings.json`, `team_ledger.json`
- Player level: `qb_player_level.csv`, `qb_rush_player_level.csv` (QB rushing, kept separate from RB data), `rb_player_level.csv` (real RBs/FBs only, includes NGS `efficiency`/cutback columns), `wr_te_player_level_ngs.csv` (one real row per player — summed/weighted from NGS's per-week rows myself, since NGS's own "week 0" season-total row is missing for ~15% of players and the raw weekly rows would otherwise chart the same player 2-4 times), `wr_te_drop_rate.csv`, `defense_player_level_by_position.csv`, `lb_db_player_level_pfr.csv` (unsplit, superseded by the position-split file above)
- `team_missed_tackle_by_position_group.csv` — the LB-vs-DB split from the grill
- `METRIC_GLOSSARY.pdf` (nfl-analytics root) — generated PDF version of the glossary, for reading off the app

## Claude.ai artifacts (separate from the Streamlit app — no server needed, iPad-friendly)

- **Scouting Clipboard** — per-team, per-week fillable scouting form (real jargon, term accordions for definitions), saves and keeps history
- **Power Sheet** — league-wide standings on the six "trust first" metrics, sortable, with reading-order guidance instead of pre-written conclusions — you find the read yourself
- **Team Ledger** — every metric, one or two teams at a time, side by side, with your own "success factors" / "the other hand" notes saved per team per week
- **Metric Glossary PDF** — one-tap save of `METRIC_GLOSSARY.pdf` to your device (uses the `downloads` capability)

Links to these live in the conversation where they were built — `/artifacts` in the terminal, or the gallery at claude.ai/code/artifacts, lists everything you've published.

## To run everything fresh, in order

```powershell
cd "C:\Users\User\Documents\Claude\Projects\GP PATH TO DREAM JOB\Antigravity\nfl-analytics"
..\.venv\Scripts\python.exe compute_team_stats.py
..\.venv\Scripts\python.exe compute_full_catalog.py
..\.venv\Scripts\python.exe compute_drop_rate.py
..\.venv\Scripts\python.exe compute_special_teams.py
..\.venv\Scripts\python.exe compute_player_level.py
..\.venv\Scripts\python.exe compute_quarter_splits.py
..\.venv\Scripts\python.exe compute_league_standings.py
..\.venv\Scripts\python.exe compute_team_ledger.py
..\.venv\Scripts\python.exe generate_glossary_pdf.py
..\.venv\Scripts\python.exe -m streamlit run viewer_app.py
```

(Then republish the Power Sheet / Team Ledger / Glossary PDF artifacts with the fresh JSON/PDF if you want them to reflect it too.)

**To freeze a new before/after snapshot next week** (e.g. once Week 4 lands and you want a Week 3 snapshot to compare it against): rerun the six scripts above that hit real data sources directly — `compute_team_stats.py`, `compute_full_catalog.py`, `compute_drop_rate.py`, `compute_special_teams.py`, `compute_player_level.py`, `compute_quarter_splits.py` — each with `2026 3` instead of `2026 2`, which writes into `output/wk3/`. The viewer's toggle currently points at `output/wk2/`; update that path in `viewer_app.py` (search "wk2") when you want the toggle to compare against a different frozen week.

## Known honest gaps (not silently skipped — just genuinely not available yet)

- **Individual O-line attribution** — not available in any free data source. Team-level proxies (already built) are the real ceiling without paid PFF-style charting.
- **Pass breakups (PBU) and forced fumbles** — not in the PFR defensive table used here. INT rate is real and shown; the full 3-way "havoc rate" from the original brief needs a data source I haven't found yet.
- **Red-zone TD count specifically** (vs. overall TD count) — in the catalog, not yet computed.
- **Route concept (slant/corner/post/etc.)** — only throw depth (short/medium/long, via NGS air yards) and play-type tendency (screen/PA/RPO/motion, via FTN) are available for free; the actual named route run is PFF-paid charting data, not in anything pulled here.
- **Missed-tackle % by quarter** — PFR's missed-tackle count is a weekly/season charting total, never tagged to an individual play (let alone a quarter) in any free source pulled here. Everything else on the By-quarter tab (scoring, giveaways, completion %, play-type, EPA) comes straight from play-by-play and genuinely can be split by quarter; missed tackles can't be, honestly, without paid per-play charting.

## Where this is going next

Once you've spent real time in the viewer and the artifacts: build the actual HTML diagnostic report (same visual system as your other projects) + the LinkedIn PDF slide version, using everything confirmed real above. Not started yet — waiting on your read of the data first.
