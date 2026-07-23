attach_metadata <- function(coordinates, metadata, sample_col = "sample_id") {
  idx <- match(coordinates[[sample_col]], metadata$matrix_sample)
  if (anyNA(idx)) stop("Coordinate samples missing from metadata")
  cbind(coordinates, metadata[idx, setdiff(names(metadata), "matrix_sample"), drop = FALSE])
}

run_scaled_pca <- function(m_values) {
  stats::prcomp(t(m_values), center = TRUE, scale. = TRUE, rank. = ncol(m_values) - 1)
}

run_unscaled_pca <- function(m_values) {
  stats::prcomp(t(m_values), center = TRUE, scale. = FALSE, rank. = ncol(m_values) - 1)
}

pca_coordinates <- function(pca, sample_ids) {
  variance <- pca$sdev^2 / sum(pca$sdev^2)
  out <- data.frame(sample_id = sample_ids, pca$x, check.names = FALSE)
  attr(out, "variance_explained") <- variance
  out
}

run_baseline_tsne <- function(m_values, config) {
  pars <- config$tsne$baseline
  set.seed(pars$seed)
  Rtsne::Rtsne(t(m_values), dims = pars$dims, perplexity = pars$perplexity,
    theta = pars$theta, pca = pars$pca, initial_dims = pars$initial_dims,
    check_duplicates = FALSE)
}
