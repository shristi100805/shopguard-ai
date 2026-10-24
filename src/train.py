import json
import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import classification_report
from src.preprocess import clean_text

# 1. Load. keep_default_na=False keeps the word "None" as a label
d = pd.read_csv("data/processed/shopguard_combined_model.csv",
                encoding="utf-8", keep_default_na=False)
d = d[(d["Text Snippet"].str.strip() != "") & (d["CCPA Category"].str.strip() != "")]
d["CCPA Category"] = d["CCPA Category"].replace({"None": "No Dark Pattern"})

# 2. Add-on / insurance rows belong to the Basket Sneaking rules, not the ML model
addon = d["Text Snippet"].str.contains(
    r"insurance|trip protect|secure my trip|trip secure|freebies|add services|add only|\btip\b",
    case=False, regex=True)
d = d[~((d["CCPA Category"] == "No Dark Pattern") & addon)]

# 3. Clean text the same way the app will clean it later
d["clean"] = d["Text Snippet"].apply(clean_text)

# 4. Same text with two different labels cannot be learned: show and drop
n_labels = d.groupby("clean")["CCPA Category"].transform("nunique")
conf = d[n_labels > 1]
print("Conflicting rows removed:", len(conf))
print(conf[["Text Snippet", "CCPA Category", "dataset_origin"]].to_string(max_colwidth=60))
d = d[n_labels == 1]

# 5. Remove repeated texts
before = len(d)
d = d.drop_duplicates(subset="clean")
print("\nDuplicate texts removed:", before - len(d))
print("\nFinal training data:")
print(d["CCPA Category"].value_counts())
print(d["dataset_origin"].value_counts())

# 6. Embed, cross-validate, train
embedder = SentenceTransformer("all-MiniLM-L6-v2")
X = embedder.encode(d["clean"].tolist(), show_progress_bar=False)
y = np.array(d["CCPA Category"].tolist())

clf = LogisticRegression(max_iter=2000, class_weight="balanced")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
pred = cross_val_predict(clf, X, y, cv=cv)

print("\nALL DATA")
print(classification_report(y, pred, zero_division=0))
mask = np.array((d["dataset_origin"] == "Indian").tolist())
print("INDIAN ROWS ONLY")
print(classification_report(y[mask], pred[mask], zero_division=0))

clf.fit(X, y)
joblib.dump(clf, "models/best_model.joblib")
json.dump([str(c) for c in clf.classes_], open("models/labels.json", "w"))
print("Saved model.")