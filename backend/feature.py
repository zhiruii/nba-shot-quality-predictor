import math

def cal_seconds(minute, sec):
    return minute * 60 + sec

def cal_angle(x, y):
    return math.atan2(y, x)

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

    result = mapping.get(first)
    if result is None:
        raise ValueError(f"Unmapped action {action_type}")
    return result

def featurize(row, player_stats=None):
    output = {"SHOT_DISTANCE": row["SHOT_DISTANCE"],
              "SHOT_ANGLE": cal_angle(row["LOC_X"], row["LOC_Y"]),
              "TIME_LEFT_IN_Q": cal_seconds(row["MINUTES_REMAINING"], row["SECONDS_REMAINING"]),
              "PERIOD": row["PERIOD"], "SHOT_TYPE": row["SHOT_TYPE"],
              "SHOT_ZONE_BASIC": row["SHOT_ZONE_BASIC"], "ACTION_TYPE": get_action_group(row["ACTION_TYPE"])}

    player = (player_stats or {}).get(row["PLAYER_ID"], {})
    fg_pct = player.get("FG_PCT", 0)
    fg3_pct = player.get("FG3_PCT", 0)

    output["PLAYER_FG_PCT"] = 0 if fg_pct is None or math.isnan(fg_pct) else fg_pct
    output["PLAYER_3PT_PCT"] = 0 if fg3_pct is None or math.isnan(fg3_pct) else fg3_pct

    return output

