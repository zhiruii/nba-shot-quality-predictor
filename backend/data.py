import db
from nba_api.stats.endpoints import shotchartdetail, leaguedashplayerstats

date_from = db.get_latest_shot_date()

shot_kwargs = dict(
    team_id=0,
    player_id=0,
    season_type_all_star="Regular Season",
    season_nullable="2025-26",
    context_measure_simple="FGA",
    timeout=60,
)
if date_from is not None:
    shot_kwargs["date_from_nullable"] = date_from.strftime("%m/%d/%Y")

player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season="2025-26",
    season_type_all_star="Regular Season",
    timeout=60
)
player_df = player_stats.get_data_frames()[0][["PLAYER_ID", "PLAYER_NAME", "FG_PCT", "FG3_PCT"]]
db.upsert_player_stats(player_df.to_dict(orient="records"))

shots = shotchartdetail.ShotChartDetail(**shot_kwargs)
df = shots.get_data_frames()[0]
df = df.merge(player_df[["PLAYER_ID", "FG_PCT", "FG3_PCT"]], on="PLAYER_ID", how="left")
db.insert_shots(df.to_dict(orient="records"))
