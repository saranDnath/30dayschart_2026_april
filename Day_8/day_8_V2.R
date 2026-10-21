# ============================================================
# #30DayChartChallenge — Day 08: Circular
# Sugar-Sweetened Beverage Intake (g/day) · GDD 2018
# Nightingale Rose (Polar Area) Chart  |  R + ggplot2
#
# Install deps:
#   install.packages(c("tidyverse", "ggtext"))
# ============================================================

library(tidyverse)
library(ggtext)

# ── 1. Load & filter ─────────────────────────────────────────
df <- read_csv("sugar_intake_country_wise_2018.csv.gz")

data <- df |>
  filter(year == 2018, age == 999, female == 999, urban == 999, edu == 999)

# ── 2. Aggregate to superregion level ─────────────────────────
sr <- data |>
  group_by(superregion2) |>
  summarise(
    mean_intake = mean(median),
    n           = n(),
    .groups     = "drop"
  ) |>
  arrange(desc(mean_intake)) |>
  mutate(
    # Nightingale rule: radius = sqrt(value) so AREA ∝ intake
    radius = sqrt(mean_intake),
    # Assign equal angles clockwise from top
    angle_mid  = seq(90, 90 - 360 * (n() - 1) / n(), length.out = n()),
    angle_start = angle_mid + (360 / n()) * 0.45,
    angle_end   = angle_mid - (360 / n()) * 0.45
  )

# ── 3. Palette & labels ───────────────────────────────────────
BG <- "#FAF9F6"

palette <- c(
  "LAC"   = "#E94B35",
  "SSA"   = "#F5A623",
  "MENA"  = "#9B59B6",
  "Asia"  = "#27AE60",
  "HIC"   = "#2E86C1",
  "FSU"   = "#17A589",
  "SAARC" = "#E67E22"
)
long_names <- c(
  "LAC"   = "Latin America\n& Caribbean",
  "SSA"   = "Sub-Saharan\nAfrica",
  "MENA"  = "Middle East\n& N. Africa",
  "Asia"  = "East &\nSE Asia",
  "HIC"   = "High-Income\nCountries",
  "FSU"   = "Former\nSoviet Union",
  "SAARC" = "South Asia"
)

# ── 4. Build petal polygons ───────────────────────────────────
# Each petal is a wedge from r=0 to r=radius, spanning its angular width.
# We approximate the arc with 60 points.

make_petal <- function(angle_start, angle_end, r, n_arc = 60) {
  arc_angles <- seq(angle_start, angle_end, length.out = n_arc)
  tibble(
    angle = c(0,        arc_angles,          0),
    rad   = c(0, rep(r, n_arc),             0)
  )
}

petals <- sr |>
  mutate(id = row_number()) |>
  rowwise() |>
  reframe(
    make_petal(angle_start, angle_end, radius),
    id           = id,
    superregion2 = superregion2
  )

# Convert polar to cartesian for geom_polygon
petals <- petals |>
  mutate(
    x = rad * cos(angle * pi / 180),
    y = rad * sin(angle * pi / 180)
  )

# ── 5. Reference circles (100, 200, 300 g/day) ───────────────
ref_circles <- map_dfr(c(100, 200, 300), function(val) {
  r <- sqrt(val)
  tibble(
    x    = r * cos(seq(0, 2 * pi, length.out = 300)),
    y    = r * sin(seq(0, 2 * pi, length.out = 300)),
    val  = val
  )
})

# Label position: in the gap between SAARC (last) and LAC (first)
gap_angle_deg <- sr$angle_mid[nrow(sr)] - (360 / nrow(sr)) * 0.52
gap_angle_rad <- gap_angle_deg * pi / 180

ref_labels <- tibble(
  val = c(100, 200, 300),
  r   = sqrt(c(100, 200, 300)),
  x   = r * cos(gap_angle_rad),
  y   = r * sin(gap_angle_rad),
  lbl = paste(c(100, 200, 300), "g")
)

# ── 6. Value labels (inside each petal) ───────────────────────
value_labels <- sr |>
  mutate(
    angle_rad = angle_mid * pi / 180,
    lx = radius * 0.52 * cos(angle_rad),
    ly = radius * 0.52 * sin(angle_rad),
    lbl = paste0(round(mean_intake), " g/day")
  )

# ── 7. Region labels (outside each petal) ─────────────────────
max_r      <- max(sr$radius)
label_push <- max_r * 0.30     # how far past petal tip to place label

region_labels <- sr |>
  mutate(
    angle_rad  = angle_mid * pi / 180,
    lx         = (radius + label_push) * cos(angle_rad),
    ly         = (radius + label_push) * sin(angle_rad),
    long_name  = paste0(long_names[superregion2], "\n(", n, " countries)")
  )

# ── 8. Plot ───────────────────────────────────────────────────
p <- ggplot() +
  
  # Reference rings
  geom_path(
    data = ref_circles,
    aes(x = x, y = y, group = val),
    color = "white", alpha = 0.10, linewidth = 0.5, linetype = "dashed"
  ) +
  
  # Reference ring labels
  geom_text(
    data = ref_labels,
    aes(x = x, y = y, label = lbl),
    color = "black", alpha = 0.4, size = 3.5, hjust = 0
  ) +
  
  # Petals
  geom_polygon(
    data = petals,
    aes(x = x, y = y, group = id, fill = superregion2),
    alpha = 0.88, color = "white", linewidth = 0.3
  ) +
  
  # Value labels inside petals
  geom_text(
    data = value_labels,
    aes(x = lx, y = ly, label = lbl),
    color = "white", fontface = "bold", size = 4.5, alpha = 0.95
  ) +
  
  # Region labels outside petals
  geom_label(
    data = region_labels,
    aes(x = lx, y = ly, label = long_name, color = superregion2),
    fill       = BG,
    label.size = 0,
    fontface   = "bold",
    size       = 4,
    alpha      = 0.95,
    lineheight = 1.2
  ) +
  
  scale_fill_manual(values  = palette, name = NULL) +
  scale_color_manual(values = palette, name = NULL) +
  
  labs(
    title    = "Sugar-Sweetened Beverage Consumption by Region",
    subtitle = "Mean daily intake (g/day) per world region  ·  Petal area ∝ intake  ·  GDD 2018",
    caption  = "Source: Global Dietary Database (GDD) 2018  ·  #30DayChartChallenge Day 08 — Circular"
  ) +
  
  coord_equal() +
  theme_void() +
  theme(
    plot.background  = element_rect(fill = BG, color = NA),
    panel.background = element_rect(fill = BG, color = NA),
    plot.title       = element_text(color = "black", size = 26, face = "bold",
                                    hjust = 0.5, margin = margin(b = 5)),
    plot.subtitle    = element_text(color = "#2C3E50", size = 13,
                                    hjust = 0.5, margin = margin(b = 10)),
    plot.caption     = element_text(color = "#555555", size = 10,
                                    hjust = 0.5, margin = margin(t = 10)),
    legend.position  = "none",
    plot.margin      = margin(14, 14, 10, 14)
  )

# ── 9. Save ───────────────────────────────────────────────────
ggsave(
  "ssb_nightingale.png",
  plot   = p,
  width  = 11,
  height = 11.5,
  dpi    = 300,
  bg     = BG
)
message("Saved: ssb_nightingale.png")