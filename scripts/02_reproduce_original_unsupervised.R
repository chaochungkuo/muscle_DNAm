source("R/config.R")
source("R/metadata.R")
source("R/plotting.R")
source("R/unsupervised.R")

cfg <- read_project_config()
ensure_output_dirs(cfg$root)
load(file.path(cfg$paths$project_data_root,
  "analysis/DNAmArray/DNAmArray_Processing.RData"))
metadata <- read.delim("results/tables/analysis_metadata.tsv", check.names = FALSE)
stopifnot(identical(colnames(mVals), metadata$matrix_sample))

if (file.exists("results/models/pca_scaled.rds")) {
  message("Loading cached scaled PCA...")
  pca_scaled <- readRDS("results/models/pca_scaled.rds")
} else {
  message("Computing scaled PCA on 771,381 CpGs...")
  pca_scaled <- run_scaled_pca(mVals)
  saveRDS(pca_scaled, "results/models/pca_scaled.rds")
}
pca_df <- pca_coordinates(pca_scaled, colnames(mVals))
pca_df <- attach_metadata(pca_df, metadata)
variance <- attr(pca_coordinates(pca_scaled, colnames(mVals)), "variance_explained")
write.table(pca_df, "results/coordinates/pca_scaled_coordinates.tsv", sep = "\t",
  row.names = FALSE, quote = FALSE)
write.table(data.frame(PC = paste0("PC", seq_along(variance)),
  variance_explained = variance, cumulative_variance = cumsum(variance)),
  "results/tables/pca_scaled_variance.tsv", sep = "\t", row.names = FALSE, quote = FALSE)

if (file.exists("results/coordinates/tsne_baseline_coordinates.tsv")) {
  message("Loading cached baseline t-SNE coordinates...")
  tsne_df <- read.delim("results/coordinates/tsne_baseline_coordinates.tsv", check.names = FALSE)
  tsne_df <- tsne_df[, c("sample_id", "TSNE1", "TSNE2")]
  tsne_df <- attach_metadata(tsne_df, metadata)
  write.table(tsne_df, "results/coordinates/tsne_baseline_coordinates.tsv", sep = "\t",
    row.names = FALSE, quote = FALSE)
} else {
  message("Computing baseline Rtsne (pca=TRUE, initial_dims=50)...")
  tsne <- run_baseline_tsne(mVals, cfg$analysis)
  tsne_df <- data.frame(sample_id = colnames(mVals), TSNE1 = tsne$Y[, 1], TSNE2 = tsne$Y[, 2])
  tsne_df <- attach_metadata(tsne_df, metadata)
  write.table(tsne_df, "results/coordinates/tsne_baseline_coordinates.tsv", sep = "\t",
    row.names = FALSE, quote = FALSE)
}

annotations <- c("display_group", "dataset_source", "city_of_origin", "sentrix_id", "age_group",
  "gender", "muscle_location_group", "lymphomonocytes")
for (variable in annotations) {
  p_pca <- embedding_plot(pca_df, "PC1", "PC2", variable,
    paste("PCA colored by", gsub("_", " ", variable)),
    sprintf("PC1 (%.2f%%)", 100 * variance[1]), sprintf("PC2 (%.2f%%)", 100 * variance[2]))
  p_tsne <- embedding_plot(tsne_df, "TSNE1", "TSNE2", variable,
    paste("t-SNE colored by", gsub("_", " ", variable)), "t-SNE 1", "t-SNE 2")
  save_publish_figure(p_pca, file.path("figures/supplementary", paste0("pca_scaled_by_", variable)))
  save_publish_figure(p_tsne, file.path("figures/supplementary", paste0("tsne_baseline_by_", variable)))
}

save_publish_figure(
  embedding_plot(pca_df, "PC1", "PC2", "display_group", "Unsupervised PCA",
    sprintf("PC1 (%.2f%%)", 100 * variance[1]), sprintf("PC2 (%.2f%%)", 100 * variance[2])),
  "figures/main/Figure_unsupervised_PCA", width = 7.2, height = 5.2)
save_publish_figure(
  embedding_plot(tsne_df, "TSNE1", "TSNE2", "display_group", "Unsupervised t-SNE",
    "t-SNE 1", "t-SNE 2"),
  "figures/main/Figure_unsupervised_tSNE", width = 7.2, height = 5.2)

writeLines(capture.output(sessionInfo()), "logs/session_02_reproduce_original.txt")
cat("Baseline PCA/t-SNE reproduction complete.\n")
