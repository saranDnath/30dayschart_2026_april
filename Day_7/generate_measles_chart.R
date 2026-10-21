# Load required libraries
library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(patchwork)

# File paths
cases_file <- "Measles reported cases and incidence 2026-05-04 05-46 UTC.xlsx"
coverage_file <- "vaccine_coverage.xlsx"

# Years of interest (numeric matching the Excel column names where applicable)
years_numeric <- 2010:2024

# 1. Process Cases Data
cases_df <- read_excel(cases_file)

cases_bd <- cases_df %>%
  filter(`Country / Region` == "Bangladesh") %>%
  select(all_of(as.character(years_numeric))) %>%
  pivot_longer(everything(), names_to = "Year", values_to = "Cases") %>%
  mutate(
    Year = as.numeric(Year),
    Cases = as.numeric(gsub(",", "", Cases)) # Remove commas for numbers > 1,000
  ) %>%
  arrange(Year)

# 2. Process Coverage Data
cov_df <- read_excel(coverage_file)

# Filter for Bangladesh and the WUENIC estimates category
cov_bd <- cov_df %>%
  filter(`Country / Region` == "Bangladesh", Category == "WUENIC")

mcv1 <- cov_bd %>% 
  filter(`Disease / Antigen` == "Measles-containing vaccine, 1st dose") %>%
  select(all_of(as.character(years_numeric))) %>%
  pivot_longer(everything(), names_to = "Year", values_to = "MCV1") %>%
  mutate(
    Year = as.numeric(Year),
    MCV1 = as.numeric(gsub("%", "", MCV1)) # Remove percentage signs
  )

mcv2 <- cov_bd %>% 
  filter(`Disease / Antigen` == "Measles-containing vaccine, 2nd dose") %>%
  select(all_of(as.character(years_numeric))) %>%
  pivot_longer(everything(), names_to = "Year", values_to = "MCV2") %>%
  mutate(
    Year = as.numeric(Year),
    MCV2 = as.numeric(gsub("%", "", MCV2))
  )

# Join coverage data
cov_merged <- left_join(mcv1, mcv2, by = "Year")

# 3. Create Plots
# Top Plot: Coverage Plot
p1 <- ggplot(cov_merged, aes(x = Year)) +
  geom_line(aes(y = MCV1, color = "MCV1 Coverage"), linewidth = 1) +
  geom_point(aes(y = MCV1, color = "MCV1 Coverage"), size = 2) +
  geom_line(aes(y = MCV2, color = "MCV2 Coverage"), linewidth = 1) +
  geom_point(aes(y = MCV2, color = "MCV2 Coverage"), size = 2) +
  geom_hline(aes(yintercept = 95, color = "Herd Immunity Threshold (~95%)"), linetype = "dashed") +
  scale_color_manual(values = c("MCV1 Coverage" = "#1f77b4", 
                                "MCV2 Coverage" = "#ff7f0e", 
                                "Herd Immunity Threshold (~95%)" = "#d62728")) +
  theme_bw() +
  labs(
    title = "The Story of Measles in Bangladesh: When Coverage Drops, Outbreaks Surge",
    y = "Vaccination Coverage (%)",
    x = NULL,
    color = NULL
  ) +
  theme(legend.position = c(1, 0), legend.justification = c(1, 0), legend.background = element_rect(fill = alpha("white", 0.7)))

# Bottom Plot: Cases Bar Chart
p2 <- ggplot(cases_bd, aes(x = Year, y = Cases)) +
  geom_col(aes(fill = "Reported Measles Cases"), alpha = 0.8) +
  scale_fill_manual(values = c("Reported Measles Cases" = "#d62728")) +
  theme_bw() +
  labs(
    y = "Number of Cases",
    x = "Year",
    fill = NULL
  ) +
  theme(legend.position = c(1, 1), legend.justification = c(1, 1), legend.background = element_rect(fill = alpha("white", 0.7)))

# Combine plots using patchwork (p1 over p2)
final_plot <- p1 / p2 + plot_layout(heights = c(1, 1))

# Display and save the plot
print(final_plot)
ggsave("measles_real_data_chart_R.png", final_plot, width = 10, height = 8, dpi = 300)
cat("Chart generated and saved as 'measles_real_data_chart_R.png'\n")
