"""
Full per-team metric ledger — every team-level metric across every family,
in one flat structure per team, each tagged with what it is (explanation)
and why it matters (relevance) from the shared metric_glossary module, so
this, viewer_app.py's Glossary tab, and its "All metrics" tab never drift
apart.

This does NOT rank teams or pick winners — that's the "Team Ledger" artifact's
whole point: give the reader every number + what it means, let them build
their own read of a team or a head-to-head.

Run with: python compute_team_ledger.py
Writes: output/team_ledger.json
"""
import json
import pandas as pd
from metric_glossary import METRIC_META

OUT = "output"


def main():
    team_stats = pd.read_csv("team_stats_2026.csv").set_index("team")
    disc = pd.read_csv(f"{OUT}/team_discipline_and_tackling.csv").set_index("team")
    qb = pd.read_csv(f"{OUT}/qb_stats.csv").set_index("team")
    oldl = pd.read_csv(f"{OUT}/ol_dl_stats.csv").set_index("team")
    rb = pd.read_csv(f"{OUT}/rb_stats.csv").set_index("team")
    wr_te = pd.read_csv(f"{OUT}/wr_te_team_level.csv").set_index("team")
    lb_db = pd.read_csv(f"{OUT}/lb_db_team_level.csv").set_index("team")
    special = pd.read_csv(f"{OUT}/special_teams.csv").set_index("team")
    tendency = pd.read_csv(f"{OUT}/play_type_tendency.csv").set_index("team")
    def_tendency = pd.read_csv(f"{OUT}/defense_tendency_faced.csv").set_index("team")
    split = pd.read_csv(f"{OUT}/team_missed_tackle_by_position_group.csv")
    drops = pd.read_csv(f"{OUT}/wr_te_drop_rate.csv")

    lb_split = split[split["position_group"] == "LB"].set_index("team")["missed_tackle_pct"].rename("lb_missed_tackle_pct")
    db_split = split[split["position_group"] == "DB"].set_index("team")["missed_tackle_pct"].rename("db_missed_tackle_pct")

    team_drops = drops.groupby("team").agg(d=("drops", "sum"), t=("targets", "sum"))
    team_drops["drop_rate_pct"] = (team_drops["d"] / team_drops["t"] * 100).round(1)
    team_drops = team_drops["drop_rate_pct"]

    sources = {
        "team_stats": team_stats, "discipline": disc, "qb_stats": qb, "ol_dl": oldl,
        "rb_stats": rb, "wr_te": wr_te, "lb_db": lb_db, "special_teams": special,
        "tendency": tendency, "def_tendency": def_tendency, "missed_tkl_split": pd.concat([lb_split, db_split], axis=1),
        "wr_drops": team_drops.to_frame(),
    }

    teams = sorted(team_stats.index.unique())

    # several glossary metrics are genuinely player-level concepts (NGS air-yards
    # share/cushion, QB/defense player-level splits) with no team-level rollup
    # computed in this ledger — register each source key with no matching
    # columns so the ledger honestly reports them as unavailable per team
    # instead of crashing on the missing key
    for _missing_src in ("wr_te_ngs", "qb_player_level", "defense_player_level",
                          "defense_pbu", "defense_hustle", "lb_db_pfr"):
        sources[_missing_src] = pd.DataFrame(index=teams)

    ledger = {}
    for team in teams:
        row = {}
        for key, family, label, simple, expl, rel, src in METRIC_META:
            df = sources[src]
            if team in df.index and key in df.columns:
                val = df.loc[team, key]
                if hasattr(val, "iloc"):
                    val = val.iloc[0]
                if pd.isna(val):
                    row[key] = None
                elif pd.api.types.is_number(val):
                    row[key] = float(val)
                else:
                    row[key] = val
            else:
                row[key] = None
        ledger[team] = row

    meta_out = [{"key": k, "family": f, "label": l, "simple": s2, "explanation": e, "relevance": r} for (k, f, l, s2, e, r, s) in METRIC_META]

    out = {"teams": teams, "metric_meta": meta_out, "ledger": ledger}
    with open(f"{OUT}/team_ledger.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Wrote {OUT}/team_ledger.json — {len(teams)} teams, {len(METRIC_META)} metrics each")


if __name__ == "__main__":
    main()
