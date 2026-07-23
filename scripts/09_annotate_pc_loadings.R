source("R/config.R")
cfg<-read_project_config(); ensure_output_dirs(cfg$root)
library(IlluminaHumanMethylationEPICanno.ilm10b4.hg19)
loadings<-read.delim("results/tables/pca_scaled_top_loadings.tsv")
ann<-minfi::getAnnotation(IlluminaHumanMethylationEPICanno.ilm10b4.hg19)
keep<-c("Name","chr","pos","strand","UCSC_RefGene_Name","UCSC_RefGene_Group","Relation_to_Island","Regulatory_Feature_Group","DNase_Hypersensitivity_NAME")
a<-as.data.frame(ann[,intersect(keep,colnames(ann))]); a$Name<-rownames(a)
out<-merge(loadings,a,by.x="CpG",by.y="Name",all.x=TRUE,sort=FALSE)
write.table(out,"results/tables/pca_scaled_top_loadings_annotated.tsv",sep="\t",row.names=FALSE,quote=FALSE,na="NA")
summarize_field<-function(field){
  vals<-strsplit(as.character(out[[field]]),";")
  data.frame(table(PC=rep(out$PC,lengths(vals)),direction=rep(out$direction,lengths(vals)),
    category=unlist(vals),useNA="ifany"),check.names=FALSE)
}
for(field in intersect(c("chr","UCSC_RefGene_Group","Relation_to_Island","Regulatory_Feature_Group"),names(out))){
  write.table(summarize_field(field),file.path("results/tables",paste0("pca_loading_",field,"_summary.tsv")),
    sep="\t",row.names=FALSE,quote=FALSE)
}
cat("Annotated",nrow(out),"PC-loading CpGs. Annotation supports genomic/functional description but cannot by itself identify batch causality.\n")
