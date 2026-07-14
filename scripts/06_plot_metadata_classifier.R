source("R/plotting.R")
x<-read.delim("results/tables/metadata_only_classifier.tsv")
x$feature_set<-factor(x$feature_set,levels=c("all_available_metadata","sentrix_only","source_only","age_sex","biopsy_site_only"))
p<-ggplot2::ggplot(x,ggplot2::aes(feature_set,balanced_accuracy,fill=feature_set))+
  ggplot2::geom_boxplot(show.legend=FALSE)+ggplot2::geom_hline(yintercept=1/6,linetype=2)+
  ggplot2::coord_flip()+ggplot2::labs(x=NULL,y="Repeated-CV balanced accuracy",
    title="Disease-group prediction from metadata alone")+publication_theme()
save_publish_figure(p,"figures/main/Figure_metadata_only_classifier",8,5)
