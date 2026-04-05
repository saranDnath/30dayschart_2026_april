if (!require(pacman)) {
    install.packages("pacman")
}

pacman::p_load(
    ggplot2,
    dplyr,
    ggpubr
)

if (interactive() && requireNamespace("rstudioapi", quietly = TRUE)) {
    setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
}


data <- msleep %>%
    filter(!is.na(sleep_total), !is.na(vore)) %>%
    mutate(vore = recode(vore,
        "carni"   = "Carnivore",
        "herbi"   = "Herbivore",
        "omni"    = "Omnivore",
        "insecti" = "Insectivore"
    ))

PALETTE <- list(
    background = "#F7F3EE",
    title      = "#1A1A2E",
    axis       = "#4A4A5A",
    grid       = "#E0D9D0"
)

fill_colors <- c(
    "Carnivore"   = "#2C6FA6",
    "Herbivore"   = "#4CAF7D",
    "Omnivore"    = "#E8A020",
    "Insectivore" = "#D62828"
)

# Fix: set factor levels to control order
data$vore <- factor(data$vore,
    levels = c("Carnivore", "Herbivore", "Omnivore", "Insectivore")
)

p <- ggplot(data, aes(x = vore, y = sleep_total, fill = vore)) +
    geom_violin(
        trim = FALSE, # fixed typo: triim -> trim
        alpha = 0.85,
        color = "white",
        linewidth = 0.4
    ) +
    geom_boxplot(
        width = 0.15,
        fill = "white",
        color = "#1A1A2E",
        outlier.shape = 21,
        outlier.fill = "white",
        outlier.color = "#1A1A2E",
        outlier.size = 1.5,
        linewidth = 0.5
    ) +
    stat_compare_means(
        comparisons = list(
            c("Carnivore", "Herbivore"),
            c("Carnivore", "Omnivore"),
            c("Herbivore", "Omnivore"),
            c("Insectivore", "Omnivore"),
            c("Insectivore", "Herbivore"),
            c("Insectivore", "Carnivore")
        ),
        method = "wilcox.test",
        method.args = list(exact = FALSE),
        label = "p.signif",
        tip.length = 0.01
    ) +
    stat_compare_means(
        method  = "kruskal.test",
        label.x = 0.7,
        label.y = 22,
        size    = 3.5,
        color   = PALETTE$axis # fixed: color not label.colour
    ) +
    scale_fill_manual(values = fill_colors) +
    labs(
        title    = "Do Carnivores Sleep More? Mammal Sleep by Diet Type",
        subtitle = "ggplot2 built-in msleep dataset  ·  Total sleep hours per day",
        x        = "Diet Type",
        y        = "Total Sleep (hours/day)",
        caption  = "#30DayChartChallenge"
    ) +
    theme_minimal(base_size = 13) +
    theme(
        plot.background = element_rect(fill = PALETTE$background, color = NA),
        panel.background = element_rect(fill = PALETTE$background, color = NA),
        panel.grid.major.y = element_line(
            color = PALETTE$grid,
            linetype = "dashed", linewidth = 0.5
        ),
        panel.grid.major.x = element_blank(),
        panel.grid.minor = element_blank(),
        legend.position = "none",
        axis.text = element_text(color = PALETTE$axis, size = 11),
        axis.title = element_text(
            color = PALETTE$axis,
            face = "bold", size = 13
        ),
        plot.title = element_text(
            color = PALETTE$title,
            face = "bold", size = 16,
            margin = margin(b = 4)
        ),
        plot.subtitle = element_text(
            color = PALETTE$axis, # fixed: removed alpha
            size = 10,
            margin = margin(b = 15)
        ),
        plot.caption = element_text(color = "#AAAAAA", size = 9, hjust = 1),
        plot.margin = margin(15, 20, 10, 15)
    )

output_path <- file.path(getwd(), "day_6.png")
ggsave(output_path, p, width = 11, height = 8, dpi = 300, bg = PALETTE$background)
cat("Saved →", output_path, "\n")
