setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

library(tidyverse)
library(readxl)
library(ggtext)
library(scales)

highlight_countries <- c(
    "Bangladesh", "India", "Pakistan", "Sri Lanka", "Nepal", "Bhutan", "Maldives", "Afghanistan",
    "China", "United Kingdom", "United States", "Mexico", "Brazil", "South Africa", "Nigeria", "Australia"
)

PALETTE <- list(
    background = "#F7F3EE",
    grid = "#E0D9D0",
    dot_doctor = "#2C6FA6",
    dot_nurse = "#E8A020",
    line_default = "#C8BFB5",
    line_bd = "#D62828",
    label_hl = "#1A3D5C",
    label_bd = "#006A4E",
    title = "#1A1A2E",
    axis = "#4A4A5A"
)

get_shortname <- function(name) {
    matched <- highlight_countries[str_detect(tolower(name), tolower(highlight_countries))]
    if (length(matched) > 0) matched[1] else name
}

df <- read_excel("dataset_world_health_stat_2022.xlsx",
    sheet = "Annex 2-3", col_names = FALSE
)

data <- df[6:nrow(df), c(1, 11, 12)] %>%
    setNames(c("Country", "Doctors", "Nurses")) %>%
    mutate(
        Doctors  = suppressWarnings(as.numeric(Doctors)),
        Nurses   = suppressWarnings(as.numeric(Nurses))
    ) %>%
    filter(!is.na(Doctors), !is.na(Nurses)) %>%
    mutate(
        ShortName = map_chr(Country, get_shortname),
        Highlight = ShortName %in% highlight_countries
    ) %>%
    filter(Highlight) %>%
    arrange(Doctors) %>%
    mutate(
        y = row_number(),
        is_bd = ShortName == "Bangladesh",
        lcolor = if_else(is_bd, PALETTE$line_bd, PALETTE$line_default),
        fcolor = if_else(is_bd, PALETTE$label_bd, PALETTE$label_hl),
        lwidth = if_else(is_bd, 2.5, 1.5)
    )

# Create named vectors for axis styling to highlight Bangladesh
axis_colors <- setNames(rep(PALETTE$label_hl, nrow(data)), data$ShortName)
axis_colors["Bangladesh"] <- PALETTE$label_bd

axis_face <- setNames(rep("plain", nrow(data)), data$ShortName)
axis_face["Bangladesh"] <- "bold"

plot <- ggplot(data) +
    # Connecting lines
    geom_segment(
        aes(
            x = Doctors, xend = Nurses, y = y, yend = y,
            color = I(lcolor), linewidth = I(lwidth)
        ),
        alpha = 0.8
    ) +
    # Doctor dots
    geom_point(aes(x = Doctors, y = y),
        color = PALETTE$dot_doctor, size = 4,
        shape = 21, fill = PALETTE$dot_doctor, stroke = 1.2
    ) +
    # Nurse dots
    geom_point(aes(x = Nurses, y = y),
        color = PALETTE$dot_nurse, size = 4,
        shape = 21, fill = PALETTE$dot_nurse, stroke = 1.2
    ) +
    # Doctor value labels
    geom_text(
        aes(
            x = Doctors, y = y, label = sprintf("%.1f", Doctors),
            color = I(fcolor)
        ),
        hjust = 1.4, size = 3.2, fontface = "bold"
    ) +
    # Nurse value labels
    geom_text(
        aes(
            x = Nurses, y = y, label = sprintf("%.1f", Nurses),
            color = I(fcolor)
        ),
        hjust = -0.4, size = 3.2, fontface = "bold"
    ) +
    scale_y_continuous(
        breaks = data$y,
        labels = data$ShortName
    ) +
    labs(
        title    = "Healthcare Workforce Gap: Doctors vs Nurses",
        subtitle = "WHO World Health Statistics 2022  ·  Density per 10,000 population",
        x        = "Density per 10,000 population",
        y        = NULL,
        caption  = "#30DayChartChallenge"
    ) +
    # Manual legend via annotation
    annotate("point",
        x = max(data$Nurses) * 0.6, y = 1.8,
        color = PALETTE$dot_doctor, size = 4
    ) +
    annotate("text",
        x = max(data$Nurses) * 0.6 + 2, y = 1.8,
        label = "Medical Doctors", hjust = 0,
        color = PALETTE$label_hl, size = 3.5
    ) +
    annotate("point",
        x = max(data$Nurses) * 0.6, y = 1.0,
        color = PALETTE$dot_nurse, size = 4
    ) +
    annotate("text",
        x = max(data$Nurses) * 0.6 + 2, y = 1.0,
        label = "Nurses & Midwives", hjust = 0,
        color = PALETTE$label_hl, size = 3.5
    ) +
    theme_minimal(base_size = 12) +
    theme(
        plot.background = element_rect(fill = PALETTE$background, color = NA),
        panel.background = element_rect(fill = PALETTE$background, color = NA),
        panel.grid.major.x = element_line(color = PALETTE$grid, linetype = "dashed", linewidth = 0.5),
        panel.grid.major.y = element_blank(),
        panel.grid.minor = element_blank(),
        axis.text.y = element_text(size = 11, color = axis_colors, face = axis_face),
        axis.text.x = element_text(color = PALETTE$axis, size = 10),
        axis.title.x = element_text(
            color = PALETTE$axis, face = "bold",
            size = 13, margin = margin(t = 10)
        ),
        plot.title = element_text(
            color = PALETTE$title, face = "bold",
            size = 17, margin = margin(b = 4)
        ),
        plot.subtitle = element_text(
            color = alpha(PALETTE$axis, 0.75), size = 10,
            margin = margin(b = 15)
        ),
        plot.caption = element_text(color = "#AAAAAA", size = 9, hjust = 1),
        plot.margin = margin(15, 20, 10, 15)
    )

ggsave("day_4_r.png", plot, width = 12, height = 8, dpi = 300, bg = PALETTE$background)
cat("Saved → day_4_r.png\n")
