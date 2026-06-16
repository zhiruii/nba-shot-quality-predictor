CREATE TABLE IF NOT EXISTS shots (
    id BIGSERIAL PRIMARY KEY,
    grid_type TEXT,
    game_id TEXT NOT NULL,
    game_event_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    player_name TEXT,
    team_id BIGINT,
    team_name TEXT,
    period INTEGER,
    minutes_remaining INTEGER,
    seconds_remaining INTEGER,
    event_type TEXT,
    action_type TEXT,
    shot_type TEXT,
    shot_zone_basic TEXT,
    shot_zone_area TEXT,
    shot_zone_range TEXT,
    shot_distance INTEGER,
    loc_x INTEGER,
    loc_y INTEGER,
    shot_attempted_flag SMALLINT,
    shot_made_flag SMALLINT,
    game_date DATE,
    htm TEXT,
    vtm TEXT,
    fg_pct REAL,
    fg3_pct REAL,
    UNIQUE (game_id, game_event_id)
);

CREATE TABLE IF NOT EXISTS player_stats (
    player_id INTEGER PRIMARY KEY,
    player_name TEXT,
    fg_pct REAL,
    fg3_pct REAL,
    season TEXT
);
