import os
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import numpy as np

highlight_countries = [
    'Bangladesh', 'India', 'Pakistan', 'Sri Lanka', 'Nepal', 'Bhutan', 'Maldives', 'Afghanistan',
    'China', 'United Kingdom', 'United States', 'Mexico', 'Brazil', 'South Africa', 'Nigeria', 'Australia'
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
    file_path = os.path.join(script_dir, 'dataset_world_health_stat_2022.xlsx')
    if not os.path.exists(file_path):
        urllib.request.urlretrieve('https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx', file_path)

    df = pd.read_excel(file_path, sheet_name='Annex 2-1', header=None)
    data = df.iloc[5:].copy()
    data = data[[0, 6, 9]]
    data.columns = ['Country', 'Life_Exp', 'Healthy_Life_Exp']
    data['Life_Exp'] = pd.to_numeric(data['Life_Exp'], errors='coerce')
    data['Healthy_Life_Exp'] = pd.to_numeric(data['Healthy_Life_Exp'], errors='coerce')
    data = data.dropna()
    data['ShortName'] = data['Country'].apply(get_shortname)
    data['Highlight'] = data['ShortName'].isin(highlight_countries)
    data['Label'] = data.apply(
        lambda r: f"{r['ShortName']} ({r['Life_Exp']:.1f}, {r['Healthy_Life_Exp']:.1f})"
        if r['Highlight'] else "", axis=1
    )

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(PALETTE['background'])
    ax.set_facecolor(PALETTE['background'])
    ax.grid(True, color=PALETTE['grid'], linewidth=0.8, linestyle='--', alpha=0.9)
    ax.set_axisbelow(True)

    bg = data[~data['Highlight']]
    ax.scatter(bg['Life_Exp'], bg['Healthy_Life_Exp'], color=PALETTE['dot_bg'], s=45, alpha=0.55, edgecolor='white', linewidths=0.4, zorder=1)

    hl = data[data['Highlight'] & (data['ShortName'] != 'Bangladesh')]
    ax.scatter(hl['Life_Exp'], hl['Healthy_Life_Exp'], color=PALETTE['dot_highlight'], s=180, alpha=0.92, edgecolor='white', linewidths=1.5, zorder=3)

    bd = data[data['ShortName'] == 'Bangladesh']
    if not bd.empty:
        ax.scatter(bd['Life_Exp'], bd['Healthy_Life_Exp'], color=PALETTE['dot_bd'], s=520, alpha=0.20, edgecolor='none', zorder=4)
        ax.scatter(bd['Life_Exp'], bd['Healthy_Life_Exp'], color=PALETTE['dot_bd'], s=260, edgecolor='white', linewidths=2.0, zorder=5)

    visible = data[(data['Life_Exp'] >= 50) & (data['Healthy_Life_Exp'] >= 45)]
    if not visible.empty:
        highest = visible.loc[visible['Life_Exp'].idxmax()]
        lowest  = visible.loc[visible['Life_Exp'].idxmin()]
        extremes = [highest['ShortName'], lowest['ShortName']]
    else:
        extremes = []

    from adjustText import adjust_text

    texts = []
    for _, row in data[data['Highlight']].iterrows():
        if row['ShortName'] in extremes: continue
        is_bd = row['ShortName'] == 'Bangladesh'
        t = ax.text(
            row['Life_Exp'], row['Healthy_Life_Exp'], row['Label'],
            color=PALETTE['label_bd'] if is_bd else PALETTE['label_hl'],
            fontsize=10.5 if is_bd else 9.5, fontweight='bold' if is_bd else 'semibold', zorder=7,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='white')]
        )
        texts.append(t)

    adjust_text(texts, ax=ax, expand=(1.2, 1.5), arrowprops=dict(arrowstyle='-', color='#8899AA', lw=0.6, alpha=0.5))

    if not visible.empty:
        ax.scatter(highest['Life_Exp'], highest['Healthy_Life_Exp'], color='#E8A020', s=180, edgecolor='white', linewidths=1.5, zorder=6)
        ax.annotate(
            f"{highest['ShortName']} ({highest['Life_Exp']:.1f}, {highest['Healthy_Life_Exp']:.1f})\n↑ Highest Life Expectancy",
            xy=(highest['Life_Exp'], highest['Healthy_Life_Exp']), xytext=(-125, 10), textcoords='offset points',
            fontsize=9, color='#8B5E00', fontweight='bold', path_effects=[pe.withStroke(linewidth=2.5, foreground='white')], zorder=8
        )

        ax.scatter(lowest['Life_Exp'], lowest['Healthy_Life_Exp'], color='#E8A020', s=180, edgecolor='white', linewidths=1.5, zorder=6)
        ax.annotate(
            f"{lowest['ShortName']} ({lowest['Life_Exp']:.1f}, {lowest['Healthy_Life_Exp']:.1f})\n↓ Lowest Life Expectancy",
            xy=(lowest['Life_Exp'], lowest['Healthy_Life_Exp']), xytext=(12, -10), textcoords='offset points',
            fontsize=9, color='#8B5E00', fontweight='bold', path_effects=[pe.withStroke(linewidth=2.5, foreground='white')], zorder=8
        )

    ax.tick_params(colors=PALETTE['axis'], labelsize=11)
    for spine in ax.spines.values(): spine.set_edgecolor(PALETTE['grid'])

    ax.set_xlabel('Life Expectancy (Years)', fontsize=13, fontweight='bold', color=PALETTE['axis'], labelpad=10)
    ax.set_ylabel('Healthy Life Expectancy (Years)', fontsize=13, fontweight='bold', color=PALETTE['axis'], labelpad=10)
    ax.set_xlim(50, 90)
    ax.set_ylim(45, 80)
    ax.axline((50, 50), slope=1, color=PALETTE['axis'], linestyle='--', alpha=0.4, zorder=0)
    ax.annotate('*axes start at 50 & 45', xy=(50, 45), xytext=(4, 4), textcoords='offset points', fontsize=8, color=PALETTE['axis'], alpha=0.6, style='italic', zorder=8)

    fig.text(0.2, 0.975, 'Quality of Life Gap: Life Expectancy vs Healthy Life', fontsize=17, fontweight='bold', color=PALETTE['title'], va='top')
    fig.text(0.2, 0.95, 'WHO World Health Statistics 2022  ·  Life expectancy vs Healthy life expectancy at birth', fontsize=10, color=PALETTE['title'], va='top', alpha=0.75)

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE['dot_bd'], markersize=11, label='Bangladesh', markeredgecolor='white', markeredgewidth=1.5),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE['dot_highlight'], markersize=9, label='Selected countries', markeredgecolor='white', markeredgewidth=1.2),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE['dot_bg'], markersize=7, label='Other countries', markeredgecolor='white', markeredgewidth=0.8),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E8A020', markersize=9, label='Highest / Lowest', markeredgecolor='white', markeredgewidth=1.2),
    ]
    ax.legend(handles=legend_elements, loc='upper right', frameon=True, framealpha=0.85, edgecolor=PALETTE['grid'], fontsize=10, labelcolor=PALETTE['axis'], facecolor=PALETTE['background'])
    fig.text(0.98, 0.015, '#30DayChartChallenge', ha='right', fontsize=9, color='#AAAAAA')

    plt.tight_layout(rect=[0, 0.02, 1, 0.97])
    output_filename = os.path.join(script_dir, 'day_2_python.png')
    plt.savefig(output_filename, dpi=300, facecolor=PALETTE['background'], bbox_inches='tight')
    print(f"Saved -> {output_filename}")

if __name__ == '__main__':
    main()
