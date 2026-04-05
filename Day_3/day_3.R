library(readxl)
library(dplyr)
library(ggplot2)

if (interactive() && requireNamespace("rstudioapi", quietly = TRUE)) {
  setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
}
destfile <- "dataset_world_health_stat_2022.xlsx"
if (!file.exists(destfile)) {
  download.file("https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx", destfile, mode = "wb")
}

highlight_countries <- c("Bangladesh", "India", "Pakistan", "Sri Lanka", "Nepal", "Bhutan", "Maldives", "Afghanistan", "China", "United Kingdom", "United States", "Mexico", "Brazil", "South Africa", "Nigeria", "Australia")

df <- suppressWarnings(read_excel(destfile, sheet = "Annex 2-4", col_names = FALSE))
data <- df[6:nrow(df), c(1, 2, 6)]
colnames(data) <- c("Country", "Stunting", "Overweight")
data <- data %>%
  mutate(across(c(Stunting, Overweight), as.numeric)) %>%
  filter(!is.na(Stunting)) %>%
  mutate(
    ShortName = sapply(Country, function(c) {
      m <- highlight_countries[sapply(highlight_countries, function(n) grepl(n, c, ignore.case = TRUE))]
      if (length(m) > 0) m[1] else c
    }),
    Highlight = ShortName %in% highlight_countries
  ) %>%
  filter(Highlight) %>%
  arrange(Stunting) %>%
  mutate(ShortName = factor(ShortName, levels = ShortName))

plot <- ggplot(data) +
  geom_bar(aes(x = ShortName, y = Stunting, fill = "Stunting"), stat = "identity", color = "white") +
  geom_bar(aes(x = ShortName, y = -Overweight, fill = "Overweight"), stat = "identity", color = "white") +
  geom_text(aes(x = ShortName, y = Stunting, label = sprintf("%.1f%%", Stunting)), size = 3, hjust = -0.2, color = "#1A3D5C") +
  geom_text(aes(x = ShortName, y = -Overweight, label = sprintf("%.1f%%", Overweight)), size = 3, hjust = 1.2, color = "#1A3D5C") +
  scale_fill_manual(values = c("Stunting" = "#3D5A80", "Overweight" = "#E07A5F")) +
  coord_flip(ylim = c(-max(data$Overweight, na.rm = T) - 15, max(data$Stunting, na.rm = T) + 10)) +
  theme_minimal() +
  labs(title = "Childhood Malnutrition: Overweight vs Stunting", subtitle = "WHO World Health Statistics 2022  ·  % Under-5s", x = "", y = "", fill = "") +
  theme(
    plot.background = element_rect(fill = "#F7F3EE", color = NA), panel.background = element_rect(fill = "#F7F3EE", color = NA),
    panel.grid.major.x = element_line(color = "#E0D9D0", linetype = "dashed", linewidth = 0.8), panel.grid.minor = element_blank(), panel.grid.major.y = element_blank(),
    plot.title = element_text(color = "#1A1A2E", face = "bold", size = 18, margin = margin(b = 5)), plot.subtitle = element_text(color = "#1A1A2E", size = 11, margin = margin(b = 15)),
    axis.text.x = element_blank(),
    axis.text.y = element_text(color = sapply(levels(data$ShortName), function(s) if (s == "Bangladesh") "#006A4E" else "#1A3D5C"), face = sapply(levels(data$ShortName), function(s) if (s == "Bangladesh") "bold" else "plain")),
    legend.position = "bottom"
  )

ggsave("day_3_r.png", plot, width = 10, height = 8, dpi = 300, bg = "#F7F3EE")
