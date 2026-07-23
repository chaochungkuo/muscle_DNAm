publication_theme <- function(base_size = 10) {
  ggplot2::theme_classic(base_size = base_size) +
    ggplot2::theme(
      plot.title = ggplot2::element_text(face = "bold", size = base_size + 1),
      legend.title = ggplot2::element_text(face = "bold"),
      legend.position = "right",
      axis.title = ggplot2::element_text(face = "bold")
    )
}

disease_palette <- c(
  "Control" = "#666666", "ALS" = "#D73027", "NMA" = "#FC8D59",
  "IBM" = "#4575B4", "non-IBM IIM, NOS" = "#74ADD1",
  "Multiminicores" = "#1A9850"
)

discrete_palette <- function(values) {
  lev <- sort(unique(as.character(values[!is.na(values)])))
  setNames(scales::hue_pal()(length(lev)), lev)
}

embedding_plot <- function(data, x, y, color_by, title, x_label = x, y_label = y) {
  data$.color_group <- factor(data[[color_by]])
  color_values <- data$.color_group
  palette <- if (color_by == "display_group") disease_palette else discrete_palette(color_values)
  ggplot2::ggplot(data, ggplot2::aes(x = .data[[x]], y = .data[[y]], color = .data$.color_group)) +
    ggplot2::geom_point(size = 2.7, alpha = 0.9) +
    ggplot2::scale_color_manual(values = palette, na.value = "#CCCCCC", drop = FALSE) +
    ggplot2::labs(x = x_label, y = y_label,
      color = ifelse(color_by == "display_group", "Disease group", gsub("_", " ", color_by)),
      title = title) +
    publication_theme()
}

save_publish_figure <- function(plot, stem, width = 7, height = 5, dpi = 600) {
  dir.create(dirname(stem), recursive = TRUE, showWarnings = FALSE)
  ggplot2::ggsave(paste0(stem, ".pdf"), plot, width = width, height = height,
    units = "in", device = grDevices::cairo_pdf)
  ggplot2::ggsave(paste0(stem, ".tiff"), plot, width = width, height = height,
    units = "in", dpi = dpi, compression = "lzw", bg = "white")
  invisible(stem)
}
