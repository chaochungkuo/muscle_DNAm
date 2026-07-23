clean_names_base <- function(x) {
  x <- trimws(x)
  x <- tolower(x)
  x <- gsub("[^a-z0-9]+", "_", x)
  gsub("^_|_$", "", x)
}

read_bias_metadata <- function(path) {
  x <- readxl::read_excel(path, sheet = 1)
  names(x) <- clean_names_base(names(x))
  names(x)[names(x) == "sample_name_in_metadatasheet"] <- "anonymous_id"
  x$anonymous_id <- as.integer(x$anonymous_id)
  x$sentrix_id <- as.character(x$sentrix_id)
  x$sentrix_position <- as.character(x$sentrix_position)
  x
}

read_sample_key <- function(path) {
  x <- read.csv(path, check.names = FALSE, stringsAsFactors = FALSE,
    fileEncoding = "UTF-8-BOM")
  names(x) <- clean_names_base(names(x))
  names(x)[names(x) == "sample_name_in_metadatasheet"] <- "anonymous_id"
  names(x)[names(x) == "sample_name"] <- "sample_name"
  x$anonymous_id <- suppressWarnings(as.integer(x$anonymous_id))
  x$sample_name <- trimws(x$sample_name)
  x$sentrix_id <- as.character(x$sentrix_id)
  x$sentrix_position <- as.character(x$sentrix_position)
  x
}

build_analysis_metadata <- function(bias, key, matrix_samples) {
  key_keep <- key[!is.na(key$anonymous_id), c(
    "anonymous_id", "sample_name", "sentrix_id", "sentrix_position"
  )]
  names(key_keep)[3:4] <- c("key_sentrix_id", "key_sentrix_position")
  stopifnot(!anyDuplicated(bias$anonymous_id), !anyDuplicated(key_keep$anonymous_id))

  joined <- merge(bias, key_keep, by = "anonymous_id", all.x = TRUE, sort = FALSE)
  joined <- joined[match(bias$anonymous_id, joined$anonymous_id), ]
  joined$matrix_sample <- paste(joined$sample_group, joined$sample_name, sep = ".")

  # External/control labels already include their group-compatible sample tokens.
  direct_match <- joined$matrix_sample %in% matrix_samples
  joined$matrix_sample[!direct_match] <- joined$sample_name[!direct_match]

  joined$in_matrix <- joined$matrix_sample %in% matrix_samples
  joined$sentrix_match <- joined$sentrix_id == joined$key_sentrix_id &
    joined$sentrix_position == joined$key_sentrix_position
  joined$display_group <- ifelse(
    joined$sample_group == "PM", "non-IBM IIM, NOS", joined$sample_group
  )
  joined$display_group <- factor(joined$display_group,
    levels = c("Control", "ALS", "NMA", "IBM", "non-IBM IIM, NOS", "Multiminicores"))
  joined$patient_id <- joined$matrix_sample
  joined$patient_id[joined$matrix_sample %in% c(
    "PM.B2018.30786_Mm", "PM.B2018.30786_Leu"
  )] <- "patient_B2018.30786"
  joined$dataset_source <- ifelse(
    joined$sample_group == "Control", "MALICoT",
      ifelse(joined$sample_group == "Multiminicores", "GEO GSE121961", "In-house data")
  )
  joined
}

validate_analysis_metadata <- function(metadata, matrix_samples) {
  issues <- character()
  if (nrow(metadata) != 73) issues <- c(issues, "Metadata does not contain 73 rows")
  if (anyDuplicated(metadata$matrix_sample)) issues <- c(issues, "Duplicate matrix sample IDs")
  if (length(unique(metadata$patient_id)) != 72) issues <- c(issues,
    "Expected 72 independent patients after assigning the known paired samples")
  missing_matrix <- setdiff(matrix_samples, metadata$matrix_sample)
  extra_metadata <- setdiff(metadata$matrix_sample, matrix_samples)
  if (length(missing_matrix)) issues <- c(issues,
    paste("Matrix samples missing metadata:", paste(missing_matrix, collapse = ", ")))
  if (length(extra_metadata)) issues <- c(issues,
    paste("Metadata samples absent from matrix:", paste(extra_metadata, collapse = ", ")))
  if (any(!metadata$sentrix_match, na.rm = TRUE)) issues <- c(issues,
    "Sentrix ID/position differs between Juliane table and sample key")
  list(ok = length(issues) == 0, issues = issues,
    missing_matrix = missing_matrix, extra_metadata = extra_metadata)
}

make_cross_tabs <- function(metadata) {
  variables <- c("dataset_source", "city_of_origin", "sentrix_id", "age_group", "gender",
    "muscle_location_group", "lymphomonocytes")
  lapply(setNames(variables, variables), function(v) {
    out <- as.data.frame.matrix(table(metadata$display_group, metadata[[v]], useNA = "ifany"))
    out <- data.frame(disease_group = rownames(out), out,
      row.names = NULL, check.names = FALSE)
    out
  })
}
