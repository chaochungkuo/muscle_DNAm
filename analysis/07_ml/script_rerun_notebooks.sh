#!/usr/bin/env bash
set -euo pipefail

export QUARTO_PYTHON="${QUARTO_PYTHON:-$(which python)}"
export CA_KERNEL_NAME="muscle-dnam-ml"
echo "Using python=$(which python)"
python -m ipykernel install --prefix "$(python -c 'import sys; print(sys.prefix)')" --name "${CA_KERNEL_NAME}" --display-name "muscle_DNAm ML" >/dev/null
echo "Registered kernel ${CA_KERNEL_NAME} for $(python -c 'import sys; print(sys.prefix)')"

jupyter nbconvert --to notebook --execute 01_Preprocessing.ipynb
jupyter nbconvert --to notebook --execute 02_Model_Selection_Leakage_Safe.ipynb
jupyter nbconvert --to notebook --execute 03-01_Logistic_Regression.ipynb
jupyter nbconvert --to notebook --execute 03-02_Decision_Trees.ipynb
jupyter nbconvert --to notebook --execute 03-03_Random_Forest.ipynb
jupyter nbconvert --to notebook --execute 03-04_SVM.ipynb
jupyter nbconvert --to notebook --execute 04_Model_Evaluation.ipynb
jupyter nbconvert --to notebook --execute 05_Applying_Unknown.ipynb
jupyter nbconvert --to notebook --execute 03_Exploratory_Feature_Selection.ipynb
