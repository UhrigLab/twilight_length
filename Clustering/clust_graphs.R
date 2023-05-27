#!/usr/bin/env Rscript
library(ggplot2)
library(reshape2)
library(cowplot)
library(ggthemes)
library(patchwork)
library(gghighlight)
library(ggExtra)
library(egg)
library(Hmisc)
library(tidyverse)
library(readxl)
library(lubridate)
library(openxlsx)

theme_set(theme_cowplot())

data1<-read_excel("combined_log_noMissing_ANOVA_Z-score_clustering.xlsx")

head(data1)

data2<-data1[,c("uAGI","cluster","1","2","3","4","5")]

head(data2)
tail(data2)

data2long<-melt(data=data2,
               id.vars=c("uAGI","cluster"),
               variable.name = "time",
               value.name = "abundance"
)

head(data2long)
tail(data2long)

str(data2long)
data2long<-transform(data2long,time=as.numeric(levels(time))[time])

str(data2long)
head(data2long)
tail(data2long)



prot_clusters<-unique(data2long$cluster)


str(prot_clusters)


l<-length(prot_clusters)
p=list()

myplots <- vector('list',l)


for (i in seq_along(prot_clusters)){
  message(i)
  
  d<-data.frame(AGI=factor(),cluster=integer(),time=numeric(),abundance=numeric())
  d<-subset(data2long,data2long$cluster==i)
  
  avg<-character()
  avg<-paste0("avg",i)
  print(avg)
  
  myplots[[i]] <-local({
    i<-i
    message(i)
    pR<-ggplot(data=d,aes(x=time,y=abundance, group=uAGI))+geom_line(color='#56B4E9', size= 1)+
      ylim(-3,3)+theme(axis.title.x = element_blank(),axis.title.y = element_blank(),axis.text.x=element_blank(),
                     axis.ticks.x=element_blank())+
      gghighlight(uAGI==as.character(avg),use_direct_label = FALSE, use_group_by = FALSE,
                  unhighlighted_params = list(size = 1, colour = alpha("grey", 0.3)))+
      geom_point(data=subset(d,time %in% "5"),color=alpha("grey",0.3))+
      geom_vline(xintercept=c(1,2,3,4,5),linetype=2, colour="black")
  })
}


plot<-plot_grid(plotlist = c(myplots), nrow = 2)
plot

save_plot('clust.pdf', plot,base_aspect_ratio = 2, base_height =8)

