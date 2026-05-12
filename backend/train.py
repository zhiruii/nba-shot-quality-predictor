import pandas as pd
from feature import featurize
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
import pickle
import json

df = pd.read_csv("202526_shots.csv")

rows = df.to_dict(orient = 'records')
features_df = pd.DataFrame([featurize(row) for row in rows])

cat_df = features_df[["SHOT_TYPE", "SHOT_ZONE_BASIC", "ACTION_TYPE"]]
num_df = features_df[["SHOT_DISTANCE", "SHOT_ANGLE", "TIME_LEFT_IN_Q", "PERIOD"]]

encoder = OneHotEncoder(sparse_output=False, handle_unknown="error")
encoded = encoder.fit_transform(cat_df)

# Convert num_df into numpy and stack horizontally to fit into model.
X_unscaled = np.hstack([num_df.to_numpy(), encoded])

y = df["SHOT_MADE_FLAG"]

#pipeline made to prevent contamination of data during cross validation. not used in the final model training.
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=1000))
])

#cross_validation = StratifiedKFold(n_splits=5, shuffle=True, random_state=123)
#scores = cross_val_score(pipeline, X_unscaled, y, cv=cross_validation, scoring= "roc_auc")
#print(scores.round(3))
#print(scores.mean().round(3))
#print(scores.std().round(3))

scaler = StandardScaler()
X = scaler.fit_transform(X_unscaled)
model = LogisticRegression(max_iter=1000)
model.fit(X, y)

#print(encoder.get_feature_names_out())
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("encoder.pkl", "wb") as f1:
    pickle.dump(encoder, f1)

with open("scaler.pkl", "wb") as f2:
    pickle.dump(scaler, f2)

num_cols = ["SHOT_DISTANCE", "SHOT_ANGLE", "TIME_LEFT_IN_Q", "PERIOD"]
feature_names = num_cols + encoder.get_feature_names_out().tolist()
json.dump(feature_names, open("feature_names.json", "w"))
