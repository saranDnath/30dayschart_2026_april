# Load required libraries
library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(patchwork)

# File paths
cases_file <- "Measles reported cases and incidence 2026-05-04 05-46 UTC.xlsx"
coverage_file <- "vaccine_coverage.xlsx"

# Years of interest (2000 to 2024)
years_numeric <- 2000:2024

# 1. Process Cases Data
cases_df <- read_excel(cases_file)

cases_bd <- cases_df %>%
  filter(`Country / Region` == "Bangladesh") %>%
  select(all_of(as.character(years_numeric))) %>%
  pivot_longer(everything(), names_to = "Year", values_to = "Cases") %>%
  mutate(
    Year = as.numeric(Year),
    Cases = as.numeric(gsub(",", "", Cases))
  )

# Add 2025 and 2026 outbreak data manually (from MoH/DGHS)
new_cases <- data.frame(Year = c(2025, 2026), Cases = c(125, 8534))
cases_bd <- bind_rows(cases_bd, new_cases) %>% arrange(Year)

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
    MCV1 = as.numeric(gsub("%", "", MCV1))
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

# Add 2025 & 2026 coverage updates manually (59.6% based on news)
new_cov <- data.frame(Year = c(2025, 2026), MCV1 = c(59.6, NA), MCV2 = c(59.6, NA))
cov_merged <- bind_rows(cov_merged, new_cov) %>% arrange(Year)

# 3. Create Plots
# Top Plot: Coverage Plot
p1 <- ggplot(cov_merged, aes(x = Year)) +
  annotate("rect", xmin = 2024.5, xmax = 2026.5, ymin = 0, ymax = Inf, alpha = 0.15, fill = "gray") +
  geom_line(aes(y = MCV1, color = "MCV1 Coverage"), linewidth = 1) +
  geom_point(aes(y = MCV1, color = "MCV1 Coverage"), size = 2) +
  geom_line(aes(y = MCV2, color = "MCV2 Coverage"), linewidth = 1) +
  geom_point(aes(y = MCV2, color = "MCV2 Coverage"), size = 2) +
  geom_hline(aes(yintercept = 95, color = "Herd Immunity Threshold (~95%)"), linetype = "dashed") +
  annotate("text", x = 2024.3, y = 65, label = "Data Source:\nMoH / News Reports\n(Plunges to 59.6%)", hjust = 1, vjust = 0, size = 3.5, fontface = "bold") +
  scale_color_manual(values = c("MCV1 Coverage" = "#1f77b4", 
                                "MCV2 Coverage" = "#ff7f0e", 
                                "Herd Immunity Threshold (~95%)" = "#d62728")) +
  theme_bw() +
  scale_x_continuous(breaks = seq(2000, 2026, by = 2)) +  # Force integer years
  labs(
    title = "The Story of Measles in Bangladesh: When Coverage Drops, Outbreaks Surge",
    y = "Vaccination Coverage (%)",
    x = NULL,
    color = NULL
  ) +
  theme(legend.position = c(0, 0), legend.justification = c(0, 0), legend.background = element_rect(fill = alpha("white", 0.7)))

# Bottom Plot: Cases Bar Chart
cases_bd <- cases_bd %>%
  mutate(DataType = ifelse(Year >= 2025, "MoH Outbreak / Suspected Cases", "WHO Reported Cases"))

p2 <- ggplot(cases_bd, aes(x = Year, y = Cases, fill = DataType)) +
  annotate("rect", xmin = 2024.5, xmax = 2026.5, ymin = 0, ymax = Inf, alpha = 0.15, fill = "gray") +
  geom_col(alpha = 0.9) +
  scale_fill_manual(values = c("WHO Reported Cases" = "#d62728", "MoH Outbreak / Suspected Cases" = "darkred")) +
  geom_text(data = filter(cases_bd, Year == 2026), aes(label = "8,534", y = Cases + 300), size = 3.5, color = "darkred", fontface="bold") +
  theme_bw() +
  scale_x_continuous(breaks = seq(2000, 2026, by = 2)) +  # Force integer years
  labs(
    y = "Number of Cases",
    x = "Year",
    fill = NULL,
    caption = "Source: 2000-2024 WHO Immunization Portal | 2025-2026 Ministry of Health / IFRC & News Reports"
  ) +
  theme(
    legend.position = c(0.5, 1), 
    legend.justification = c(0.5, 1), 
    legend.background = element_rect(fill = alpha("white", 0.7)),
    plot.caption = element_text(face = "italic", color = "dimgrey", size = 10, hjust = 0.5)
  )

# Combine plots using patchwork (p1 over p2)
final_plot <- p1 / p2 + plot_layout(heights = c(1, 1))

# Display and save the plot
print(final_plot)
ggsave("measles_real_data_chart_v3_R.png", final_plot, width = 11, height = 9, dpi = 300)
cat("Chart generated and saved as 'measles_real_data_chart_v3_R.png'\n")
