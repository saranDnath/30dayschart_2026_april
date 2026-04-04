import os

py_scatter = """import os
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import numpy as np

highlight_countries = [
    'Bangladesh', 'India', 'Pakistan', 'Sri Lanka', 'Nepal', 'Bhutan', 'Maldives', 'Afghanistan',
    'China', 'Japan', 'United Kingdom', 'United States', 'Mexico', 'Brazil', 'South Africa', 'Nigeria', 'Australia'
]

PALETTE = {
    'background':   '#F7F3EE',
    'grid':         '#E0D9D0',
    'dot_bg':       '#C8BFB5',
    'dot_highlight':'#2C6FA6',
    'dot_bd':       '#D62828',
    'label_hl':     '#1A3D5C',
    'label_bd':     '#006A4E',
    'title':        '#1A1A2E',
    'axis':         '#4A4A5A',
}

def get_shortname(c_name):
    for k in highlight_countries:
        if k.lower() in str(c_name).lower(): return k
    return c_name

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("Loading dataset...")
    url = 'https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx'
    file_path = os.path.join(script_dir, 'dataset_world_health_stat_2022.xlsx')
    if not os.path.exists(file_path):
        urllib.request.urlretrieve(url, file_path)

    df = pd.read_excel(file_path, sheet_name='{sheet}', header=None)
    data = df.iloc[5:].copy()
    data = data[[0, {col_x}, {col_y}]]
    data.columns = ['Country', '{name_x}', '{name_y}']
    data['{name_x}'] = pd.to_numeric(data['{name_x}'], errors='coerce')
    data['{name_y}'] = pd.to_numeric(data['{name_y}'], errors='coerce')
    data = data.dropna()
    data['ShortName'] = data['Country'].apply(get_shortname)
    data['Highlight'] = data['ShortName'].isin(highlight_countries)
    data['Label'] = data.apply(
        lambda r: f"{r['ShortName']} ({r['{name_x}']:.1f}, {r['{name_y}']:.1f})"
        if r['Highlight'] else "", axis=1
    )

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(PALETTE['background'])
    ax.set_facecolor(PALETTE['background'])

    ax.grid(True, color=PALETTE['grid'], linewidth=0.8, linestyle='--', alpha=0.9)
    ax.set_axisbelow(True)

    bg = data[~data['Highlight']]
    ax.scatter(bg['{name_x}'], bg['{name_y}'], color=PALETTE['dot_bg'], s=45, alpha=0.55, edgecolor='white', linewidths=0.4, zorder=1)

    hl = data[data['Highlight'] & (data['ShortName'] != 'Bangladesh')]
    ax.scatter(hl['{name_x}'], hl['{name_y}'], color=PALETTE['dot_highlight'], s=180, alpha=0.92, edgecolor='white', linewidths=1.5, zorder=3)

    bd = data[data['ShortName'] == 'Bangladesh']
    if not bd.empty:
        ax.scatter(bd['{name_x}'], bd['{name_y}'], color=PALETTE['dot_bd'], s=520, alpha=0.20, edgecolor='none', zorder=4)
        ax.scatter(bd['{name_x}'], bd['{name_y}'], color=PALETTE['dot_bd'], s=260, edgecolor='white', linewidths=2.0, zorder=5)

    for _, row in data[data['Highlight']].iterrows():
        is_bd = row['ShortName'] == 'Bangladesh'
        dx, dy = (8, 6)
        ax.annotate(
            row['Label'], xy=(row['{name_x}'], row['{name_y}']), xytext=(dx, dy), textcoords='offset points',
            color=PALETTE['label_bd'] if is_bd else PALETTE['label_hl'],
            fontsize=10.5 if is_bd else 9.5, fontweight='bold' if is_bd else 'semibold', zorder=7,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='white')]
        )

    ax.tick_params(colors=PALETTE['axis'], labelsize=11)
    for spine in ax.spines.values(): spine.set_edgecolor(PALETTE['grid'])

    ax.set_xlabel('{label_x}', fontsize=13, fontweight='bold', color=PALETTE['axis'], labelpad=10)
    ax.set_ylabel('{label_y}', fontsize=13, fontweight='bold', color=PALETTE['axis'], labelpad=10)
    {extra_python}

    fig.text(0.2, 0.975, '{title}', fontsize=17, fontweight='bold', color=PALETTE['title'], va='top')
    fig.text(0.2, 0.95, '{subtitle}', fontsize=10, color=PALETTE['title'], va='top', alpha=0.75)

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE['dot_bd'], markersize=11, label='Bangladesh', markeredgecolor='white', markeredgewidth=1.5),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE['dot_highlight'], markersize=9, label='Selected countries', markeredgecolor='white', markeredgewidth=1.2),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE['dot_bg'], markersize=7, label='Other countries', markeredgecolor='white', markeredgewidth=0.8),
    ]
    ax.legend(handles=legend_elements, loc='upper right', frameon=True, framealpha=0.85, edgecolor=PALETTE['grid'], fontsize=10, labelcolor=PALETTE['axis'], facecolor=PALETTE['background'])
    fig.text(0.98, 0.015, '#30DayChartChallenge', ha='right', fontsize=9, color='#AAAAAA')

    plt.tight_layout(rect=[0, 0.02, 1, 0.97])
    output_filename = os.path.join(script_dir, '{out_name}_python.png')
    plt.savefig(output_filename, dpi=300, facecolor=PALETTE['background'], bbox_inches='tight')
    print(f"Saved -> {output_filename}")

if __name__ == '__main__':
    main()
"""

r_scatter = """library(readxl)
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

df <- suppressWarnings(read_excel(destfile, sheet = "{sheet}", col_names = FALSE))
data <- df[6:nrow(df), c(1, {r_col_x}, {r_col_y})]
colnames(data) <- c("Country", "{name_x}", "{name_y}")
data <- data %>% mutate(across(c({name_x}, {name_y}), as.numeric)) %>% filter(!is.na({name_x}) & !is.na({name_y}))

data <- data %>% mutate(
  ShortName = sapply(Country, function(c) {
    m <- highlight_countries[sapply(highlight_countries, function(n) grepl(n, c, ignore.case=TRUE))]
    if(length(m)>0) m[1] else c
  }),
  Highlight = ShortName %in% highlight_countries,
  Label = ifelse(Highlight, sprintf("%s (%.1f, %.1f)", ShortName, {name_x}, {name_y}), "")
)

plot <- ggplot() +
  geom_point(data = data %>% filter(!Highlight), aes(x={name_x}, y={name_y}), color="#C8BFB5", size=3, alpha=0.55, stroke=0.4) +
  geom_point(data = data %>% filter(Highlight & ShortName != "Bangladesh"), aes(x={name_x}, y={name_y}), color="#2C6FA6", size=5, alpha=0.92, stroke=1.5) +
  
  geom_point(data = data %>% filter(ShortName == "Bangladesh"), aes(x={name_x}, y={name_y}), color="#D62828", size=14, alpha=0.20) +
  geom_point(data = data %>% filter(ShortName == "Bangladesh"), aes(x={name_x}, y={name_y}), fill="#D62828", color="white", shape=21, size=8, stroke=2.0) +
  
  geom_text_repel(data = data %>% filter(Highlight), 
                  aes(x={name_x}, y={name_y}, label=Label, color=ifelse(ShortName == "Bangladesh", "#006A4E", "#1A3D5C")), 
                  fontface="bold", size=3.5, bg.color="white", bg.r=0.15, max.overlaps=Inf) +
  scale_color_identity() +
  {extra_r} +
  theme_minimal() +
  labs(title="{title}", subtitle="{subtitle}", x="{label_x}", y="{label_y}") +
  theme(plot.background = element_rect(fill="#F7F3EE", color=NA), panel.background = element_rect(fill="#F7F3EE", color=NA),
        panel.grid.major = element_line(color="#E0D9D0", linetype="dashed", linewidth=0.8), panel.grid.minor = element_blank(),
        plot.title = element_text(color="#1A1A2E", face="bold", size=18, margin=margin(b=5)), plot.subtitle = element_text(color="#1A1A2E", size=11, margin=margin(b=15)),
        axis.title = element_text(color="#4A4A5A", face="bold", size=13), axis.text = element_text(color="#4A4A5A", size=11), legend.position = "none")

ggsave("{out_name}_r.png", plot, width = 12, height = 8, dpi = 300, bg="#F7F3EE")
"""

configs = [
    {
        'day': 2, 'sheet': 'Annex 2-1', 'col_x': 6, 'col_y': 9, 'r_col_x': 7, 'r_col_y': 10,
        'name_x': 'Life_Exp', 'name_y': 'Healthy_Life_Exp', 'out_name': 'day_2',
        'title': 'Quality of Life Gap: Life Expectancy vs Healthy Life',
        'subtitle': 'WHO World Health Statistics 2022  ·  Life expectancy vs Healthy life expectancy at birth',
        'label_x': 'Life Expectancy (Years)', 'label_y': 'Healthy Life Expectancy (Years)',
        'extra_python': "ax.axline((0, 0), slope=1, color=PALETTE['axis'], linestyle='--', alpha=0.5, zorder=0)",
        'extra_r': 'geom_abline(intercept = 0, slope = 1, color = "#4A4A5A", linetype = "dashed", alpha = 0.5)'
    },
    {
        'day': 3, 'sheet': 'Annex 2-1', 'col_x': 11, 'col_y': 10, 'r_col_x': 12, 'r_col_y': 11,
        'name_x': 'Skilled_Birth', 'name_y': 'Maternal_Mortality', 'out_name': 'day_3',
        'title': 'Maternal Mortality vs Skilled Birth Attendance', 'subtitle': 'WHO World Health Statistics 2022  ·  Proportion of births attended by skilled personnel vs MMR',
        'label_x': 'Births Attended by Skilled Personnel (%)', 'label_y': 'Maternal Mortality Ratio (log scale)',
        'extra_python': "ax.set_yscale('log')",
        'extra_r': 'scale_y_log10()'
    },
    {
        'day': 4, 'sheet': 'Annex 2-3', 'col_x': 10, 'col_y': 11, 'r_col_x': 11, 'r_col_y': 12,
        'name_x': 'Doctors', 'name_y': 'Nurses', 'out_name': 'day_4',
        'title': 'Health Workforce: Doctors vs Nurses Density', 'subtitle': 'WHO World Health Statistics 2022  ·  Doctors vs Nurses & Midwives per 10,000',
        'label_x': 'Doctors (per 10k log)', 'label_y': 'Nurses & Midwives (per 10k log)',
        'extra_python': "ax.set_xscale('log')\n    ax.set_yscale('log')",
        'extra_r': 'scale_x_log10() + scale_y_log10()'
    }
]

for cfg in configs:
    py_c = py_scatter
    r_c = r_scatter
    for k, v in cfg.items():
        py_c = py_c.replace("{" + k + "}", str(v))
        r_c = r_c.replace("{" + k + "}", str(v))
    
    os.makedirs(f"Day_{cfg['day']}", exist_ok=True)
    with open(f"Day_{cfg['day']}/day_{cfg['day']}.py", 'w', encoding='utf-8') as f: f.write(py_c)
    with open(f"Day_{cfg['day']}/day_{cfg['day']}.R", 'w', encoding='utf-8') as f: f.write(r_c)

py_bar = """import os
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

highlight_countries = ['Bangladesh', 'India', 'Pakistan', 'Sri Lanka', 'Nepal', 'Bhutan', 'Maldives', 'Afghanistan', 'China', 'Japan', 'United Kingdom', 'United States', 'Mexico', 'Brazil', 'South Africa', 'Nigeria', 'Australia']

PALETTE = {
    'background':   '#F7F3EE', 'grid': '#E0D9D0', 'bar_wasting': '#E07A5F', 'bar_stunting': '#3D5A80',
    'label_hl':     '#1A3D5C', 'label_bd': '#006A4E', 'title': '#1A1A2E', 'axis': '#4A4A5A',
}

def get_shortname(c_name):
    for k in highlight_countries:
        if k.lower() in str(c_name).lower(): return k
    return c_name

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'dataset_world_health_stat_2022.xlsx')
    if not os.path.exists(file_path): urllib.request.urlretrieve('https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx', file_path)

    df = pd.read_excel(file_path, sheet_name='Annex 2-4', header=None)
    data = df.iloc[5:].copy()
    data = data[[0, 1, 3]]
    data.columns = ['Country', 'Stunting', 'Wasting']
    data['Stunting'] = pd.to_numeric(data['Stunting'], errors='coerce')
    data['Wasting'] = pd.to_numeric(data['Wasting'], errors='coerce')
    data = data.dropna()
    data['ShortName'] = data['Country'].apply(get_shortname)
    data['Highlight'] = data['ShortName'].isin(highlight_countries)
    data = data[data['Highlight']].sort_values('Stunting', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(PALETTE['background'])
    ax.set_facecolor(PALETTE['background'])
    ax.grid(True, axis='x', color=PALETTE['grid'], linewidth=0.8, linestyle='--', alpha=0.9)
    ax.set_axisbelow(True)

    bars_w = ax.barh(data['ShortName'], -data['Wasting'], color=PALETTE['bar_wasting'], label='Wasting (Acute)', edgecolor='white', linewidth=1)
    bars_s = ax.barh(data['ShortName'], data['Stunting'], color=PALETTE['bar_stunting'], label='Stunting (Chronic)', edgecolor='white', linewidth=1)
    ax.axvline(0, color=PALETTE['axis'], linewidth=1.5)

    for bar in bars_w: ax.text(bar.get_width() - 0.5, bar.get_y() + bar.get_height()/2, f"{-bar.get_width():.1f}%", ha='right', va='center', fontsize=9, color=PALETTE['label_hl'])
    for bar in bars_s: ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.1f}%", ha='left', va='center', fontsize=9, color=PALETTE['label_hl'])

    ax.set_xticks([])
    for spine in ax.spines.values(): spine.set_visible(False)
    for label in ax.get_yticklabels():
        if label.get_text() == 'Bangladesh':
            label.set_color(PALETTE['label_bd'])
            label.set_weight('bold')
        else: label.set_color(PALETTE['label_hl'])

    fig.text(0.1, 0.95, 'Childhood Malnutrition: Wasting vs Stunting', fontsize=17, fontweight='bold', color=PALETTE['title'], va='top')
    fig.text(0.1, 0.92, 'WHO World Health Statistics 2022  ·  % Under-5s', fontsize=10, color=PALETTE['title'], va='top', alpha=0.75)
    ax.legend(loc='lower right', frameon=True, facecolor=PALETTE['background'], edgecolor=PALETTE['grid'])
    fig.text(0.98, 0.015, '#30DayChartChallenge', ha='right', fontsize=9, color='#AAAAAA')
    plt.tight_layout(rect=[0, 0.02, 1, 0.90])
    plt.savefig(os.path.join(script_dir, 'day_5_python.png'), dpi=300, facecolor=PALETTE['background'], bbox_inches='tight')

if __name__ == '__main__': main()
"""

r_bar = """library(readxl)
library(dplyr)
library(ggplot2)

if (interactive() && requireNamespace("rstudioapi", quietly = TRUE)) { setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) }
destfile <- "dataset_world_health_stat_2022.xlsx"
if (!file.exists(destfile)) { download.file("https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx", destfile, mode = "wb") }

highlight_countries <- c("Bangladesh", "India", "Pakistan", "Sri Lanka", "Nepal", "Bhutan", "Maldives", "Afghanistan", "China", "Japan", "United Kingdom", "United States", "Mexico", "Brazil", "South Africa", "Nigeria", "Australia")

df <- suppressWarnings(read_excel(destfile, sheet = "Annex 2-4", col_names = FALSE))
data <- df[6:nrow(df), c(1, 2, 4)]
colnames(data) <- c("Country", "Stunting", "Wasting")
data <- data %>% mutate(across(c(Stunting, Wasting), as.numeric)) %>% filter(!is.na(Stunting)) %>% mutate(
  ShortName = sapply(Country, function(c) { m <- highlight_countries[sapply(highlight_countries, function(n) grepl(n, c, ignore.case=TRUE))]; if(length(m)>0) m[1] else c }),
  Highlight = ShortName %in% highlight_countries) %>% filter(Highlight) %>% arrange(Stunting) %>% mutate(ShortName = factor(ShortName, levels = ShortName))

plot <- ggplot(data) + 
  geom_bar(aes(x = ShortName, y = Stunting, fill = "Stunting (Chronic)"), stat = "identity", color="white") +
  geom_bar(aes(x = ShortName, y = -Wasting, fill = "Wasting (Acute)"), stat = "identity", color="white") +
  geom_text(aes(x = ShortName, y = Stunting, label = sprintf("%.1f%%", Stunting)), size=3, hjust=-0.2, color="#1A3D5C") +
  geom_text(aes(x = ShortName, y = -Wasting, label = sprintf("%.1f%%", Wasting)), size=3, hjust=1.2, color="#1A3D5C") +
  scale_fill_manual(values = c("Stunting (Chronic)" = "#3D5A80", "Wasting (Acute)" = "#E07A5F")) + coord_flip() + theme_minimal() +
  labs(title="Childhood Malnutrition: Wasting vs Stunting", subtitle="WHO World Health Statistics 2022  ·  % Under-5s", x="", y="", fill="") +
  theme(plot.background = element_rect(fill="#F7F3EE", color=NA), panel.background = element_rect(fill="#F7F3EE", color=NA),
        panel.grid.major.x = element_line(color="#E0D9D0", linetype="dashed", linewidth=0.8), panel.grid.minor = element_blank(), panel.grid.major.y = element_blank(),
        plot.title = element_text(color="#1A1A2E", face="bold", size=18, margin=margin(b=5)), plot.subtitle = element_text(color="#1A1A2E", size=11, margin=margin(b=15)),
        axis.text.x = element_blank(), 
        axis.text.y = element_text(color = sapply(levels(data$ShortName), function(s) if(s=="Bangladesh") "#006A4E" else "#1A3D5C"), face = sapply(levels(data$ShortName), function(s) if(s=="Bangladesh") "bold" else "plain")),
        legend.position = "bottom")

ggsave("day_5_r.png", plot, width = 10, height = 8, dpi = 300, bg="#F7F3EE")
"""

os.makedirs('Day_5', exist_ok=True)
with open("Day_5/day_5.py", 'w', encoding='utf-8') as f: f.write(py_bar)
with open("Day_5/day_5.R", 'w', encoding='utf-8') as f: f.write(r_bar)
print("Bar charts generated")
