#!/usr/bin/env python3
"""
Stahuje veřejná data z Fantasy Premier League API a ukládá je jako štíhlá CSV.
Bez externích závislostí - jen standardní knihovna Pythonu.
"""
import csv, json, os, sys, urllib.request
from datetime import datetime, timezone

BASE = "https://fantasy.premierleague.com/api"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

PLAYER_FIELDS = [
    "id", "web_name", "first_name", "second_name", "team", "element_type",
    "now_cost", "cost_change_start", "cost_change_event",
    "status", "chance_of_playing_next_round", "news", "news_added",
    "form", "total_points", "points_per_game", "minutes", "starts",
    "selected_by_percent", "transfers_in_event", "transfers_out_event",
    "goals_scored", "assists", "clean_sheets", "goals_conceded",
    "yellow_cards", "red_cards", "saves", "bonus", "bps",
    "influence", "creativity", "threat", "ict_index",
    "expected_goals", "expected_assists", "expected_goal_involvements",
    "expected_goals_per_90", "expected_assists_per_90",
    "expected_goal_involvements_per_90", "expected_goals_conceded_per_90",
    "defensive_contribution", "defensive_contribution_per_90",
    "penalties_order", "corners_and_indirect_freekicks_order",
    "direct_freekicks_order", "value_season", "ep_this", "ep_next",
]
TEAM_FIELDS = [
    "id", "name", "short_name", "position", "played", "win", "draw", "loss",
    "points", "form", "strength", "strength_overall_home", "strength_overall_away",
    "strength_attack_home", "strength_attack_away",
    "strength_defence_home", "strength_defence_away",
]
FIXTURE_FIELDS = [
    "id", "event", "kickoff_time", "team_h", "team_a",
    "team_h_score", "team_a_score", "team_h_difficulty", "team_a_difficulty",
    "finished", "started", "minutes",
]


def get(path):
    req = urllib.request.Request(
        BASE + path, headers={"User-Agent": "fpl-data-snapshot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def write_csv(name, rows, fields):
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})
    print(f"  {name}: {len(rows)} řádků")


def main():
    print("Stahuji bootstrap-static ...")
    boot = get("/bootstrap-static/")
    print("Stahuji fixtures ...")
    fixtures = get("/fixtures/")

    events = boot.get("events", [])
    cur = next((e for e in events if e.get("is_current")), None)
    nxt = next((e for e in events if e.get("is_next")), None)

    write_csv("players.csv", boot.get("elements", []), PLAYER_FIELDS)
    write_csv("teams.csv", boot.get("teams", []), TEAM_FIELDS)
    write_csv("fixtures.csv", fixtures, FIXTURE_FIELDS)

    # snímek hráčů pro aktuální kolo -> historie sezóny
    if cur:
        write_csv(
            os.path.join("history", "players_gw%d.csv" % cur["id"]),
            boot.get("elements", []),
            PLAYER_FIELDS,
        )

    meta = {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "current_event": cur["id"] if cur else None,
        "next_event": nxt["id"] if nxt else None,
        "next_deadline_utc": nxt["deadline_time"] if nxt else None,
        "player_count": len(boot.get("elements", [])),
        "injured_or_doubtful": sum(
            1 for p in boot.get("elements", []) if p.get("status") != "a"
        ),
    }
    with open(os.path.join(OUT, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Hotovo:", json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("CHYBA:", e, file=sys.stderr)
        sys.exit(1)
