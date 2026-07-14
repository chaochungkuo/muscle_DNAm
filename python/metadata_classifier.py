from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
data = pd.read_csv(ROOT / "results/tables/analysis_metadata.tsv", sep="\t", dtype=str)
y = data["display_group"]
sets = {
    "all_available_metadata": ["dataset_source","city_of_origin","sentrix_id","age_group","gender","muscle_location_group"],
    "sentrix_only": ["sentrix_id"], "source_only": ["dataset_source"],
    "age_sex": ["age_group","gender"], "biopsy_site_only": ["muscle_location_group"],
}
cv = RepeatedStratifiedKFold(n_splits=3, n_repeats=30, random_state=42)
rows=[]
for name, cols in sets.items():
    model=Pipeline([
        ("prep",ColumnTransformer([("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),
            ("onehot",OneHotEncoder(handle_unknown="ignore"))]),cols)])),
        ("model",LogisticRegression(max_iter=5000,class_weight="balanced")),
    ])
    for fold,(tr,te) in enumerate(cv.split(data,y),1):
        model.fit(data.iloc[tr],y.iloc[tr]); pred=model.predict(data.iloc[te])
        rows.append({"feature_set":name,"fold":fold,"accuracy":accuracy_score(y.iloc[te],pred),
            "balanced_accuracy":balanced_accuracy_score(y.iloc[te],pred)})
out=pd.DataFrame(rows)
out.to_csv(ROOT/"results/tables/metadata_only_classifier.tsv",sep="\t",index=False)
summary=out.groupby("feature_set")[["accuracy","balanced_accuracy"]].agg(["mean","std","min","max"])
summary.to_csv(ROOT/"results/tables/metadata_only_classifier_summary.tsv",sep="\t")
print(summary)
