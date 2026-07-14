read_project_config <- function(root = getwd()) {
  local_path <- file.path(root, "config", "paths.local.yml")
  example_path <- file.path(root, "config", "paths.example.yml")
  path_file <- if (file.exists(local_path)) local_path else example_path
  list(
    root = normalizePath(root, mustWork = TRUE),
    paths = yaml::read_yaml(path_file),
    analysis = yaml::read_yaml(file.path(root, "config", "analysis.yml"))
  )
}

ensure_output_dirs <- function(root) {
  dirs <- c(
    "results/coordinates", "results/tables", "results/models",
    "figures/main", "figures/supplementary", "figures/qc",
    "reports/manuscript_analysis", "reports/reviewer_revision", "logs"
  )
  invisible(vapply(file.path(root, dirs), dir.create, logical(1),
    recursive = TRUE, showWarnings = FALSE))
}
