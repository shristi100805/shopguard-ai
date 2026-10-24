import pandas as pd

d = pd.read_csv("data/processed/shopguard_combined_model.csv")
print("Shape:", d.shape)
print("Columns:", d.columns.tolist())
print()

for c in d.columns:
    n = d[c].nunique()
    print(f"{c}: {n} unique values")

print()
for c in d.columns:
    if c != "text" and d[c].nunique() <= 40:
        print(d[c].value_counts(), "\n")

print(d.head(3).to_string(max_colwidth=60))