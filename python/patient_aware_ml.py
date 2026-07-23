from pathlib import Path
import json, time
from functools import partial
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif, mutual_info_classif, RFE
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import train_test_split, StratifiedGroupKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

ROOT=Path(__file__).resolve().parents[1]
paths=__import__('yaml').safe_load((ROOT/'config/paths.local.yml').read_text())
meta=pd.read_csv(ROOT/'results/tables/analysis_metadata.tsv',sep='\t',dtype=str)
patient=meta[['patient_id','display_group']].drop_duplicates()
assert len(patient)==72
train_pat,test_pat=train_test_split(patient,test_size=.4,random_state=41,stratify=patient.display_group)
train_ids=set(train_pat.patient_id); test_ids=set(test_pat.patient_id)
assert train_ids.isdisjoint(test_ids)

start=time.time()
raw=pd.read_csv(paths['processed_m_values'],index_col=0).T
raw=raw.loc[meta.matrix_sample]
y=meta.set_index('matrix_sample').loc[raw.index,'display_group']
groups=meta.set_index('matrix_sample').loc[raw.index,'patient_id']
tr=groups.isin(train_ids); te=groups.isin(test_ids)
Xtr,Xte=raw.loc[tr],raw.loc[te]; ytr,yte=y.loc[tr],y.loc[te]; gtr=groups.loc[tr]
assert set(groups[tr]).isdisjoint(set(groups[te]))

vt=VarianceThreshold(.8*(1-.8)); a=vt.fit_transform(Xtr); b=vt.transform(Xte)
names=np.asarray(raw.columns)[vt.get_support()]
uni=SelectKBest(f_classif,k=max(1,int(a.shape[1]*.1))); a=uni.fit_transform(a,ytr); b=uni.transform(b); names=names[uni.get_support()]
mi=SelectKBest(partial(mutual_info_classif,random_state=42),k=max(1,int(a.shape[1]*.5)))
a=mi.fit_transform(a,ytr); b=mi.transform(b); names=names[mi.get_support()]
sc=StandardScaler(); a=sc.fit_transform(a); b=sc.transform(b)
rfe=RFE(RandomForestClassifier(n_estimators=100,random_state=42,n_jobs=-1),n_features_to_select=50,step=.1)
a=rfe.fit_transform(a,ytr); b=rfe.transform(b); names=names[rfe.get_support()]

cv=StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=42)
models={
 'Logistic regression':(LogisticRegression(max_iter=5000),{'C':[.01,.1,1,10,100]}),
 'Decision tree':(DecisionTreeClassifier(random_state=42),{'max_depth':[3,5,10,None],'min_samples_leaf':[1,2,4]}),
 'Random forest':(RandomForestClassifier(random_state=42,n_jobs=-1),{'n_estimators':[100,300],'max_depth':[5,10,None]}),
 'SVM':(SVC(random_state=42),{'C':[.1,1,10,100],'kernel':['linear','rbf']})}
rows=[]
outdir=ROOT/'results/models/patient_aware'; outdir.mkdir(parents=True,exist_ok=True)
for name,(est,grid) in models.items():
    gs=GridSearchCV(est,grid,cv=cv,scoring='balanced_accuracy',n_jobs=-1)
    gs.fit(a,ytr,groups=gtr); pred=gs.best_estimator_.predict(b)
    rows.append({'model':name,'train_samples':len(ytr),'test_samples':len(yte),
      'train_patients':len(set(gtr)),'test_patients':len(set(groups[te])),
      'accuracy':accuracy_score(yte,pred),'balanced_accuracy':balanced_accuracy_score(yte,pred),
      'weighted_f1':f1_score(yte,pred,average='weighted'),'best_params':json.dumps(gs.best_params_)})
    joblib.dump(gs.best_estimator_,outdir/(name.lower().replace(' ','_')+'.joblib'))
pd.DataFrame(rows).to_csv(ROOT/'results/tables/patient_aware_ml_metrics.tsv',sep='\t',index=False)
pd.DataFrame({'CpG':names}).to_csv(ROOT/'results/tables/patient_aware_selected_cpgs.tsv',sep='\t',index=False)
pd.DataFrame({'sample_id':raw.index,'patient_id':groups,'disease_group':y,
 'partition':np.where(tr,'train','test')}).to_csv(ROOT/'results/tables/patient_aware_ml_partition.tsv',sep='\t',index=False)
joblib.dump({'variance':vt,'univariate':uni,'mutual_information':mi,'scaler':sc,'rfe':rfe,'features':names},outdir/'feature_pipeline.joblib')
(ROOT/'logs/patient_aware_ml_runtime.txt').write_text(f"elapsed_minutes={(time.time()-start)/60:.3f}\n")
print(pd.DataFrame(rows))
