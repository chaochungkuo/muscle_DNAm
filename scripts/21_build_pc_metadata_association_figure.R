source("R/plotting.R")

assoc <- read.delim("results/tables/pc_metadata_associations.tsv", check.names = FALSE)

pc_levels <- paste0("PC", seq_len(20))
variable_levels <- c(
  "display_group",
  "dataset_source",
  "city_of_origin",
  "sentrix_id",
  "age_group",
  "gender",
  "muscle_location_group",
  "lymphomonocytes"
)

assoc$PC <- factor(assoc$PC, levels = pc_levels)
assoc$variable <- factor(assoc$variable, levels = rev(variable_levels))
assoc$PCA <- factor(assoc$PCA, levels = c("scaled", "unscaled"),
  labels = c("Centered, scaled PCA", "Centered, unscaled PCA"))

p_assoc <- ggplot2::ggplot(
  assoc,
  ggplot2::aes(x = PC, y = variable, fill = eta_squared)
) +
  ggplot2::geom_tile(color = "white", linewidth = 0.25) +
  ggplot2::facet_wrap(~PCA, ncol = 1) +
  ggplot2::scale_fill_viridis_c(limits = c(0, 1), option = "viridis") +
  ggplot2::scale_x_discrete(drop = FALSE) +
  ggplot2::scale_y_discrete(
    drop = FALSE,
    labels = c(
      "display_group" = "Disease group",
      "dataset_source" = "Dataset source",
      "city_of_origin" = "City",
      "sentrix_id" = "Sentrix ID",
      "age_group" = "Age group",
      "gender" = "Sex",
      "muscle_location_group" = "Biopsy site",
      "lymphomonocytes" = "Lymphomonocytes"
    )
  ) +
  ggplot2::labs(
    x = "Principal component",
    y = NULL,
    fill = expression(eta^2),
    title = "PC–metadata associations"
  ) +
  publication_theme(base_size = 11) +
  ggplot2::theme(
    axis.text.x = ggplot2::element_text(angle = 45, hjust = 1, vjust = 1),
    panel.spacing = grid::unit(0.35, "lines"),
    strip.background = ggplot2::element_blank(),
    strip.text = ggplot2::element_text(face = "bold")
  )

dir.create("figures/main", recursive = TRUE, showWarnings = FALSE)
dir.create("figures/response", recursive = TRUE, showWarnings = FALSE)
dir.create("figures/web", recursive = TRUE, showWarnings = FALSE)

for (stem in c(
  "figures/main/Figure_PC_metadata_associations",
  "figures/response/Response_Figure_1C_PC_metadata_associations",
  "figures/web/Figure_PC_metadata_associations"
)) {
  ggplot2::ggsave(paste0(stem, ".pdf"), p_assoc, width = 9, height = 6.5,
    units = "in", device = grDevices::cairo_pdf)
  ggplot2::ggsave(paste0(stem, ".tiff"), p_assoc, width = 9, height = 6.5,
    units = "in", dpi = 600, compression = "lzw", bg = "white")
  ggplot2::ggsave(paste0(stem, ".png"), p_assoc, width = 9, height = 6.5,
    units = "in", dpi = 300, bg = "white")
}

message("Wrote PC–metadata association figures with natural PC1–PC20 x-axis order.")
