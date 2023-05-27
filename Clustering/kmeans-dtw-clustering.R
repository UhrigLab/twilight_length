library(ggplot2)
library(cowplot)
library(here)
library(tidyverse)
library(ppclust)
library(factoextra)
library(fclust)
library(cluster)
library(dtwclust)
library(readxl)

theme_set(theme_cowplot())

data<-read_excel("combined_log_noMissing_ANOVA_Z-score.xlsx")

head(data)

data<-as.data.frame(data)
str(data)

data[6]

data2<-data[-1]
str(data2)


interactive_clustering(data2)

write.csv(`cluster`@cluster,"dtw2_combined_clusters.csv")
write.csv(`cluster`@cldist,"dtw2_combined_cluster_dist.csv")
write.csv(`cluster`@distmat,"dtw2_combined_cluster_distmat.csv")
write.csv(`cluster`@centroids,"dtw2_combined_centroids.csv")

write.csv(data,'cluster_input.csv')

plot<-plot(`cluster`,type="sc")
plot2<-plot(`cluster`,type="c")

save_plot("dtw2_combined_clustering.pdf",plot,base_asp = 2,base_height = 8)
save_plot("dtw2_combined_clustering_centroids.pdf",plot2,base_asp = 2,base_height = 8)


