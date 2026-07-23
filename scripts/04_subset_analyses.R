source("R/config.R"); source("R/plotting.R"); source("R/unsupervised.R")
cfg<-read_project_config(); ensure_output_dirs(cfg$root)
load(file.path(cfg$paths$project_data_root,"analysis/DNAmArray/DNAmArray_Processing.RData"))
metadata<-read.delim("results/tables/analysis_metadata.tsv",check.names=FALSE)
metadata<-metadata[match(colnames(mVals),metadata$matrix_sample),]

subsets<-list(
  excluding_MMC=metadata$sample_group!="Multiminicores",
  excluding_controls=metadata$sample_group!="Control",
  in_house_data=metadata$dataset_source=="In-house data",
  IBM_vs_nonIBM_IIM=metadata$sample_group%in%c("IBM","PM"),
  ALS_vs_nonALS_NMA=metadata$sample_group%in%c("ALS","NMA")
)
all_coords<-list(); summaries<-list()

embedding_plot_large <- function(data, x, y, color_by, title, x_label = x, y_label = y) {
  data$.color_group <- factor(data[[color_by]])
  color_values <- data$.color_group
  palette <- if (color_by == "display_group") disease_palette else discrete_palette(color_values)
  ggplot2::ggplot(data, ggplot2::aes(x = .data[[x]], y = .data[[y]], color = .data$.color_group)) +
    ggplot2::geom_point(size = 4.0, alpha = 0.92) +
    ggplot2::scale_color_manual(values = palette, na.value = "#CCCCCC", drop = FALSE) +
    ggplot2::labs(
      x = x_label,
      y = y_label,
      color = ifelse(color_by == "display_group", "Disease group", gsub("_", " ", color_by)),
      title = title
    ) +
    publication_theme(base_size = 16) +
    ggplot2::theme(
      plot.title = ggplot2::element_text(face = "bold", size = 17),
      axis.title = ggplot2::element_text(face = "bold", size = 16),
      axis.text = ggplot2::element_text(size = 13),
      legend.title = ggplot2::element_text(face = "bold", size = 14),
      legend.text = ggplot2::element_text(size = 12),
      legend.key.size = grid::unit(0.45, "cm")
    ) +
    ggplot2::guides(color = ggplot2::guide_legend(override.aes = list(size = 4.2)))
}

if (!file.exists("results/coordinates/subset_coordinates.tsv")) {
for(nm in names(subsets)){
  keep<-subsets[[nm]]; x<-mVals[,keep,drop=FALSE]; md<-metadata[keep,,drop=FALSE]
  message("Subset ",nm,": n=",ncol(x))
  pca<-prcomp(t(x),center=TRUE,scale.=TRUE,rank.=min(ncol(x)-1,20))
  vv<-pca$sdev^2/sum(pca$sdev^2)
  set.seed(42)
  perp<-min(15,max(2,floor((ncol(x)-1)/3)-1))
  ts<-Rtsne::Rtsne(t(x),dims=2,perplexity=perp,theta=.5,pca=TRUE,
    initial_dims=min(50,ncol(x)-1),check_duplicates=FALSE)
  d<-data.frame(subset=nm,sample_id=colnames(x),PC1=pca$x[,1],PC2=pca$x[,2],
    TSNE1=ts$Y[,1],TSNE2=ts$Y[,2],md)
  all_coords[[nm]]<-d
  summaries[[nm]]<-data.frame(subset=nm,n=ncol(x),groups=paste(sort(unique(md$display_group)),collapse="; "),
    perplexity=perp,PC1_variance=vv[1],PC2_variance=vv[2],
    PCA_disease_silhouette=mean(cluster::silhouette(as.integer(factor(md$display_group)),dist(pca$x[,1:min(10,ncol(pca$x)),drop=FALSE]))[,3]),
    TSNE_disease_silhouette=mean(cluster::silhouette(as.integer(factor(md$display_group)),dist(ts$Y))[,3]))
  pp<-embedding_plot(d,"PC1","PC2","display_group",paste("PCA:",gsub("_"," ",nm)),
    sprintf("PC1 (%.2f%%)",100*vv[1]),sprintf("PC2 (%.2f%%)",100*vv[2]))
  pt<-embedding_plot(d,"TSNE1","TSNE2","display_group",paste("t-SNE:",gsub("_"," ",nm)))
  save_publish_figure(pp,file.path("figures/supplementary",paste0("subset_",nm,"_PCA")),7,5)
  save_publish_figure(pt,file.path("figures/supplementary",paste0("subset_",nm,"_tSNE")),7,5)
}
write.table(do.call(rbind,all_coords),"results/coordinates/subset_coordinates.tsv",sep="\t",row.names=FALSE,quote=FALSE)
write.table(do.call(rbind,summaries),"results/tables/subset_analysis_summary.tsv",sep="\t",row.names=FALSE,quote=FALSE)
} else {
  cached <- read.delim("results/coordinates/subset_coordinates.tsv", check.names=FALSE)
  all_coords <- split(cached, cached$subset)
}

# Always regenerate publication plots from cached/recomputed coordinates using
# larger text and legends for A4-size multi-panel rebuttal figures.
summary_df <- read.delim("results/tables/subset_analysis_summary.tsv", check.names = FALSE)
for (nm in names(subsets)) {
  d <- all_coords[[nm]]
  ss <- summary_df[summary_df$subset == nm, , drop = FALSE]
  pp <- embedding_plot_large(d, "PC1", "PC2", "display_group", paste("PCA:", gsub("_", " ", nm)),
    sprintf("PC1 (%.2f%%)", 100 * ss$PC1_variance[1]),
    sprintf("PC2 (%.2f%%)", 100 * ss$PC2_variance[1]))
  pt <- embedding_plot_large(d, "TSNE1", "TSNE2", "display_group", paste("t-SNE:", gsub("_", " ", nm)))
  save_publish_figure(pp, file.path("figures/supplementary", paste0("subset_", nm, "_PCA")), 8.4, 6.0, dpi = 900)
  save_publish_figure(pt, file.path("figures/supplementary", paste0("subset_", nm, "_tSNE")), 8.4, 6.0, dpi = 900)
}

# Influence analysis in clinically relevant contrasts using leave-one-out
# nearest-centroid accuracy in a recomputed centered/unscaled PC space.
influence<-list()
for(nm in c("IBM_vs_nonIBM_IIM","ALS_vs_nonALS_NMA")){
  d <- all_coords[[nm]]; y<-droplevels(factor(d$display_group)); ids<-d$sample_id
  zfull<-as.matrix(d[,c("PC1","PC2")])
  full_sil<-mean(cluster::silhouette(as.integer(y),dist(zfull))[,3])
  for(i in seq_len(nrow(d))){
    z<-zfull[-i,,drop=FALSE]; yy<-y[-i]
    s<-mean(cluster::silhouette(as.integer(yy),dist(z))[,3])
    influence[[length(influence)+1]]<-data.frame(subset=nm,removed_sample=ids[i],removed_group=y[i],
      full_silhouette=full_sil,leave_one_out_silhouette=s,delta=s-full_sil)
  }
}
influence<-do.call(rbind,influence)
write.table(influence,"results/tables/influential_sample_analysis.tsv",sep="\t",row.names=FALSE,quote=FALSE)
pinf<-ggplot2::ggplot(influence,ggplot2::aes(reorder(removed_sample,delta),delta,fill=removed_group))+
  ggplot2::geom_col()+ggplot2::coord_flip()+ggplot2::facet_wrap(~subset,scales="free_y")+
  ggplot2::labs(x="Removed sample",y="Change in silhouette",fill="Disease group",title="Influence of individual samples")+publication_theme()
save_publish_figure(pinf,"figures/supplementary/influential_sample_analysis",9,8)
writeLines(capture.output(sessionInfo()),"logs/session_04_subset_analyses.txt")
cat("Subset and influence analyses complete.\n")
