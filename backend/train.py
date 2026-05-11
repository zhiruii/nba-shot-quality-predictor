from nba_api.stats.endpoints import shotchartdetail
import pandas as pd
shots = shotchartdetail.ShotChartDetail(
    team_id=0,
    player_id=0,        # 0 = all players
    season_type_all_star="Regular Season",
    season_nullable="2023-24",
    context_measure_simple="FGA"
)

df = shots.get_data_frames()[0]

print("Shape:", df.shape)
print("\nColumns:\n", df.columns.tolist())
print("\nDtypes:\n", df.dtypes)
print("\nFirst 3 rows:\n", df.head(3).to_string())
print("\nNulls per column:\n", df.isnull().sum())
print("\nSHOT_MADE_FLAG distribution:\n", df['SHOT_MADE_FLAG'].value_counts())
print("\nACTION_TYPE value counts:\n", df['ACTION_TYPE'].value_counts())
print("\nSHOT_ZONE_BASIC value counts:\n", df['SHOT_ZONE_BASIC'].value_counts())
print("\nSHOT_TYPE value counts:\n", df['SHOT_TYPE'].value_counts())
print("\nPERIOD value counts:\n", df['PERIOD'].value_counts().sort_index())
print("\nSHOT_DISTANCE describe:\n", df['SHOT_DISTANCE'].describe())
print("\nLOC_X describe:\n", df['LOC_X'].describe())
print("\nLOC_Y describe:\n", df['LOC_Y'].describe())
# See all unique first words in ACTION_TYPE
first_words = df['ACTION_TYPE'].str.split().str[0]
#print(first_words.value_counts())


def get_action_group(action_type):
    words = action_type.split()
    first = words[0]

    if first == "Alley":
        return "Dunk" if "Dunk" in words else "Layup"
    if first == "Reverse":
        return "Dunk" if "Dunk" in words else "Layup"
    if first == "Tip":
        return "Putback"
    if first == "Finger":
        return "Layup"

    mapping = {
        "Jump": "Jump Shot",
        "Pullup": "Pullup",
        "Driving": "Driving",
        "Running": "Running",
        "Step": "Step Back",
        "Turnaround": "Turnaround",
        "Cutting": "Cutting",
        "Fadeaway": "Fadeaway",
        "Floating": "Floating",
        "Layup": "Layup",
        "Dunk": "Dunk",
        "Hook": "Hook",
        "Putback": "Putback",
    }

    return mapping.get(first, f"UNMAPPED: {action_type}")


# Check every unique action type
for action in sorted(df['ACTION_TYPE'].unique()):
    group = get_action_group(action)
    if "UNMAPPED" in group:
        print(group)

print("Done — any lines above are unhandled cases")

made_by_zone = df.groupby('SHOT_ZONE_BASIC')['SHOT_MADE_FLAG'].mean()
print(made_by_zone.sort_values(ascending=False))

made_by_action = df.groupby('ACTION_TYPE').apply(
    lambda x: pd.Series({
        'make_rate': x['SHOT_MADE_FLAG'].mean(),
        'count': len(x)
    })
).sort_values('make_rate', ascending=False)

print(made_by_action.to_string())