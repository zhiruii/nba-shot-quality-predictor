from feature import featurize
import numpy as np

def predict(model, encoder, scaler, raw_input):
    f_dict = featurize(raw_input)
    cat_vals = [f_dict["SHOT_TYPE"], f_dict["SHOT_ZONE_BASIC"], f_dict["ACTION_TYPE"]]
    num_vals = [f_dict["SHOT_DISTANCE"], f_dict["SHOT_ANGLE"], f_dict["TIME_LEFT_IN_Q"], f_dict["PERIOD"], f_dict["PLAYER_FG_PCT"], f_dict["PLAYER_3PT_PCT"]]
    encoded = encoder.transform([cat_vals])

    X = np.hstack([num_vals, encoded[0]])
    X = scaler.transform([X])

    return model.predict_proba(X)[0][1]