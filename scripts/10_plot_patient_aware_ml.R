source("R/plotting.R")
x<-read.delim("results/tables/patient_aware_ml_metrics.tsv")
d<-reshape(x[,c("model","accuracy","balanced_accuracy","weighted_f1")],direction="long",
  varying=c("accuracy","balanced_accuracy","weighted_f1"),v.names="value",timevar="metric",
  times=c("Accuracy","Balanced accuracy","Weighted F1"))
p<-ggplot2::ggplot(d,ggplot2::aes(model,value,fill=metric))+ggplot2::geom_col(position="dodge")+
  ggplot2::coord_cartesian(ylim=c(0,1))+ggplot2::labs(x=NULL,y="Held-out performance",fill=NULL,
    title="Patient-aware held-out disease-group classification")+publication_theme()+
  ggplot2::theme(axis.text.x=ggplot2::element_text(angle=30,hjust=1))
save_publish_figure(p,"figures/main/Figure_patient_aware_ML",8,5)
