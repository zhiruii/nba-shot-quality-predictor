from nba_api.stats.endpoints import shotchartdetail, leaguedashplayerstats

shots = shotchartdetail.ShotChartDetail(
    team_id=0,
    player_id=0,
    season_type_all_star="Regular Season",
    season_nullable="2025-26",
    context_measure_simple="FGA",
    timeout= 60
)

df = shots.get_data_frames()[0]

#print("Shape:", df.shape)
#print("\nColumns:\n", df.columns.tolist())

df.to_csv('202526_shots.csv', index=False)

player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season="2025-26",
    season_type_all_star="Regular Season",
    timeout=60
)

player_df = player_stats.get_data_frames()[0]
player_df = player_df[["PLAYER_ID", "FG_PCT", "FG3_PCT"]]

player_df.to_csv('player_stats.csv', index=False)