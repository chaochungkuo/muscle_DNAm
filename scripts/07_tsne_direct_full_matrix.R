source("R/config.R"); source("R/metadata.R"); source("R/plotting.R"); source("R/unsupervised.R")
cfg<-read_project_config(); ensure_output_dirs(cfg$root)
load(file.path(cfg$paths$project_data_root,"analysis/DNAmArray/DNAmArray_Processing.RData"))
metadata<-read.delim("results/tables/analysis_metadata.tsv",check.names=FALSE)
metadata<-metadata[match(colnames(mVals),metadata$matrix_sample),]
start<-Sys.time(); set.seed(42)
fit<-Rtsne::Rtsne(t(mVals),dims=2,perplexity=15,theta=.5,pca=FALSE,
  check_duplicates=FALSE,normalize=TRUE)
elapsed<-as.numeric(difftime(Sys.time(),start,units="mins"))
d<-data.frame(sample_id=colnames(mVals),TSNE1=fit$Y[,1],TSNE2=fit$Y[,2])
d<-attach_metadata(d,metadata)
write.table(d,"results/coordinates/tsne_direct_pca_false_coordinates.tsv",sep="\t",row.names=FALSE,quote=FALSE)
write.table(data.frame(pca=FALSE,perplexity=15,theta=.5,seed=42,elapsed_minutes=elapsed),
  "results/tables/tsne_direct_pca_false_runtime.tsv",sep="\t",row.names=FALSE,quote=FALSE)
baseline<-read.delim("results/coordinates/tsne_baseline_coordinates.tsv",check.names=FALSE)
procorr<-function(a,b){a<-scale(a,scale=FALSE);b<-scale(b,scale=FALSE);s<-svd(t(b)%*%a);br<-b%*%(s$u%*%t(s$v));cor(as.vector(a),as.vector(br))}
sil<-function(x,g)mean(cluster::silhouette(as.integer(factor(g)),dist(x))[,3])
metrics<-data.frame(
  procrustes_correlation=procorr(as.matrix(baseline[,c("TSNE1","TSNE2")]),fit$Y),
  disease_silhouette=sil(fit$Y,metadata$display_group)
)
write.table(metrics,"results/tables/tsne_direct_pca_false_metrics.tsv",sep="\t",row.names=FALSE,quote=FALSE)
p<-embedding_plot(d,"TSNE1","TSNE2","display_group","Direct full-matrix t-SNE (pca = FALSE)")
save_publish_figure(p,"figures/main/Figure_tSNE_direct_pca_false",7.2,5.2)
cat("Direct pca=FALSE t-SNE complete in",elapsed,"minutes.\n")
