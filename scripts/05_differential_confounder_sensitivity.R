source("R/config.R"); source("R/plotting.R")
cfg<-read_project_config(); ensure_output_dirs(cfg$root)
load(file.path(cfg$paths$project_data_root,"analysis/DNAmArray/DNAmArray_Processing.RData"))
metadata<-read.delim("results/tables/analysis_metadata.tsv",check.names=FALSE)
metadata<-metadata[match(colnames(mVals),metadata$matrix_sample),]
metadata$group<-factor(metadata$sample_group)
metadata$age_group<-factor(metadata$age_group); metadata$gender<-factor(metadata$gender)
metadata$site<-factor(metadata$muscle_location_group); metadata$source<-factor(metadata$dataset_source)
metadata$sentrix<-factor(metadata$sentrix_id)

forms<-list(unadjusted=~0+group,age_sex=~0+group+age_group+gender,
  biopsy_site=~0+group+site,source=~0+group+source,sentrix=~0+group+sentrix)
audit<-do.call(rbind,lapply(names(forms),function(nm){
  d<-model.matrix(forms[[nm]],metadata)
  data.frame(model=nm,n=nrow(d),parameters=ncol(d),rank=qr(d)$rank,
    full_rank=qr(d)$rank==ncol(d),residual_df=nrow(d)-qr(d)$rank)
}))
write.table(audit,"results/tables/differential_design_estimability.tsv",sep="\t",row.names=FALSE,quote=FALSE)

contrasts<-c(ALS_vs_Control="ALS-Control",IBM_vs_Control="IBM-Control",
  Multiminicores_vs_Control="Multiminicores-Control",NMA_vs_Control="NMA-Control",
  PM_vs_Control="PM-Control",ALS_vs_NMA="ALS-NMA",IBM_vs_PM="IBM-PM")
fit_model<-function(nm){
  design<-model.matrix(forms[[nm]],metadata)
  colnames(design)<-make.names(sub("^group","",colnames(design)))
  if(qr(design)$rank<ncol(design)) return(NULL)
  cm<-limma::makeContrasts(contrasts=unname(contrasts),levels=design); colnames(cm)<-names(contrasts)
  limma::eBayes(limma::contrasts.fit(limma::lmFit(mVals,design),cm))
}
fits<-lapply(audit$model[audit$full_rank],fit_model); names(fits)<-audit$model[audit$full_rank]
if(!"unadjusted"%in%names(fits))stop("Unadjusted model failed")

# Patient-aware model for the known paired samples. All other blocks are singletons.
base_design <- model.matrix(~0+group, metadata)
colnames(base_design) <- sub("^group", "", colnames(base_design))
base_cm <- limma::makeContrasts(contrasts=unname(contrasts), levels=base_design)
colnames(base_cm) <- names(contrasts)
repeated_patients <- sum(table(metadata$patient_id) > 1)
patient_cor <- if (repeated_patients >= 2) {
  limma::duplicateCorrelation(mVals, base_design, block=metadata$patient_id)
} else list(consensus.correlation=NA_real_)
patient_estimable <- is.finite(patient_cor$consensus.correlation)
if (patient_estimable) {
  fits$patient_block <- limma::eBayes(limma::contrasts.fit(
    limma::lmFit(mVals, base_design, block=metadata$patient_id,
      correlation=patient_cor$consensus.correlation), base_cm))
}
write.table(data.frame(estimable=patient_estimable,
  consensus_correlation=patient_cor$consensus.correlation,
  repeated_patients=repeated_patients,samples=ncol(mVals),patients=length(unique(metadata$patient_id)),
  note=ifelse(patient_estimable,"Patient block model fitted",
    "Not estimable from only one patient with repeated samples; use paired-sample exclusion sensitivity")),
  "results/tables/patient_block_correlation.tsv",sep="\t",row.names=FALSE,quote=FALSE)

# Sensitivity to retaining either one of the two samples from the repeated patient.
for (drop_id in c("PM.B2018.30786_Mm", "PM.B2018.30786_Leu")) {
  keep <- metadata$matrix_sample != drop_id
  md <- droplevels(metadata[keep, ]); md$group <- droplevels(factor(md$sample_group))
  design <- model.matrix(~0+group, md); colnames(design) <- sub("^group", "", colnames(design))
  cm <- limma::makeContrasts(contrasts=unname(contrasts),levels=design); colnames(cm)<-names(contrasts)
  key <- if (grepl("_Mm$", drop_id)) "drop_paired_Mm" else "drop_paired_Leu"
  fits[[key]] <- limma::eBayes(limma::contrasts.fit(limma::lmFit(mVals[,keep],design),cm))
}
summary<-list(); pairwise<-list()
for(comp in names(contrasts)){
  ref<-limma::topTable(fits$unadjusted,coef=comp,number=Inf,sort.by="none")
  for(nm in names(fits)){
    tt<-limma::topTable(fits[[nm]],coef=comp,number=Inf,sort.by="none")
    top_ref<-rownames(ref)[order(ref$P.Value)[1:1000]]; top_new<-rownames(tt)[order(tt$P.Value)[1:1000]]
    summary[[length(summary)+1]]<-data.frame(comparison=comp,model=nm,
      significant_FDR_0_001=sum(tt$adj.P.Val<.001),
      logFC_correlation=cor(ref$logFC,tt$logFC,use="complete.obs"),
      top1000_overlap=length(intersect(top_ref,top_new))/1000)
    pairwise[[length(pairwise)+1]]<-data.frame(comparison=comp,model=nm,
      unadjusted_logFC=ref$logFC,adjusted_logFC=tt$logFC)
  }
}
summary<-do.call(rbind,summary); pairwise<-do.call(rbind,pairwise)
write.table(summary,"results/tables/differential_confounder_sensitivity.tsv",sep="\t",row.names=FALSE,quote=FALSE)
p<-ggplot2::ggplot(subset(summary,model!="unadjusted"),ggplot2::aes(comparison,logFC_correlation,fill=model))+
  ggplot2::geom_col(position="dodge")+ggplot2::coord_cartesian(ylim=c(0,1))+
  ggplot2::labs(x=NULL,y="Correlation with unadjusted logFC",fill="Sensitivity model",
    title="Differential-methylation sensitivity to estimable covariates")+publication_theme()+
  ggplot2::theme(axis.text.x=ggplot2::element_text(angle=45,hjust=1))
save_publish_figure(p,"figures/main/Figure_differential_sensitivity",9,5.5)
writeLines(capture.output(sessionInfo()),"logs/session_05_differential_sensitivity.txt")
cat("Differential confounder sensitivity complete.\n")
