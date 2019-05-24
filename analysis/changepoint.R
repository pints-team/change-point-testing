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

  data <- data %>%
    mutate(date=as.POSIXct(date,format="%Y-%m-%d")) %>% 
    mutate(week=week(date)) %>% 
    mutate(date_week=cut(date, "week")) %>% 
    mutate(date_2_week = round_date(date, "2 weeks"))

  # print(fromJSON(data$json[1]))

  required_cols = c("date", "week", "date_2_week", "pfunk_commit", "pints_commit")
  sample_json_entry <- fromJSON(data$json[1])
  json_cols = names(sample_json_entry)

  json_data_list <- list()
  

  # Copy over the exiting data
  k <- 1
  for (col in required_cols) {
    json_data_list[[col]] <- data[col]
    k <- k + 1
  }

  # # Create each column to be the correct length
  # for (name in names(sample_json_entry)) {
  #   json_data_list[name] <-  vector("list", length = 5)
  # }

  # print(json_data_list)

  one_col = c("kld")

  
for (name in json_cols){
  
  ncols <- length(sample_json_entry[[name]])
  if(ncols==1)
    mTemp <- vector(length=length(data$json))
  else
    mTemp <- matrix(nrow=length(data$json), ncol=ncols)

  for (i in 1:length(data$json)) {
    new_data <- fromJSON(data$json[i])
    new_data1 <- new_data[[name]]
    for(j in 1:ncols){
      if(ncols==1)
        mTemp[i] <- new_data1[j]
      else
        mTemp[i, j] <- new_data1[j]
    }
  }
  json_data_list[[k]] <- mTemp
  k <- k + 1
}
names(json_data_list) <- c(required_cols, json_cols)

# print(json_data_list)


  return(json_data_list)
}

# fetch data
test <- f_prep_data(data_filename, database)


# fit PELT online changepoint model and add means to data frame ----------
lnames <- names(test)
lnames <- gsub('kld', 'score', lnames)
names(test) <- lnames
model  <- cpt.mean(test$score, method = "PELT", minseglen = 1)
cpts <- as.vector(model@cpts)
cpts <- cpts[-length(cpts)]
if(length(cpts) > 1){
  means <- model@param.est$mean
  vMeans <- vector(length = nrow(test))
  ncpts <- length(cpts)
  for(i in 1:(ncpts + 1)){
    if(i < (ncpts + 1))
      current_cpt <- cpts[i]
    
    if(i == 1){
      vMeans[1:current_cpt] <- rep(means[i], current_cpt)
    }else if(i < (ncpts + 1)){
      diff <- current_cpt - prev_cpt
      vMeans[(prev_cpt + 1):(prev_cpt + diff)] <- rep(means[i], diff)
    }else{
      vMeans[(prev_cpt + 1):length(vMeans)] <- rep(means[i], length(vMeans) - prev_cpt)
    }
    prev_cpt <- current_cpt
  }
}else{
  vMeans <- rep(model@param.est$mean, length(test$score))
}


num_cpts <- length(cpts)
cpt_dates <- vector(mode="list", length = num_cpts)
cpt_weeks <- vector(mode="list", length = num_cpts)
cpt_main_commits <- vector(mode="list", length = num_cpts)
cpt_commits <- vector(mode="list", length = num_cpts)
if(num_cpts > 0){
  for (i in 1:num_cpts){
    a_cpt <- cpts[i]
    cpt_dates[[i]] <- test$date[[1]][a_cpt]
    cpt_weeks[[i]] <- test$week[[1]][a_cpt]
    print("hello fergus")
    cpt_main_commits[[i]] <- as.character(test$pints_commit[[1]][cpts[[i]]])
    # get last changepoints_num_tests_commits test commits
    a_min <- if_else((a_cpt - changepoints_num_tests_commits) > 1,
                    a_cpt - changepoints_num_tests_commits, 1)
    a_max <- if_else((a_cpt + changepoints_num_tests_commits) < nrow(test),
                    a_cpt + changepoints_num_tests_commits, as.numeric(nrow(test)))
    cpt_commits[[i]] <- as.character(unique(test$commit[a_min:a_max]))
  }
}else{
  cpt_dates[[1]] <- -99
  cpt_weeks[[1]] <- -99
  cpt_main_commits[[1]] <- -99
  cpt_commits[[1]] <- -99
}
output_list <- list()
if(num_cpts > 1){
  for(i in 1:num_cpts){
    output_list[[i]] <- list(changepoint=cpts[i],
                            date=cpt_dates[[i]],
                            week=cpt_weeks[[i]],
                            commit_main=cpt_main_commits[[i]],
                            commits_nearby=cpt_commits[[i]])
  }
}else{
  output_list[[1]] <- list(changepoint=cpts[1],
                            date=cpt_dates[[1]],
                            week=cpt_weeks[[1]],
                            commit_main=cpt_main_commits[[1]],
                            commits_nearby=cpt_commits[[1]])
}

test$cpt_means <- vMeans

# plot by grouping by every two weeks ----------
# raw data plot
test <- tibble(date_2_week=as.Date(test$date_2_week[[1]]),
               score=test$score,
               cpt_means=test$cpt_means)
print(as.Date(test$date_2_week))
g <-
    test %>% 
    ggplot(aes(x=date_2_week, y=score)) +
    geom_jitter() +
    theme_classic() +
    xlab("Date, two weeks grouped") +
    ylab("Score") +
    theme(axis.title = element_text(size=14, colour="black"),
          axis.text = element_text(size=14, colour="black")) +
    stat_summary(fun.data=mean_sdl, mult=1, 
                 geom="pointrange", color="red")
  
# add log y scale
if(plot_raw_logged){
  g <- g +
    scale_y_log10()
}

# add changepoints
if(plot_raw_changepoints){
  g <- g +
    geom_line(aes(y=cpt_means), linetype=2, colour="blue", size=1)
}

# plot percentage of tests passing user specified threshold
test <- test %>% 
  mutate(pass=if_else(score < plot_pass_threshold, 1, 0)) %>% 
  group_by(date_2_week) %>% 
  summarise(pass=sum(pass),
            size=n()) %>% 
  mutate(score=pass / size,
         upper=qbeta(0.95, 1 + pass, 1 + size - pass),
         lower=qbeta(0.05, 1 + pass, 1 + size - pass),
         middle=qbeta(0.5, 1 + pass, 1 + size - pass))

g1 <- 
  test %>% 
  ggplot(aes(x=date_2_week, y=score)) +
  theme_classic() +
  xlab("Date, two weeks grouped") +
  ylab("Mean passing threshold") +
  theme(axis.title = element_text(size=14, colour="black"),
        axis.text = element_text(size=14, colour="black")) +
  geom_point() +
  geom_point(aes(y=middle), colour="red") + 
  geom_errorbar(aes(ymin=lower, ymax=upper), size=0.1, colour="red") +
  scale_y_continuous(labels = scales::percent, limits = c(0, 1))

# add smoothed line
if(plot_smooth){
  g <- g + 
    geom_smooth(linetype=3, colour="orange")
  g1 <- g1 + 
    geom_smooth(linetype=3, colour="orange")
}

# Output changepoint test results as json to directory -------
exportJson <- toJSON(output_list)
write(exportJson, paste0(output_directory, "/", output_filename_base, ".json"))

# output plot
ggsave(paste0(output_directory, "/", output_filename_base, "_raw.pdf"), g, width = 10, height = 6)
ggsave(paste0(output_directory, "/", output_filename_base, "_threshold.pdf"), g1, width = 10, height = 6)
