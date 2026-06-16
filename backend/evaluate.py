import numpy as np
import pandas as pd
import db
from feature import featurize
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

rows = db.fetch_all_shots()
df = pd.DataFrame(rows)

player_stats = db.fetch_all_player_stats()

features_df = pd.DataFrame([featurize(row, player_stats=player_stats) for row in rows])

cat_df = features_df[["SHOT_TYPE", "SHOT_ZONE_BASIC", "ACTION_TYPE"]]
num_df = features_df[["SHOT_DISTANCE", "SHOT_ANGLE", "TIME_LEFT_IN_Q", "PERIOD", "PLAYER_FG_PCT", "PLAYER_3PT_PCT"]]
y = df["SHOT_MADE_FLAG"]

cat_train, cat_test, num_train, num_test, y_train, y_test = train_test_split(
    cat_df, num_df, y, test_size=0.2, stratify=y, random_state=123
)

encoder = OneHotEncoder(sparse_output=False, handle_unknown="error")
encoded_train = encoder.fit_transform(cat_train)
encoded_test = encoder.transform(cat_test)

X_train = np.hstack([num_train.to_numpy(), encoded_train])
X_test = np.hstack([num_test.to_numpy(), encoded_test])

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

train_auc = roc_auc_score(y_train, model.predict_proba(X_train)[:, 1])
test_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

print(f"Train ROC-AUC: {train_auc:.3f}")
print(f"Test ROC-AUC:  {test_auc:.3f}")
