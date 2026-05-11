import pandas as pd
from feature import featurize
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score

df = pd.read_csv("202526_shots.csv")

rows = df.to_dict(orient = 'records')
features_df = pd.DataFrame([featurize(row) for row in rows])

cat_df = features_df[["SHOT_TYPE", "SHOT_ZONE_BASIC", "ACTION_TYPE"]]
num_df = features_df[["SHOT_DISTANCE", "SHOT_ANGLE", "TIME_LEFT_IN_Q", "PERIOD"]]

encoder = OneHotEncoder(sparse_output=False, handle_unknown="error")
encoded = encoder.fit_transform(cat_df)

# Convert num_df into numpy and stack horizontally to fit into model.
X = np.hstack([num_df.to_numpy(), encoded])
X = StandardScaler().fit_transform(X)

y = df["SHOT_MADE_FLAG"]

model = LogisticRegression(max_iter = 1000)
model.fit(X, y)

cross_validation = StratifiedKFold(n_splits=5, shuffle=True, random_state=123)
scores = cross_val_score(model, X, y, cv=cross_validation, scoring= "roc_auc")
print(scores.round(3))
print(scores.mean().round(3))
print(scores.std().round(3))