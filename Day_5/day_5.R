library(tidyverse)
library(readxl)
library(sf)
library(rnaturalearth)

if (interactive() && requireNamespace("rstudioapi", quietly = TRUE)) {
  setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
}

# ── Configuration ────────────────────────────────────────────────────────────
INDICATOR_SHEET <- "Annex 2-1"
INDICATOR_COL <- 16
INDICATOR_LABEL <- "Tuberculosis incidence (per 100 000 population)"
INDICATOR_SHORT <- "Tuberculosis"
OUTPUT_FILE <- "day_5_tuberculosis_map_r.png"

PALETTE <- list(
  background = "#F7F3EE",
  title      = "#1A1A2E",
  axis       = "#4A4A5A",
  missing    = "#D6D0C8",
  bd_edge    = "#D62828"
)

# ── 1. Load WHO Data ──────────────────────────────────────────────────────────
destfile <- "dataset_world_health_stat_2022.xlsx"
df <- suppressWarnings(read_excel(destfile, sheet = INDICATOR_SHEET, col_names = FALSE))
data <- df[6:nrow(df), c(1, INDICATOR_COL + 1)]
colnames(data) <- c("Country", "Value")
data <- data %>%
  mutate(Value = as.numeric(gsub("[<>]", "", Value))) %>%
  filter(!is.na(Value)) %>%
  mutate(Country = str_trim(Country))

# ── 2. Load World Shapefile ───────────────────────────────────────────────────
# Using 110m low-res for global stability
world <- ne_countries(scale = 110, returnclass = "sf")

# ── 3. Name Mapping ───────────────────────────────────────────────────────────
name_map <- c(
  "Bolivia" = "Bolivia (Plurinational State of)",
  "Bosnia and Herz." = "Bosnia and Herzegovina",
  "Brunei" = "Brunei Darussalam",
  "Central African Rep." = "Central African Republic",
  "Democratic Republic of the Congo" = "Democratic Republic of the Congo",
  "Dominican Rep." = "Dominican Republic",
  "Eq. Guinea" = "Equatorial Guinea",
  "Iran" = "Iran (Islamic Republic of)",
  "Laos" = "Lao People's Democratic Republic",
  "Moldova" = "Republic of Moldova",
  "North Korea" = "Democratic People's Republic of Korea",
  "Palestine" = "Occupied Palestinian Territory",
  "Russia" = "Russian Federation",
  "S. Sudan" = "South Sudan",
  "South Korea" = "Republic of Korea",
  "Syria" = "Syrian Arab Republic",
  "Tanzania" = "United Republic of Tanzania",
  "Venezuela" = "Venezuela (Bolivarian Republic of)",
  "Vietnam" = "Viet Nam",
  "eSwatini" = "Eswatini",
  "Côte d'Ivoire" = "Côte d'Ivoire",
  "Czechia" = "Czech Republic",
  "Greenland" = "Denmark",
  "Puerto Rico" = "United States of America",
  "Falkland Is." = "United Kingdom of Great Britain and Northern Ireland",
  "New Caledonia" = "France",
  "Fr. S. Antarctic Lands" = "France",
  "W. Sahara" = "Morocco",
  "Somaliland" = "Somalia",
  "Kosovo" = "Serbia",
  "N. Cyprus" = "Cyprus",
  "Taiwan" = "China" # sorry Taiwan
)

# Handle cases where name or name_long might be used
world <- world %>%
  mutate(
    name_lookup = case_when(
      name %in% names(name_map) ~ name_map[name],
      TRUE ~ name
    )
  )

# ── 4. Merge ──────────────────────────────────────────────────────────────────
merged <- world %>%
  left_join(data, by = c("name_lookup" = "Country"))

# ── 5. Plot ───────────────────────────────────────────────────────────────────
plot <- ggplot(merged) +
  geom_sf(aes(fill = Value), color = "white", size = 0.1) +
  # Highlight Bangladesh
  geom_sf(data = filter(merged, name_lookup == "Bangladesh"), fill = NA, color = PALETTE$bd_edge, linewidth = 0.8) +
  scale_fill_gradientn(
    colors = c("#FEF0D9", "#FDD49E", "#FC8D59", "#D7301F", "#7F0000"),
    na.value = PALETTE$missing,
    name = INDICATOR_LABEL
  ) +
  labs(
    title = paste0("Global ", INDICATOR_SHORT, " Prevalence"),
    subtitle = "WHO World Health Statistics 2022  ·  Incidence per 100,000 population",
    caption = "#30DayChartChallenge"
  ) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = PALETTE$background, color = NA),
    panel.background = element_rect(fill = PALETTE$background, color = NA),
    plot.title = element_text(color = PALETTE$title, face = "bold", size = 18, margin = margin(t = 20, b = 5)),
    plot.subtitle = element_text(color = PALETTE$axis, size = 10, margin = margin(b = 20)),
    plot.caption = element_text(color = "#AAAAAA", size = 8, hjust = 0.95),
    legend.position = "bottom",
    legend.title = element_text(size = 9, color = PALETTE$axis),
    legend.key.width = unit(2, "cm")
  )

ggsave(OUTPUT_FILE, plot, width = 12, height = 7, dpi = 300, bg = PALETTE$background)
cat(paste0("Saved → ", OUTPUT_FILE, "\n"))
