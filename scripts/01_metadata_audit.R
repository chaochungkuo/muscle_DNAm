source("R/config.R")
source("R/metadata.R")

cfg <- read_project_config()
ensure_output_dirs(cfg$root)

load(file.path(cfg$paths$project_data_root,
  "analysis/DNAmArray/DNAmArray_Processing.RData"))
bias <- read_bias_metadata(cfg$paths$bias_metadata)
key <- read_sample_key(cfg$paths$sample_sheet)
metadata <- build_analysis_metadata(bias, key, colnames(mVals))
validation <- validate_analysis_metadata(metadata, colnames(mVals))

write.table(metadata, "results/tables/analysis_metadata.tsv", sep = "\t",
  row.names = FALSE, quote = FALSE, na = "NA")
write.csv(metadata, "results/tables/analysis_metadata.csv", row.names = FALSE, na = "NA")

tabs <- make_cross_tabs(metadata)
for (name in names(tabs)) {
  write.table(tabs[[name]], file.path("results/tables", paste0("group_by_", name, ".tsv")),
    sep = "\t", row.names = FALSE, quote = FALSE)
}

missingness <- data.frame(
  variable = names(metadata),
  missing_n = vapply(metadata, function(x) sum(is.na(x) | trimws(as.character(x)) == ""), integer(1)),
  unique_nonmissing_n = vapply(metadata, function(x) length(unique(x[!is.na(x) & trimws(as.character(x)) != ""])), integer(1))
)
write.table(missingness, "results/tables/metadata_missingness.tsv", sep = "\t",
  row.names = FALSE, quote = FALSE)

audit <- c(
  paste("timestamp:", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")),
  paste("metadata_rows:", nrow(metadata)),
  paste("matrix_samples:", ncol(mVals)),
  paste("independent_patients:", length(unique(metadata$patient_id))),
  paste("mapping_valid:", validation$ok),
  if (length(validation$issues)) paste("issue:", validation$issues) else "issues: none",
  "policy: Juliane Excel is authoritative for reviewer-round metadata.",
  "policy: lymphomonocytes is displayed as supplied but remains undefined and uninterpreted.",
  "policy: unavailable pathology variables are not inferred."
)
writeLines(audit, "logs/metadata_audit.txt")

if (!validation$ok) stop(paste(validation$issues, collapse = "\n"))
cat(paste(audit, collapse = "\n"), "\n")
