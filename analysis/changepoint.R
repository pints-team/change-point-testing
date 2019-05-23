# Ensure all required packages are installed
list.of.packages <- c(
  'changepoint',
  'ggplot2',
  'Hmisc',
  'lubridate',
  'RJSONIO',
  'RSQLite',
  'tidyverse'
)

new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages) > 0) install.packages(new.packages)

# Load required libaries
rm(list=ls())
library(changepoint)
library(DBI)
library(Hmisc)
library(lubridate)
library(RJSONIO)
library(tidyverse)

# command line arguments passed to plotting
args <- commandArgs(trailingOnly=TRUE)
current_directory <- as.character(args[1])
database <- as.character(args[2])
data_filename <- as.character(args[3])
output_directory <- as.character(args[4])
output_filename_base <- as.character(args[5])
plot_raw_logged <- as.numeric(args[6])
plot_raw_changepoints <- as.numeric(args[7])
plot_smooth <- as.numeric(args[8])
plot_pass_threshold <- as.numeric(args[9])
changepoints_run_length <- as.numeric(args[10])
changepoints_near_end_threshold <- as.numeric(args[11])
changepoints_num_tests_commits <- as.numeric(args[12])

setwd(current_directory)

# takes data in form in 'cleaned' folder and preps it for plotting
f_prep_data <- function(filebase, database){

  print(filebase)
  print(database)

  con <- dbConnect(RSQLite::SQLite(), dbname=database)
  res <- dbSendQuery(con, "SELECT * FROM test_results WHERE name like 'mcmc_banana_AdaptiveCovarianceMCMC_1'")
  data <- dbFetch(res)

  # data <- data %>%
  #   mutate(date2=as.POSIXct(date,format="%Y-%m-%d")) %>% 
  #   mutate(week=week(date2)) %>% 
  #   mutate(date_week=cut(date2, "week")) %>% 
  #   mutate(date_2_week = round_date(date2, "2 weeks"))

  # print(data$json)

  required_cols = c("date", "pfunk_commit", "pints_commit")
  sample_json_entry <- fromJSON(data$json[1])
  json_cols = names(sample_json_entry)

  json_data_list <- vector("list", length(json_cols) + length(required_cols))
  names(json_data_list) <- c(required_cols, json_cols)

  # Copy over the exiting data
  for (col in required_cols) {
    json_data_list[col] <- data[col]
  }

  print(data[1])

  # Create each column to be the correct length
  for (name in names(sample_json_entry)) {
    json_data_list[name] <- data[2]
  }

  # for (i in 1:length(data$json)) {

  #   for (name in json_cols) {
      
  #     print(name)
  #     print(json_data_list[name][3])

  #   }

  # }

  # print(json_data_list['date'])
  # print(typeof(json_data_list['date']))

  print('###################################')
  print(json_data_list['date'])
  print(json_data_list['date'][2])
  print('###################################')
  print(json_data_list$date)
  print(json_data_list$date[2])


  # print(json_data_list)

  # print(names(sample_json_entry))

  # data2 <- fromJSON(data$json[1], simplifyVector = TRUE,
  # simplifyDataFrame = TRUE, simplifyMatrix = TRUE,
  # flatten = TRUE)

  kld = list()
  ess = list()
  
  # for (json in data$json) {

  #   data2 <- fromJSON(json)

  #   print(length(data2$ess))
  #   print(length(data2[2]))

  #   # kld.app
  #   print(c(data2$ess))
  #   print(typeof(data2$ess))
  # }



  return(data)
}

# fetch data
test <- f_prep_data(data_filename, database)

# print(test)

# # fit PELT online changepoint model and add means to data frame ----------
# model  <- cpt.mean(test$score, method = "PELT", minseglen = changepoints_run_length)
# cpts <- as.vector(model@cpts)
# if(length(cpts) > 1){
#   cpts <- cpts[-length(cpts)]
#   means <- model@param.est$mean
#   vMeans <- vector(length = nrow(test))
#   ncpts <- length(cpts)
#   for(i in 1:(ncpts + 1)){
#     if(i < (ncpts + 1))
#       current_cpt <- cpts[i]
    
#     if(i == 1){
#       vMeans[1:current_cpt] <- rep(means[i], current_cpt)
#     }else if(i < (ncpts + 1)){
#       diff <- current_cpt - prev_cpt
#       vMeans[(prev_cpt + 1):(prev_cpt + diff)] <- rep(means[i], diff)
#     }else{
#       vMeans[(prev_cpt + 1):length(vMeans)] <- rep(means[i], length(vMeans) - prev_cpt)
#     }
#     prev_cpt <- current_cpt
#   }
# }else{
#   vMeans <- rep(model@param.est$mean, nrow(test))
# }

# # check if a changepoint has occurred between [changepoints_near_end_threshold tests ago, most recent commit]
# print(changepoints_near_end_threshold)
# cpt_alarm_triggered <- if_else(max(cpts) > (nrow(test) - changepoints_near_end_threshold), 1, 0)
# if(cpt_alarm_triggered == 1){
#   max_cpt <- max(cpts)
#   cpt_date <- test$date[max_cpt]
#   cpt_week <- test$week[max_cpt]
#   cpt_main_commit <- as.character(test$commit[max_cpt])
#   # get last changepoints_num_tests_commits test commits
#   a_min <- if_else((max_cpt - changepoints_num_tests_commits) > 1,
#                    max_cpt - changepoints_num_tests_commits, 1)
#   a_max <- if_else((max_cpt + changepoints_num_tests_commits) < nrow(test),
#                    max_cpt + changepoints_num_tests_commits, as.numeric(nrow(test)))
#   cpt_commits <- as.character(unique(test$commit[a_min:a_max]))
# }else{
#   cpt_date <- -99
#   cpt_week <- -99
#   cpt_main_commit <- -99
#   cpt_commits <- -99
# }
# commit_list <- list(cpt_alarm_triggered=cpt_alarm_triggered,
#                     cpt_date=cpt_date,
#                     cpt_week=cpt_week,
#                     cpt_main_commit=cpt_main_commit,
#                     cpt_commits=cpt_commits)

# test$cpt_means <- vMeans

# # plot by grouping by every two weeks ----------
# # raw data plot
# g <-
#     test %>% 
#     ggplot(aes(x=date_2_week, y=score)) +
#     geom_jitter() +
#     theme_classic() +
#     xlab("Date, two weeks grouped") +
#     ylab("Score") +
#     theme(axis.title = element_text(size=14, colour="black"),
#           axis.text = element_text(size=14, colour="black")) +
#     stat_summary(fun.data=mean_sdl, mult=1, 
#                  geom="pointrange", color="red")
  
# # add log y scale
# if(plot_raw_logged){
#   g <- g +
#     scale_y_log10()
# }

# # add changepoints
# if(plot_raw_changepoints){
#   g <- g +
#     geom_line(aes(y=cpt_means), linetype=2, colour="blue", size=1)
# }

# # plot percentage of tests passing user specified threshold
# test <- test %>% 
#   mutate(pass=if_else(score < plot_pass_threshold, 1, 0)) %>% 
#   group_by(date_2_week) %>% 
#   summarise(pass=sum(pass),
#             size=n()) %>% 
#   mutate(score=pass / size,
#          upper=qbeta(0.95, 1 + pass, 1 + size - pass),
#          lower=qbeta(0.05, 1 + pass, 1 + size - pass),
#          middle=qbeta(0.5, 1 + pass, 1 + size - pass))

# g1 <- 
#   test %>% 
#   ggplot(aes(x=date_2_week, y=score)) +
#   theme_classic() +
#   xlab("Date, two weeks grouped") +
#   ylab("Mean passing threshold") +
#   theme(axis.title = element_text(size=14, colour="black"),
#         axis.text = element_text(size=14, colour="black")) +
#   geom_point() +
#   geom_point(aes(y=middle), colour="red") + 
#   geom_errorbar(aes(ymin=lower, ymax=upper), size=0.1, colour="red") +
#   scale_y_continuous(labels = scales::percent, limits = c(0, 1))

# # add smoothed line
# if(plot_smooth){
#   g <- g + 
#     geom_smooth(linetype=3, colour="orange")
#   g1 <- g1 + 
#     geom_smooth(linetype=3, colour="orange")
# }

# # Output changepoint test results as json to directory -------
# exportJson <- toJSON(commit_list)
# write(exportJson, paste0(output_directory, "/", output_filename_base, ".json"))

# # output plot
# ggsave(paste0(output_directory, "/", output_filename_base, "_raw.pdf"), g, width = 10, height = 6)
# ggsave(paste0(output_directory, "/", output_filename_base, "_threshold.pdf"), g1, width = 10, height = 6)
