# muscle_DNAm

Analysis scripts for the manuscript:
> Entity-specific DNA methylation patterns in non-neoplastic skeletal muscle pathology

## Overview
This repository contains only analysis notebooks/scripts and reproducibility files. It excludes raw data and generated outputs (figures, tables, reports).

## Methods summary

### Data processing and statistics

Array data analysis was performed using R v.4.3.3, using a number of packages from Bioconductor and other repositories. Raw signal intensities were obtained from IDAT files using the minfi R package (Aryee et al 2014). Each sample was individually normalised by performing background correction for both colour channels. Subsequently, several filtering criteria were applied to the initial CpG sites (865859): removal of probes targeting X and Y chromosomes (18507), removal of probes containing single nucleotide polymorphism within five base pairs spanning and within the targeted CpG site (46224), and probes with bad quality (23956). Normalization was performed using the preprocessQuantile function in minfi (Touleimat & Tost 2012). The M values of the filtered probes were used for principal component analysis (PCA) and t-SNE clustering (Rtsne package v.0.17). Differential methylation analysis was conducted using the limma R package (Ritchie et al 2015) on the M values of all CpG sites with the annotation on human genome hg19. The adjusted p-values were corrected using the Benjamini-Hochberg procedure to calculate the False Discovery Rate (FDR). Gene Set Enrichment Analysis (GSEA) was performed using the clusterProfiler R package (Yu et al 2012). Customized heatmaps were generated using the pheatmap R package (Kolde 2018).

### Supervised Learning for Predicting Diagnosis

The normalized M values were loaded for supervised diagnosis prediction using a leakage-safe workflow. The dataset was first split into stratified training and held-out test sets. Low-variance filtering, univariate feature selection, mutual-information feature selection, scaling, and recursive feature elimination were then fitted on the training set only. The held-out test set and unknown application samples were transformed with the fitted feature-selection artifacts, without using their labels to select CpG sites. K-fold cross-validation (k=5) was used for hyperparameter tuning within the training set. Supervised learning algorithms, including logistic regression, decision trees, random forests, and support vector machines (SVM), were implemented using the scikit-learn Python package (Pedregosa et al 2011). Exploratory full-dataset feature-selection visualizations are kept separate from the benchmarking workflow.

## Repo layout
- `analysis/01_qc` QC notebook
- `analysis/02_processing` preprocessing and normalization
- `analysis/03_differential` differential methylation analysis
- `analysis/04_functional` functional analysis and GO heatmap
- `analysis/05_visualization` visualization steps
- `analysis/06_gene_quantification` gene quantification
- `analysis/07_ml` leakage-safe supervised learning notebooks (Python)
- `scripts/` helper scripts
- `data/` placeholder for raw data (not included)
- `metadata/` placeholder for sample metadata (if shareable)
- `output/` generated outputs (not tracked)

## Reproducibility
- R: `renv.lock` (repo root)
- Python: `analysis/07_ml/conda_environment.yml`, `analysis/07_ml/pixi.toml`, or `analysis/07_ml/requirements.txt`

## Notes
- Raw data and generated results are intentionally excluded.
- Add small, shareable metadata tables under `metadata/` if permitted.
- Place IDAT files under `data/idats` and the sample sheet at `metadata/samplesheet.csv`.
- Outputs are written to `output/`, including `output/processed_mVals.csv` used by the ML notebooks.
