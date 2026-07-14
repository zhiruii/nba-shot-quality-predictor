# NBA Shot Quality Predictor

A full-stack ML system that predicts the probability of any NBA shot going in, built on a growing PostgreSQL database that accumulates shots across seasons with automated refresh every 2 days via GitHub Actions.

Live site → https://nba-shot-quality-predictor1.streamlit.app/

> **Note:** The backend is hosted on Render's free tier, which spins down after ~15 minutes of inactivity. The first prediction after idle time can take up to a few minutes while the server cold-starts. Subsequent predictions are must faster.

The frontend is an interactive half-court: click anywhere on the court to place the shot, and shot distance, zone, and angle are derived from that click instead of typed in manually.

---

## What this project is actually about

The NBA MVP Predictor was my first real ML project. It taught me the basics such as feature engineering, model evaluation, avoiding data leakage, and serving predictions through an API. But the data layer was static: a manually maintained CSV file, updated by hand, with no database and no automation.

This project is what I built next, with those gaps specifically in mind.

The four things this project demonstrates that the MVP Predictor doesn't:

**1. A real database.** Shot data lives in PostgreSQL (Supabase). The application reads from and writes to a live database instead of a CSV bundled in the repo.

**2. Stateful, incremental data fetching.** `data.py` doesn't blindly re-pull everything on each run. It queries `SELECT MAX(game_date) FROM shots`, then calls the NBA API with `date_from_nullable` set to that date to fetch only shots newer than what's already stored. Re-running the script is safe by design, as `INSERT ... ON CONFLICT (game_id, game_event_id) DO NOTHING` means duplicate fetches produce no duplicate rows.

**3. A scheduled pipeline that runs without me.** A GitHub Actions workflow triggers every 2 days at 06:00 UTC on a self-hosted runner. It checks out the repo and runs `data.py`. The database stays current without any manual intervention.

**4. A schema designed to support a model that improves over time.** Two tables with deliberately different retention behaviour — shots are historical and self-contained, player stats are always current. See the Schema Design section below.

---

## Schema Design

The schema has two tables with deliberately different retention behaviour, designed to support a model that improves as seasons accumulate.

**`shots`** is an append-only historical table. Every shot row permanently carries `fg_pct` and `fg3_pct` baked in at ingest time, reflecting the shooter's stats as of that week's pipeline run. This means a November shot is paired with November running stats, not end-of-season stats. That's a feature that reflects what the shooter's performance actually looked like at the time of the shot, which is what the model should be learning from.

**`player_stats`** is non-historical, it always reflects the latest stats after each pipeline run, overwritten via upsert on every `data.py` execution. Its only role is to power the `/players` API endpoint, which is not currently called by the frontend (FG%/3PT% are entered manually instead). It has no role in training or inference.

The reason for baking stats into each shot row rather than joining at training time is that `player_stats` is mutable. If the join were deferred to training, every historical shot would be paired with whatever stats happened to be in `player_stats` at that moment — correct this season, wrong next season when `player_stats` gets overwritten. By embedding stats at ingest, each shot is self-contained and the training data stays temporally correct regardless of when the model is retrained.

During a current season or when a new season starts: `data.py` fetches new shots, merges in that season's player stats, and inserts them alongside all prior seasons. The model retrains on the full growing dataset, a system that is designed to get better as more seasons accumulate, with the 2025-26 season as the starting point.

---

## Dataset

`nba_api` `shotchartdetail` endpoint. All players, accumulating across seasons starting from 2025-26.

- ~219,160 shot attempts in the initial season, growing with each refresh
- ~115k misses, ~104k makes — nearly balanced classes
- Player shooting tendencies (season FG% and 3PT%) merged into each shot row at ingest time

---

## Feature Engineering

| Feature | Source | Notes |
|---|---|---|
| `SHOT_DISTANCE` | Raw | Direct from API |
| `SHOT_ANGLE` | `LOC_X`, `LOC_Y` | `atan2(LOC_Y, LOC_X)` — encodes shot direction |
| `TIME_LEFT_IN_Q` | `MINUTES_REMAINING`, `SECONDS_REMAINING` | Combined into total seconds |
| `PERIOD` | Raw | Overtime periods included |
| `SHOT_TYPE` | Categorical | One-hot encoded (2PT / 3PT) |
| `SHOT_ZONE_BASIC` | Categorical | One-hot encoded (7 zones) |
| `ACTION_TYPE` | Categorical | 60+ raw action types grouped into 13 categories, then one-hot encoded |
| `PLAYER_FG_PCT` | Baked into shot row at ingest | Shooter's season FG% as of ingest date |
| `PLAYER_3PT_PCT` | Baked into shot row at ingest | Shooter's season 3PT% as of ingest date |

The `ACTION_TYPE` grouping deserves a note. The raw API returns 60+ distinct action types such as "Driving Floating Jump Shot", "Turnaround Fadeaway Bank Jump Shot", and so on. Feeding these directly into the encoder would produce a sparse, noisy categorical with no generalisation across similar shot types. I grouped them by first-word pattern into 13 categories (Jump Shot, Layup, Dunk, Pullup, Driving, Fadeaway, Step Back, Turnaround, Running, Cutting, Floating, Hook, Putback) based on the mechanical similarity of the shot attempt.

Player FG% and 3PT% are included as numeric features. Fallback for missing stats is zero, not league average. A center with zero three-point attempts is not an average three-point shooter.

---

## Model

**Algorithm:** Logistic Regression (`max_iter=1000`)

**Preprocessing:**
- `OneHotEncoder(sparse_output=False, handle_unknown='error')` on categorical columns
- `StandardScaler()` on the full 28-column feature matrix after hstack

**Evaluation:** 80/20 stratified train/test split. Train AUC: 0.654, Test AUC: 0.655 — near-identical scores confirm no overfitting.

The dominant missing signal is defender proximity, representing how contested the shot is. This information is not available from `nba_api`.

---

## Database Design

Two tables in PostgreSQL (Supabase):

**`shots`** — one row per shot attempt. `fg_pct` and `fg3_pct` are baked in at ingest time. `UNIQUE (game_id, game_event_id)` constraint makes the incremental upsert safe: re-running `data.py` after a boundary overlap produces zero duplicates.

**`player_stats`** — one row per player, overwritten on each run via `ON CONFLICT (player_id) DO UPDATE SET fg_pct = EXCLUDED.fg_pct, ...`. Used only by the `/players` API endpoint, not used in training or inference.

---

## Automated Pipeline

```
Every 2 days, 06:00 UTC
        ↓
GitHub Actions (self-hosted runner): checkout → python data.py
        ↓
data.py: SELECT MAX(game_date) FROM shots
        ↓
nba_api shotchartdetail (date_from_nullable = last stored date)
        ↓
Merge current season player stats onto shot rows
        ↓
INSERT ... ON CONFLICT (game_id, game_event_id) DO NOTHING
        ↓
LeagueDashPlayerStats → upsert player_stats
        ↓
Database is current. No manual step required.
```

Retraining is kept manual, run `python train.py` when you want the model to reflect new data, then commit the artifacts. Separating "data freshness" from "retrain cadence".

Note: `stats.nba.com` blocks requests from GitHub-hosted runner IP ranges (Azure datacenters). The pipeline runs on a self-hosted runner to avoid this.

---

## Architecture

Data flows in one direction: ingest → features → train → serve → API. Each layer is one file with one responsibility.

```
nba_api
    ↓
data.py  ←→  db.py  ←→  PostgreSQL (Supabase)
                ↑
            train.py → feature.py → artifacts/
                                        ↓
             main.py  ←  serve.py  ← model.pkl
             main.py  ←  db.py       encoder.pkl
                ↑                     scaler.pkl
            frontend/                 feature_names.json
              ui_new.py
           (Streamlit)
```

Critical constraints enforced by design:
- `feature.py` has zero project imports. It contains pure transformation logic, callable from both training and serving without circular dependencies
- `encoder.fit_transform()` and `scaler.fit_transform()` only in `train.py`. `serve.py` calls `.transform()` only

---

## Tech Stack

- **ML:** scikit-learn, pandas, numpy
- **Data:** nba_api, PostgreSQL via Supabase, psycopg2
- **API:** FastAPI
- **Frontend:** Streamlit
- **Automation:** GitHub Actions
- **Deployment:** Render (backend), Streamlit Cloud (frontend)
