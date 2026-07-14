required <- c(
  "yaml", "readxl", "Rtsne", "ggplot2", "pheatmap",
  "minfi", "limma", "DMRcate", "missMethyl", "clusterProfiler"
)
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing) > 0) {
  stop("Missing required R packages: ", paste(missing, collapse = ", "))
}
cat("R environment check passed.\n")
cat("R version:", R.version.string, "\n")
