library(readxl)
library(dplyr)
library(ggplot2)
library(ggrepel)

if (interactive() && requireNamespace("rstudioapi", quietly = TRUE)) {
  setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
}

destfile <- "dataset_world_health_stat_2022.xlsx"
if (!file.exists(destfile)) {
  download.file("https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx", destfile, mode = "wb")
}

highlight_countries <- c("Bangladesh", "India", "Pakistan", "Sri Lanka", "Nepal", "Bhutan", "Maldives", "Afghanistan", "China", "United Kingdom", "United States", "Mexico", "Brazil", "South Africa", "Nigeria", "Australia")

df <- suppressWarnings(read_excel(destfile, sheet = "Annex 2-1", col_names = FALSE))
data <- df[6:nrow(df), c(1, 7, 10)]
colnames(data) <- c("Country", "Life_Exp", "Healthy_Life_Exp")
data <- data %>% mutate(across(c(Life_Exp, Healthy_Life_Exp), as.numeric)) %>% filter(!is.na(Life_Exp) & !is.na(Healthy_Life_Exp))

data <- data %>% mutate(
  ShortName = sapply(Country, function(c) {
    m <- highlight_countries[sapply(highlight_countries, function(n) grepl(n, c, ignore.case=TRUE))]
    if(length(m)>0) m[1] else c
  }),
  Highlight = ShortName %in% highlight_countries,
  Label = ifelse(Highlight, sprintf("%s (%.1f, %.1f)", ShortName, Life_Exp, Healthy_Life_Exp), "")
)

visible_data <- data %>% filter(Life_Exp >= 50 & Healthy_Life_Exp >= 45)
highest_val <- max(visible_data$Life_Exp, na.rm = TRUE)
lowest_val <- min(visible_data$Life_Exp, na.rm = TRUE)

extremes <- visible_data %>% filter(Life_Exp %in% c(highest_val, lowest_val)) %>% pull(ShortName)

plot <- ggplot() +
  geom_point(data = data %>% filter(!Highlight), aes(x=Life_Exp, y=Healthy_Life_Exp), color="#C8BFB5", size=3, alpha=0.55, stroke=0.4) +
  geom_point(data = data %>% filter(Highlight & ShortName != "Bangladesh"), aes(x=Life_Exp, y=Healthy_Life_Exp), color="#2C6FA6", size=5, alpha=0.92, stroke=1.5) +
  
  geom_point(data = data %>% filter(ShortName == "Bangladesh"), aes(x=Life_Exp, y=Healthy_Life_Exp), color="#D62828", size=14, alpha=0.20) +
  geom_point(data = data %>% filter(ShortName == "Bangladesh"), aes(x=Life_Exp, y=Healthy_Life_Exp), fill="#D62828", color="white", shape=21, size=8, stroke=2.0) +
  
  geom_point(data = data %>% filter(ShortName %in% extremes), aes(x=Life_Exp, y=Healthy_Life_Exp), color="#E8A020", size=6, alpha=1.0, stroke=1.5) +

  geom_text_repel(data = data %>% filter(Highlight & !(ShortName %in% extremes)), 
                  aes(x=Life_Exp, y=Healthy_Life_Exp, label=Label, color=ifelse(ShortName == "Bangladesh", "#006A4E", "#1A3D5C")), 
                  fontface="bold", size=3.5, segment.color="#8899AA", bg.color="white", bg.r=0.15, max.overlaps=Inf) +
  
  geom_text_repel(data = data %>% filter(ShortName %in% extremes), 
                  aes(x=Life_Exp, y=Healthy_Life_Exp, label=paste0(Label, "\nHighest/Lowest Life Expectancy")), 
                  color="#8B5E00", fontface="bold", size=3.5, segment.color="#8899AA", bg.color="white", bg.r=0.15, max.overlaps=Inf) +

  scale_color_identity() +
  geom_abline(intercept = 0, slope = 1, color = "#4A4A5A", linetype = "dashed", alpha = 0.5) + coord_cartesian(xlim=c(50, 90), ylim=c(45, 80)) +
  theme_minimal() +
  labs(title="Quality of Life Gap: Life Expectancy vs Healthy Life", subtitle="WHO World Health Statistics 2022  ·  Life expectancy vs Healthy life expectancy at birth", x="Life Expectancy (Years)", y="Healthy Life Expectancy (Years)") +
  theme(plot.background = element_rect(fill="#F7F3EE", color=NA), panel.background = element_rect(fill="#F7F3EE", color=NA),
        panel.grid.major = element_line(color="#E0D9D0", linetype="dashed", linewidth=0.8), panel.grid.minor = element_blank(),
        plot.title = element_text(color="#1A1A2E", face="bold", size=18, margin=margin(b=5)), plot.subtitle = element_text(color="#1A1A2E", size=11, margin=margin(b=15)),
        axis.title = element_text(color="#4A4A5A", face="bold", size=13), axis.text = element_text(color="#4A4A5A", size=11), legend.position = "none")

ggsave("day_2_r.png", plot, width = 12, height = 8, dpi = 300, bg="#F7F3EE")
