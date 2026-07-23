# Reviewer-round unsupervised bias check

This stage will be implemented sequentially after the metadata audit.

Planned reports:

1. `01_reproduce_original.qmd`: reproduce submitted PCA and t-SNE exactly
2. `02_tsne_sensitivity.qmd`: initial dimensions, perplexities, seeds, and direct-input feasibility
3. `03_pca_bias_check.qmd`: scree, PC pairs, scaled/unscaled PCA, metadata associations, and loadings
4. `04_sample_correlation.qmd`: label-free correlation-based sample clustering
5. `05_subset_and_influence.qmd`: reviewer-specified recomputed subsets and influential samples

Juliane's Excel is the authoritative metadata source for this stage. The supplied
`lymphomonocytes` field is descriptive and undefined; it must not be interpreted
or used as a model covariate without provenance supplied by the clinical team.
