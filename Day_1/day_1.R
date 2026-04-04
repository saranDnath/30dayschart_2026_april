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

highlight_countries <- c(
  "Bangladesh", "India", "Pakistan", "Sri Lanka", "Nepal", "Bhutan", "Maldives", "Afghanistan", 
  "China", "Japan", "United Kingdom", "United States", "Mexico", "Brazil", "South Africa", "Nigeria", "Australia"
)

df <- suppressWarnings(read_excel(destfile, sheet = "Annex 2-2", col_names = FALSE))
data <- df[6:nrow(df), c(1, 10, 11)]
colnames(data) <- c("Country", "UHC_Index", "OOP_10_percent")
data <- data %>% mutate(across(c(UHC_Index, OOP_10_percent), as.numeric)) %>% filter(!is.na(UHC_Index) & !is.na(OOP_10_percent))

data <- data %>% mutate(
  ShortName = sapply(Country, function(c) {
    m <- highlight_countries[sapply(highlight_countries, function(n) grepl(n, c, ignore.case=TRUE))]
    if(length(m)>0) m[1] else c
  }),
  Highlight = ShortName %in% highlight_countries,
  Label = ifelse(Highlight, sprintf("%s (%.1f, %.1f)", ShortName, UHC_Index, OOP_10_percent), "")
)

plot <- ggplot() +
  geom_point(data = data %>% filter(!Highlight), aes(x=UHC_Index, y=OOP_10_percent), color="#C8BFB5", size=3, alpha=0.55, stroke=0.4) +
  geom_point(data = data %>% filter(Highlight & ShortName != "Bangladesh"), aes(x=UHC_Index, y=OOP_10_percent), color="#2C6FA6", size=5, alpha=0.92, stroke=1.5) +
  
  geom_point(data = data %>% filter(ShortName == "Bangladesh"), aes(x=UHC_Index, y=OOP_10_percent), color="#D62828", size=14, alpha=0.20) +
  geom_point(data = data %>% filter(ShortName == "Bangladesh"), aes(x=UHC_Index, y=OOP_10_percent), fill="#D62828", color="white", shape=21, size=8, stroke=2.0) +
  
  geom_text_repel(data = data %>% filter(Highlight), 
                  aes(x=UHC_Index, y=OOP_10_percent, label=Label, 
                      color=ifelse(ShortName == "Bangladesh", "#006A4E", "#1A3D5C"),
                      fontface=ifelse(ShortName == "Bangladesh", "bold", "bold")), 
                  size=ifelse(data %>% filter(Highlight) %>% pull(ShortName) == "Bangladesh", 4.0, 3.5),
                  bg.color="white", bg.r=0.15, max.overlaps=Inf) +
  scale_color_identity() +
  theme_minimal() +
  coord_cartesian(xlim = c(20, 100), ylim = c(-5, 60)) +
  labs(
    title="The cost of care: OOP Expenditure vs UHC",
    subtitle="WHO World Health Statistics 2022  ·  Catastrophic out-of-pocket spending vs. UHC coverage",
    x="Universal Health Coverage (UHC) Index", y="% Population Spending on Health >10% of HH budget"
  ) +
  theme(
    plot.background = element_rect(fill="#F7F3EE", color=NA),
    panel.background = element_rect(fill="#F7F3EE", color=NA),
    panel.grid.major = element_line(color="#E0D9D0", linetype="dashed", linewidth=0.8),
    panel.grid.minor = element_blank(),
    plot.title = element_text(color="#1A1A2E", face="bold", size=18, margin=margin(b=5)),
    plot.subtitle = element_text(color="#1A1A2E", size=11, margin=margin(b=15)),
    axis.title = element_text(color="#4A4A5A", face="bold", size=13),
    axis.text = element_text(color="#4A4A5A", size=11),
    legend.position = "none"
  )

ggsave("cost_of_care_r.png", plot, width = 12, height = 8, dpi = 300, bg="#F7F3EE")
