import pandas as pd
from feature import featurize
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

df = pd.read_csv("202526_shots.csv")

rows = df.to_dict(orient = 'records')
features = [featurize(row) for row in rows]