import os
import math
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

SHOTS_COLUMNS = [
    "GRID_TYPE", "GAME_ID", "GAME_EVENT_ID", "PLAYER_ID", "PLAYER_NAME",
    "TEAM_ID", "TEAM_NAME", "PERIOD", "MINUTES_REMAINING", "SECONDS_REMAINING",
    "EVENT_TYPE", "ACTION_TYPE", "SHOT_TYPE", "SHOT_ZONE_BASIC", "SHOT_ZONE_AREA",
    "SHOT_ZONE_RANGE", "SHOT_DISTANCE", "LOC_X", "LOC_Y", "SHOT_ATTEMPTED_FLAG",
    "SHOT_MADE_FLAG", "GAME_DATE", "HTM", "VTM",
]

SEASON = "2025-26"

PLAYERS_COLUMNS = ["PLAYER_ID", "FG_PCT", "FG3_PCT", "SEASON"]

def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def get_latest_shot_date():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(game_date) FROM shots")
            return cur.fetchone()[0]
    finally:
        conn.close()


def _clean_value(col, val):
    if isinstance(val, float) and math.isnan(val):
        return None
    if col == "GAME_DATE" and val is not None:
        return datetime.strptime(str(int(val)), "%Y%m%d").date()
    if col == "GAME_ID":
        return str(val).zfill(10)
    return val


def insert_shots(shots):
    if not shots:
        return
    columns = [c.lower() for c in SHOTS_COLUMNS]
    sql = f"""
        INSERT INTO shots ({", ".join(columns)})
        VALUES %s
        ON CONFLICT (game_id, game_event_id) DO NOTHING
    """
    values = []
    #The entire row of values from 1 shot become 1 tuple of values, values list contain multiple shots.
    for shot in shots:
        values.append(tuple(_clean_value(col, shot.get(col)) for col in SHOTS_COLUMNS))
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, values)
        conn.commit()
    finally:
        conn.close()

def upsert_player_stats(players):
    if not players:
        return

    columns = [c.lower() for c in PLAYERS_COLUMNS]

    sql = f"""
        INSERT INTO player_stats ({", ".join(columns)})
        VALUES %s
        ON CONFLICT (player_id) DO UPDATE SET
            fg_pct = EXCLUDED.fg_pct,
            fg3_pct = EXCLUDED.fg3_pct,
            season = EXCLUDED.season
    """
    values = []
    for player in players:
        values.append(tuple(
            SEASON if col == "SEASON" else _clean_value(col, player.get(col))
            for col in PLAYERS_COLUMNS
        ))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, values)
        conn.commit()
    finally:
        conn.close()

def fetch_all_shots():
    conn = get_connection()
    columns = [c.lower() for c in SHOTS_COLUMNS]
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(columns)} FROM shots")
            rows = cur.fetchall()
    finally:
        conn.close()

    result = []
    for row in rows:
        one_shot = dict(zip(SHOTS_COLUMNS, row))
        result.append(one_shot)
    return result

def fetch_all_player_stats():
    conn = get_connection()
    columns = [c.lower() for c in PLAYERS_COLUMNS]
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(columns)} FROM player_stats")
            rows = cur.fetchall()
    finally:
        conn.close()

    result = {}
    for row in rows:
        player_id, fg_pct, fg3_pct, season = row
        result[player_id] = {"FG_PCT": fg_pct, "FG3_PCT": fg3_pct}

    return result
