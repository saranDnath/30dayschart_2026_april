library(readxl)
library(dplyr)
library(ggplot2)
library(ggrepel)

if (interactive() && requireNamespace("rstudioapi", quietly = TRUE)) {
  setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
}

url <- "https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx"
destfile <- "dataset_world_health_stat_2022.xlsx"
if (!file.exists(destfile)) {
  download.file(url, destfile, mode = "wb")
}

highlight_countries <- c("Bangladesh", "India", "Pakistan", "Sri Lanka", "Nepal", "Bhutan", "Maldives", "Afghanistan", "China", "Japan", "United Kingdom", "United States", "Mexico", "Brazil", "South Africa", "Nigeria", "Australia")

df <- suppressWarnings(read_excel(destfile, sheet = "Annex 2-3", col_names = FALSE))
data <- df[6:nrow(df), c(1, 11, 12)]
colnames(data) <- c("Country", "Doctors", "Nurses")
data <- data %>% mutate(across(c(Doctors, Nurses), as.numeric)) %>% filter(!is.na(Doctors) & !is.na(Nurses))

data <- data %>% mutate(
  ShortName = sapply(Country, function(c) {
    m <- highlight_countries[sapply(highlight_countries, function(n) grepl(n, c, ignore.case=TRUE))]
    if(length(m)>0) m[1] else c
  }),
  Highlight = ShortName %in% highlight_countries,
  Label = ifelse(Highlight, sprintf("%s (%.1f, %.1f)", ShortName, Doctors, Nurses), "")
)

plot <- ggplot() +
  geom_point(data = data %>% filter(!Highlight), aes(x=Doctors, y=Nurses), color="#C8BFB5", size=3, alpha=0.55, stroke=0.4) +
  geom_point(data = data %>% filter(Highlight & ShortName != "Bangladesh"), aes(x=Doctors, y=Nurses), color="#2C6FA6", size=5, alpha=0.92, stroke=1.5) +
  
  geom_point(data = data %>% filter(ShortName == "Bangladesh"), aes(x=Doctors, y=Nurses), color="#D62828", size=14, alpha=0.20) +
  geom_point(data = data %>% filter(ShortName == "Bangladesh"), aes(x=Doctors, y=Nurses), fill="#D62828", color="white", shape=21, size=8, stroke=2.0) +
  
  geom_text_repel(data = data %>% filter(Highlight), 
                  aes(x=Doctors, y=Nurses, label=Label, color=ifelse(ShortName == "Bangladesh", "#006A4E", "#1A3D5C")), 
                  fontface="bold", size=3.5, bg.color="white", bg.r=0.15, max.overlaps=Inf) +
  scale_color_identity() +
  scale_x_log10() + scale_y_log10() +
  theme_minimal() +
  labs(title="Health Workforce: Doctors vs Nurses Density", subtitle="WHO World Health Statistics 2022  ·  Doctors vs Nurses & Midwives per 10,000", x="Doctors (per 10k log)", y="Nurses & Midwives (per 10k log)") +
  theme(plot.background = element_rect(fill="#F7F3EE", color=NA), panel.background = element_rect(fill="#F7F3EE", color=NA),
        panel.grid.major = element_line(color="#E0D9D0", linetype="dashed", linewidth=0.8), panel.grid.minor = element_blank(),
        plot.title = element_text(color="#1A1A2E", face="bold", size=18, margin=margin(b=5)), plot.subtitle = element_text(color="#1A1A2E", size=11, margin=margin(b=15)),
        axis.title = element_text(color="#4A4A5A", face="bold", size=13), axis.text = element_text(color="#4A4A5A", size=11), legend.position = "none")

ggsave("day_4_r.png", plot, width = 12, height = 8, dpi = 300, bg="#F7F3EE")
