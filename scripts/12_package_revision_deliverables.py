from pathlib import Path
import shutil
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parents[1]/'manuscripts/reviewer_round_2/final_drafts'
(OUT/'reports').mkdir(parents=True,exist_ok=True)
(OUT/'figures_main').mkdir(parents=True,exist_ok=True)
(OUT/'tables').mkdir(parents=True,exist_ok=True)
for p in (ROOT/'reports').glob('*/*.html'):
    shutil.copy2(p,OUT/'reports'/p.name)
for p in (ROOT/'figures/main').glob('*'):
    if p.is_file(): shutil.copy2(p,OUT/'figures_main'/p.name)

tables=[
 'analysis_metadata.tsv','metadata_missingness.tsv','pc_metadata_associations.tsv',
 'tsne_sensitivity_summary.tsv','tsne_direct_pca_false_metrics.tsv',
 'subset_analysis_summary.tsv','influential_sample_analysis.tsv',
 'differential_design_estimability.tsv','differential_confounder_sensitivity.tsv',
 'patient_block_correlation.tsv','metadata_only_classifier_summary.tsv',
 'patient_aware_ml_metrics.tsv','patient_aware_ml_partition.tsv',
 'pca_scaled_top_loadings_annotated.tsv','generated_figure_files.tsv']
with pd.ExcelWriter(OUT/'tables/Reviewer_round_2_analysis_tables.xlsx',engine='openpyxl') as writer:
    for name in tables:
        p=ROOT/'results/tables'/name
        if not p.exists(): continue
        df=pd.read_csv(p,sep='\t')
        sheet=p.stem[:31]
        df.to_excel(writer,sheet_name=sheet,index=False)

layout="""# Proposed figure revision map

## Figure 1

- Panels A-D: retain the existing representative histology after author verification.
- Panel E: use `Figure_unsupervised_tSNE` and state explicitly that Rtsne internally used 50 centered, unscaled PCs.
- Panel F: replace the label-informed top-CpG heatmap with `Figure_sample_correlation_heatmap`.
- Move the limma-selected top-500 CpG heatmap to the supplement and label it supervised descriptive visualization.

## New supplementary figures

1. Scaled PCA and baseline t-SNE colored separately by dataset source, Sentrix, age, sex, biopsy site, city and lymphomonocytes.
2. Centered-unscaled PCA colored by the same variables.
3. PCA scree/cumulative variance and PC1-PC3 pairwise projections.
4. PC-metadata association heatmap and annotated loading tables.
5. t-SNE initial-dimension/perplexity/seed stability and direct pca=FALSE t-SNE.
6. Five recomputed subset analyses and individual-sample influence.
7. Differential-methylation covariate and paired-sample sensitivity.
8. Metadata-only and patient-aware classification figures.

All panels are supplied as vector PDF and 600-dpi LZW TIFF.
"""
(OUT/'Figure_revision_map.md').write_text(layout)
print(OUT)
