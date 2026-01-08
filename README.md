# muscle_DNAm

Analysis scripts for the manuscript:
> Entity-specific DNA methylation patterns in non-neoplastic skeletal muscle pathology

## Overview
This repository contains only analysis notebooks/scripts and reproducibility files. It excludes raw data and generated outputs (figures, tables, reports).

## Methods summary

### Data processing and statistics

Array data analysis was performed using R v.4.3.3, using a number of packages from Bioconductor and other repositories. Raw signal intensities were obtained from IDAT files using the minfi R package (Aryee et al 2014). Each sample was individually normalised by performing background correction for both colour channels. Subsequently, several filtering criteria were applied to the initial CpG sites (865859): removal of probes targeting X and Y chromosomes (18507), removal of probes containing single nucleotide polymorphism within five base pairs spanning and within the targeted CpG site (46224), and probes with bad quality (23956). Normalization was performed using the preprocessQuantile function in minfi (Touleimat & Tost 2012). The M values of the filtered probes were used for principal component analysis (PCA) and t-SNE clustering (Rtsne package v.0.17). Differential methylation analysis was conducted using the limma R package (Ritchie et al 2015) on the M values of all CpG sites with the annotation on human genome hg19. The adjusted p-values were corrected using the Benjamini-Hochberg procedure to calculate the False Discovery Rate (FDR). Gene Set Enrichment Analysis (GSEA) was performed using the clusterProfiler R package (Yu et al 2012). Customized heatmaps were generated using the pheatmap R package (Kolde 2018).

### Supervised Learning for Predicting Diagnosis

The normalized M values of 779,612 CpG sites were loaded, and CpG sites with low variance (331,054) were removed. Univariate feature selection was then applied to retain the top 2,000 CpG sites. Of these, 50% were selected based on their mutual information with the target variables. Finally, Random Forest Feature Selection was applied to identify the CpG sites most relevant to their labels, resulting in a final selection of 50 CpG sites for supervised learning. The dataset was split into a training set (n=45) and a test set (n=30) while maintaining the proportional distribution of labels. K-fold cross-validation (k=5) was employed for model evaluation. Supervised learning algorithms, including logistic regression, decision trees, random forests, and support vector machines (SVM), were implemented using the scikit-learn Python package (Pedregosa et al 2011).

## Repo layout
- `analysis/01_qc` QC notebook
- `analysis/02_processing` preprocessing and normalization
- `analysis/03_differential` differential methylation analysis
- `analysis/04_functional` functional analysis and GO heatmap
- `analysis/05_visualization` visualization steps
- `analysis/06_gene_quantification` gene quantification
- `analysis/07_ml` supervised learning notebooks (Python)
- `env/` Python requirements
- `scripts/` helper scripts
- `data/` placeholder for raw data (not included)
- `metadata/` placeholder for sample metadata (if shareable)
- `output/` generated outputs (not tracked)

## Reproducibility
- R: `renv.lock` (repo root)
- Python: `env/requirements.txt`

## Notes
- Raw data and generated results are intentionally excluded.
- Add small, shareable metadata tables under `metadata/` if permitted.
- Place IDAT files under `data/idats` and the sample sheet at `metadata/samplesheet.csv`.
- Outputs are written to `output/`, including `output/processed_mVals.csv` used by the ML notebooks.
