#!/bin/bash
# This script is used to export the environment.
conda env export --no-builds | grep -v "prefix" > conda_environment.yml
conda list --explicit > conda-spec-file.txt
pip freeze > requirements.txt

# You can delete your current muscle-dnam-ml environment and create a new one by:
# conda deactivate
# conda env remove --name muscle-dnam-ml
# conda env create -f conda_environment.yml
