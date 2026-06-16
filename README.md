# NBA Shot Quality Predictor

A backend ML system that predicts the probability of any 2025-26 NBA shot going in, built on a live PostgreSQL database with automated weekly data refresh via GitHub Actions.

---

## What this project is actually about

The NBA MVP Predictor was my first real ML project. It taught me the basics such as feature engineering, model evaluation, avoiding label leakage, and serving predictions through an API. But the data layer was static: a manually maintained CSV file, updated by hand, with no database and no automation.

This project is what I built next, with those gaps specifically in mind.

The three things this project demonstrates that the MVP Predictor doesn't:

**1. A real database.** Shot data lives in PostgreSQL (Supabase). The application reads from and writes to a live database instead of a CSV bundled in the repo.

**2. Stateful, incremental data fetching.** `data.py` doesn't blindly re-pull everything on each run. It queries `SELECT MAX(game_date) FROM shots`, then calls the NBA API with `date_from_nullable` set to that date to fetch only shots newer than what's already stored. Re-running the script is idempotent by design: `INSERT ... ON CONFLICT (game_id, game_event_id) DO NOTHING` means duplicate fetches produce zero duplicate rows.

**3. A scheduled pipeline that runs without me.** A GitHub Actions workflow triggers every Monday at 06:00 UTC. It checks out the repo, installs dependencies, and runs `data.py` with `DATABASE_URL` injected from a GitHub secret. The database stays current without any manual intervention.

---

## Running it locally

**1. Clone the repo and install dependencies:**
```bash
git clone https://github.com/zhirui/nba-shot-quality-predictor.git
cd nba-shot-quality-predictor/backend
pip install -r requirements.txt
```

**2. Set up the environment variable:**

Create a `.env` file inside `backend/` with your Supabase connection string:
```
DATABASE_URL=your_supabase_connection_string
```

**3. Start the server:**
```bash
python -m uvicorn main:app --reload
```

The API is now running at `http://localhost:8000`. Open `http://localhost:8000/docs` in your browser for an interactive UI where you can call the `/predict` endpoint directly.

---

## Try it yourself

The main feature is `/predict` — given a description of a shot, it returns the probability that it goes in.

### What the input fields mean

| Field | What it is | Example |
|---|---|---|
| `SHOT_DISTANCE` | How far from the basket the shot was taken, in feet | `22` for a three-pointer, `0` for a dunk |
| `LOC_X` | Horizontal position on the court in tenths of a foot. `0` is directly in front of the basket, negative is left wing, positive is right wing | `-220` for left corner three |
| `LOC_Y` | Vertical position from the basket toward half court, in tenths of a foot | `0` is directly under the basket |
| `MINUTES_REMAINING` | Minutes left in the quarter | `2` |
| `SECONDS_REMAINING` | Seconds left on top of the minutes | `30` |
| `PERIOD` | Quarter number. 1–4 for regulation, 5+ for overtime | `4` |
| `SHOT_TYPE` | Whether it's a two or three point attempt | `"2PT Field Goal"` or `"3PT Field Goal"` |
| `SHOT_ZONE_BASIC` | Named zone on the court | `"Restricted Area"`, `"Mid-Range"`, `"Above the Break 3"`, `"Left Corner 3"`, `"Right Corner 3"`, `"In The Paint (Non-RA)"`, `"Backcourt"` |
| `ACTION_TYPE` | How the shot was taken | `"Dunk"`, `"Driving Layup"`, `"Jump Shot"`, `"Pullup Jump Shot"`, `"Step Back Jump Shot"`, `"Fadeaway Jump Shot"` |
| `PLAYER_ID` | The NBA's internal ID for the shooter — used under the hood to look up their season FG% and 3PT% | `2544` for LeBron James, `201939` for Steph Curry |

### Example 1 — Dunk at the rim (LeBron James)

```json
{
  "SHOT_DISTANCE": 0,
  "LOC_X": 0,
  "LOC_Y": 0,
  "MINUTES_REMAINING": 5,
  "SECONDS_REMAINING": 0,
  "PERIOD": 2,
  "SHOT_TYPE": "2PT Field Goal",
  "SHOT_ZONE_BASIC": "Restricted Area",
  "ACTION_TYPE": "Dunk",
  "PLAYER_ID": 2544
}
```
**Result: ~90%** — dunks are nearly automatic, and the model reflects that.

### Example 2 — Mid-range jumper from the elbow (Steph Curry)

```json
{
  "SHOT_DISTANCE": 15,
  "LOC_X": 150,
  "LOC_Y": 100,
  "MINUTES_REMAINING": 3,
  "SECONDS_REMAINING": 20,
  "PERIOD": 3,
  "SHOT_TYPE": "2PT Field Goal",
  "SHOT_ZONE_BASIC": "Mid-Range",
  "ACTION_TYPE": "Jump Shot",
  "PLAYER_ID": 201939
}
```
**Result: ~46%** — mid-range jumpers are contested and lower probability than shots near the rim.

### Example 3 — Three-pointer (Steph Curry)

```json
{
  "SHOT_DISTANCE": 22,
  "LOC_X": -220,
  "LOC_Y": 10,
  "MINUTES_REMAINING": 2,
  "SECONDS_REMAINING": 30,
  "PERIOD": 4,
  "SHOT_TYPE": "3PT Field Goal",
  "SHOT_ZONE_BASIC": "Above the Break 3",
  "ACTION_TYPE": "Jump Shot",
  "PLAYER_ID": 201939
}
```
**Result: ~39%** — even elite shooters make fewer than half their threes. Probability drops further with distance.

The pattern holds intuitively: **dunk (90%) → mid-range (46%) → three-pointer (39%)**. Probability falls as distance and shot difficulty increase.

---

## Dataset

`nba_api` `shotchartdetail` endpoint — 2025-26 NBA regular season, all players.

- ~219,160 shot attempts, 24 columns
- ~115k misses, ~104k makes — nearly balanced classes
- Player shooting tendencies (season FG% and 3PT%) fetched separately from `LeagueDashPlayerStats` and stored in a `player_stats` table (~582 players)

---

## Feature Engineering

| Feature | Source | Notes |
|---|---|---|
| `SHOT_DISTANCE` | Raw | Direct from API |
| `SHOT_ANGLE` | `LOC_X`, `LOC_Y` | `atan2(LOC_Y, LOC_X)` — encodes shot direction, not just distance |
| `TIME_LEFT_IN_Q` | `MINUTES_REMAINING`, `SECONDS_REMAINING` | Combined into total seconds |
| `PERIOD` | Raw | Overtime periods included |
| `SHOT_TYPE` | Categorical | One-hot encoded (2PT / 3PT) |
| `SHOT_ZONE_BASIC` | Categorical | One-hot encoded (7 zones) |
| `ACTION_TYPE` | Categorical | 60+ raw action types grouped into 13 categories, then one-hot encoded |
| `PLAYER_FG_PCT` | Player stats lookup | Shooter's season FG% |
| `PLAYER_3PT_PCT` | Player stats lookup | Shooter's season 3PT% |

The `ACTION_TYPE` grouping deserves a note. The raw API returns 60+ distinct action types such as "Driving Floating Jump Shot", "Turnaround Fadeaway Bank Jump Shot", and so on. Feeding these directly into the encoder would produce a sparse, noisy categorical with no generalisation across similar shot types. I grouped them by first-word pattern into 13 categories (Jump Shot, Layup, Dunk, Pullup, Driving, Fadeaway, Step Back, Turnaround, Running, Cutting, Floating, Hook, Putback) based on the mechanical similarity of the shot attempt.

Player FG% and 3PT% are included as numeric features. Fallback for missing players is zero, not league average, as a center with zero three-point attempts is not an average three-point shooter.

---

## Model

**Algorithm:** Logistic Regression (`max_iter=1000`)

**Preprocessing:**
- `OneHotEncoder(sparse_output=False, handle_unknown='error')` on categorical columns
- `StandardScaler()` on the full 28-column feature matrix after hstack

**Evaluation:** 80/20 stratified train/test split. Train AUC: 0.654, Test AUC: 0.654 — scores match exactly, confirming no overfitting.

The dominant missing signal is defender proximity, indicating how contested the shot is.

---

## Database Design

Two tables in PostgreSQL (Supabase):

**`shots`** — one row per shot attempt. `UNIQUE (game_id, game_event_id)` constraint makes the incremental upsert safe: re-running `data.py` after a boundary overlap produces zero duplicates.

**`player_stats`** — one row per player per season. Upserted on each run via `ON CONFLICT (player_id) DO UPDATE SET fg_pct = EXCLUDED.fg_pct, ...` — stats always reflect the latest available stats.

---

## Automated Pipeline

```
Every Monday, 06:00 UTC
        ↓
GitHub Actions: checkout → pip install → python data.py
        ↓
data.py: SELECT MAX(game_date) FROM shots
        ↓
nba_api shotchartdetail (date_from_nullable = last stored date)
        ↓
INSERT ... ON CONFLICT (game_id, game_event_id) DO NOTHING
        ↓
LeagueDashPlayerStats → upsert player_stats
        ↓
Database is current. No manual step required.
```

Retraining is kept manual — run `python train.py` when you want the model to reflect new data, then commit the artifacts. Separating "data freshness" from "retrain cadence".

Known limitation: `stats.nba.com` occasionally times out from GitHub-hosted runner IPs. Manual re-run via `workflow_dispatch` is the fix.

---

## Architecture

Data flows in one direction: ingest → features → train → serve → API. Each layer is one file with one responsibility.

```
nba_api
    ↓
data.py  ←→  db.py  ←→  PostgreSQL (Supabase)
                              ↓
                          train.py → feature.py → artifacts/
                                                      ↓
                          main.py  ←  serve.py  ← model.pkl
                                                   encoder.pkl
                                                   scaler.pkl
                                                   feature_names.json
```

Critical constraints enforced by design:
- `feature.py` has zero project imports. It is pure transformation logic, callable from both training and serving without circular dependencies
- `encoder.fit_transform()` and `scaler.fit_transform()` only in `train.py`. `serve.py` calls `.transform()` only

---

## Tech Stack

- **ML:** scikit-learn, pandas, numpy
- **Data:** nba_api, PostgreSQL via Supabase, psycopg2
- **API:** FastAPI
- **Automation:** GitHub Actions
