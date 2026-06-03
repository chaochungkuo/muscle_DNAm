#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

quarto render 01_Preprocessing.ipynb --output-dir=reports --to html --execute --no-clean
quarto render 02_Model_Selection_Leakage_Safe.ipynb --output-dir=reports --to html --execute --no-clean
quarto render 03-01_Logistic_Regression.ipynb --output-dir=reports --to html --execute --no-clean
quarto render 03-02_Decision_Trees.ipynb --output-dir=reports --to html --execute --no-clean
quarto render 03-03_Random_Forest.ipynb --output-dir=reports --to html --execute --no-clean
quarto render 03-04_SVM.ipynb --output-dir=reports --to html --execute --no-clean
quarto render 04_Model_Evaluation.ipynb --output-dir=reports --to html --execute --no-clean
quarto render 05_Applying_Unknown.ipynb --output-dir=reports --to html --execute --no-clean
quarto render 03_Exploratory_Feature_Selection.ipynb --output-dir=reports --to html --execute --no-clean
