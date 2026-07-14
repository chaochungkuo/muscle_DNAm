source("R/config.R")
source("R/metadata.R")
source("R/plotting.R")
source("R/unsupervised.R")

cfg <- read_project_config(); ensure_output_dirs(cfg$root)
load(file.path(cfg$paths$project_data_root, "analysis/DNAmArray/DNAmArray_Processing.RData"))
metadata <- read.delim("results/tables/analysis_metadata.tsv", check.names = FALSE)
metadata <- metadata[match(colnames(mVals), metadata$matrix_sample), ]
stopifnot(!anyNA(metadata$matrix_sample))

# Official Rtsne internal PCA: centered, unscaled M-values.
if (file.exists("results/models/pca_unscaled.rds")) {
  pca_unscaled <- readRDS("results/models/pca_unscaled.rds")
} else {
  message("Computing centered, unscaled PCA...")
  pca_unscaled <- run_unscaled_pca(mVals)
  saveRDS(pca_unscaled, "results/models/pca_unscaled.rds")
}
unscaled_df <- attach_metadata(pca_coordinates(pca_unscaled, colnames(mVals)), metadata)
unscaled_var <- pca_unscaled$sdev^2 / sum(pca_unscaled$sdev^2)
write.table(unscaled_df, "results/coordinates/pca_unscaled_coordinates.tsv", sep="\t", row.names=FALSE, quote=FALSE)
write.table(data.frame(PC=paste0("PC",seq_along(unscaled_var)), variance_explained=unscaled_var,
  cumulative_variance=cumsum(unscaled_var)), "results/tables/pca_unscaled_variance.tsv",
  sep="\t", row.names=FALSE, quote=FALSE)

# Scree and cumulative variance for scaled and unscaled PCA.
scaled_var <- read.delim("results/tables/pca_scaled_variance.tsv")
uv <- data.frame(PC=seq_len(20), variance=100*unscaled_var[1:20], cumulative=100*cumsum(unscaled_var)[1:20], PCA="Centered, unscaled")
sv <- data.frame(PC=seq_len(20), variance=100*scaled_var$variance_explained[1:20], cumulative=100*scaled_var$cumulative_variance[1:20], PCA="Centered, scaled")
variance_df <- rbind(sv,uv)
p_scree <- ggplot2::ggplot(variance_df, ggplot2::aes(PC,variance,color=PCA)) + ggplot2::geom_line() +
  ggplot2::geom_point() + ggplot2::labs(y="Variance explained (%)",title="PCA scree plot") + publication_theme()
p_cum <- ggplot2::ggplot(variance_df, ggplot2::aes(PC,cumulative,color=PCA)) + ggplot2::geom_line() +
  ggplot2::geom_point() + ggplot2::labs(y="Cumulative variance explained (%)",title="PCA cumulative variance") + publication_theme()
save_publish_figure(p_scree,"figures/main/Figure_PCA_scree",7,5)
save_publish_figure(p_cum,"figures/supplementary/PCA_cumulative_variance",7,5)

# Multiple PC projections for both PCA definitions.
scaled_df <- read.delim("results/coordinates/pca_scaled_coordinates.tsv",check.names=FALSE)
pca_scaled <- readRDS("results/models/pca_scaled.rds")
for (kind in c("scaled","unscaled")) {
  d <- if(kind=="scaled") scaled_df else unscaled_df
  vv <- if(kind=="scaled") scaled_var$variance_explained else unscaled_var
  for(pair in list(c(1,2),c(1,3),c(2,3))) {
    x<-paste0("PC",pair[1]); y<-paste0("PC",pair[2])
    p<-embedding_plot(d,x,y,"display_group",paste("PCA",kind,x,"vs",y),
      sprintf("%s (%.2f%%)",x,100*vv[pair[1]]),sprintf("%s (%.2f%%)",y,100*vv[pair[2]]))
    save_publish_figure(p,file.path("figures/supplementary",paste0("PCA_",kind,"_",x,"_",y)))
  }
}

# PC association audit using eta-squared from one-variable ANOVA.
variables <- c("display_group","dataset_source","city_of_origin","sentrix_id","age_group","gender","muscle_location_group","lymphomonocytes")
for (variable in variables) {
  p <- embedding_plot(unscaled_df, "PC1", "PC2", variable,
    paste("Centered, unscaled PCA colored by", gsub("_", " ", variable)),
    sprintf("PC1 (%.2f%%)", 100 * unscaled_var[1]),
    sprintf("PC2 (%.2f%%)", 100 * unscaled_var[2]))
  save_publish_figure(p, file.path("figures/supplementary",
    paste0("pca_unscaled_by_", variable)))
}
assoc_one <- function(scores, var, kind) {
  y <- factor(metadata[[var]])
  do.call(rbind,lapply(1:20,function(i){
    fit<-lm(scores[,i]~y); a<-anova(fit); eta<-a$`Sum Sq`[1]/sum(a$`Sum Sq`)
    data.frame(PCA=kind,PC=paste0("PC",i),variable=var,eta_squared=eta,p_value=a$`Pr(>F)`[1])
  }))
}
assoc <- do.call(rbind,c(lapply(variables,function(v)assoc_one(pca_scaled$x,v,"scaled")),
  lapply(variables,function(v)assoc_one(pca_unscaled$x,v,"unscaled"))))
assoc$fdr <- p.adjust(assoc$p_value,"BH")
write.table(assoc,"results/tables/pc_metadata_associations.tsv",sep="\t",row.names=FALSE,quote=FALSE)
p_assoc <- ggplot2::ggplot(assoc,ggplot2::aes(PC,variable,fill=eta_squared)) + ggplot2::geom_tile() +
  ggplot2::facet_wrap(~PCA,ncol=1) + ggplot2::scale_fill_viridis_c() +
  ggplot2::labs(fill=expression(eta^2),title="Association of leading PCs with supplied metadata") + publication_theme() +
  ggplot2::theme(axis.text.x=ggplot2::element_text(angle=45,hjust=1))
save_publish_figure(p_assoc,"figures/main/Figure_PC_metadata_associations",9,7)

# Highest positive/negative loadings.
loadings <- do.call(rbind,lapply(1:5,function(i){
  ordp<-order(pca_scaled$rotation[,i],decreasing=TRUE)[1:100]
  ordn<-order(pca_scaled$rotation[,i],decreasing=FALSE)[1:100]
  rbind(data.frame(PC=paste0("PC",i),direction="positive",CpG=rownames(pca_scaled$rotation)[ordp],loading=pca_scaled$rotation[ordp,i]),
    data.frame(PC=paste0("PC",i),direction="negative",CpG=rownames(pca_scaled$rotation)[ordn],loading=pca_scaled$rotation[ordn,i]))
}))
write.table(loadings,"results/tables/pca_scaled_top_loadings.tsv",sep="\t",row.names=FALSE,quote=FALSE)

# t-SNE sensitivity using the exact centered/unscaled PC score basis used internally by Rtsne.
grid <- expand.grid(initial_dims=cfg$analysis$tsne$sensitivity$initial_dims,
  perplexity=cfg$analysis$tsne$sensitivity$perplexities,
  seed=cfg$analysis$tsne$sensitivity$seeds,KEEP.OUT.ATTRS=FALSE)
baseline <- read.delim("results/coordinates/tsne_baseline_coordinates.tsv",check.names=FALSE)
base_xy <- as.matrix(baseline[,c("TSNE1","TSNE2")])
sil <- function(x,g) mean(cluster::silhouette(as.integer(factor(g)),dist(x))[,3])
procorr <- function(a,b) {
  a<-scale(a,scale=FALSE); b<-scale(b,scale=FALSE)
  s<-svd(t(b)%*%a); br<-b%*%(s$u%*%t(s$v)); cor(as.vector(a),as.vector(br))
}
summaries <- vector("list",nrow(grid))
all_coords <- vector("list",nrow(grid))
for(i in seq_len(nrow(grid))){
  g<-grid[i,]; set.seed(g$seed)
  fit<-Rtsne::Rtsne(pca_unscaled$x[,seq_len(g$initial_dims),drop=FALSE],pca=FALSE,normalize=TRUE,
    check_duplicates=FALSE,dims=2,perplexity=g$perplexity,theta=0.5)
  xy<-fit$Y
  summaries[[i]]<-data.frame(g,procrustes_correlation=procorr(base_xy,xy),
    disease_silhouette=sil(xy,metadata$display_group))
  all_coords[[i]]<-data.frame(run_id=i,sample_id=colnames(mVals),TSNE1=xy[,1],TSNE2=xy[,2],g)
}
sens_summary<-do.call(rbind,summaries); sens_coords<-do.call(rbind,all_coords)
write.table(sens_summary,"results/tables/tsne_sensitivity_summary.tsv",sep="\t",row.names=FALSE,quote=FALSE)
write.table(sens_coords,"results/coordinates/tsne_sensitivity_coordinates.tsv.gz",sep="\t",row.names=FALSE,quote=FALSE)
p_stab<-ggplot2::ggplot(sens_summary,ggplot2::aes(factor(perplexity),procrustes_correlation,fill=factor(initial_dims)))+
  ggplot2::geom_boxplot(position=ggplot2::position_dodge(.8)) + ggplot2::labs(x="Perplexity",fill="Initial dimensions",y="Procrustes correlation",title="t-SNE stability across random seeds")+publication_theme()
save_publish_figure(p_stab,"figures/main/Figure_tSNE_stability",8,5)

# Full-matrix, label-free sample correlation heatmap.
sample_cor <- cor(mVals,method="pearson")
write.table(sample_cor,"results/tables/sample_correlations.tsv.gz",sep="\t",quote=FALSE)
ann <- data.frame(Disease=metadata$display_group,Source=metadata$dataset_source,City=metadata$city_of_origin,Sentrix=factor(metadata$sentrix_id),
  Age=metadata$age_group,Sex=metadata$gender,Site=metadata$muscle_location_group,Lymphomonocytes=metadata$lymphomonocytes)
rownames(ann)<-colnames(mVals)
pdf("figures/main/Figure_sample_correlation_heatmap.pdf",width=12,height=11)
hp<-pheatmap::pheatmap(sample_cor,clustering_distance_rows=as.dist(1-sample_cor),
  clustering_distance_cols=as.dist(1-sample_cor),clustering_method="complete",annotation_col=ann,
  annotation_row=ann,show_rownames=FALSE,show_colnames=FALSE,border_color=NA,
  main="Unsupervised sample-to-sample correlation")
dev.off()
tiff("figures/main/Figure_sample_correlation_heatmap.tiff",width=12,height=11,units="in",res=600,compression="lzw")
pheatmap::pheatmap(sample_cor,clustering_distance_rows=as.dist(1-sample_cor),
  clustering_distance_cols=as.dist(1-sample_cor),clustering_method="complete",annotation_col=ann,
  annotation_row=ann,show_rownames=FALSE,show_colnames=FALSE,border_color=NA,
  main="Unsupervised sample-to-sample correlation")
dev.off()
write.table(data.frame(order=seq_along(hp$tree_col$order),sample_id=colnames(mVals)[hp$tree_col$order]),
  "results/tables/sample_correlation_cluster_order.tsv",sep="\t",row.names=FALSE,quote=FALSE)
writeLines(capture.output(sessionInfo()),"logs/session_03_unsupervised_bias_checks.txt")
cat("Unsupervised bias checks complete.\n")
