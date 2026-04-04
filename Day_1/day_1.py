import os
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import numpy as np
from adjustText import adjust_text

highlight_countries = [
    'Bangladesh', 'India', 'Pakistan', 'Sri Lanka', 'Nepal', 'Bhutan', 'Maldives', 'Afghanistan',
    'China', 'Japan', 'United Kingdom', 'United States', 'Mexico', 'Brazil', 'South Africa', 'Nigeria', 'Australia'
]

# Color palette with clear visual hierarchy
PALETTE = {
    'background':   '#F7F3EE',
    'grid':         '#E0D9D0',
    'dot_bg':       '#C8BFB5',      # muted background dots
    'dot_highlight':'#2C6FA6',      # rich blue for highlighted countries
    'dot_bd':       '#D62828',      # strong red for Bangladesh
    'label_hl':     '#1A3D5C',      # dark navy for highlighted labels
    'label_bd':     '#006A4E',      # Bangladesh green
    'title':        '#1A1A2E',
    'axis':         '#4A4A5A',
}

def get_shortname(c_name):
    for k in highlight_countries:
        if k.lower() in str(c_name).lower():
            return k
    return c_name

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("Loading dataset...")
    url = 'https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx'
    file_path = os.path.join(script_dir, 'dataset_world_health_stat_2022.xlsx')
    if not os.path.exists(file_path):
        print("Downloading dataset...")
        urllib.request.urlretrieve(url, file_path)

    df = pd.read_excel(file_path, sheet_name='Annex 2-2', header=None)
    data = df.iloc[5:].copy()
    data = data[[0, 9, 10]]
    data.columns = ['Country', 'UHC_Index', 'OOP_10_percent']
    data['UHC_Index'] = pd.to_numeric(data['UHC_Index'], errors='coerce')
    data['OOP_10_percent'] = pd.to_numeric(data['OOP_10_percent'], errors='coerce')
    data = data.dropna()
    data['ShortName'] = data['Country'].apply(get_shortname)
    data['Highlight'] = data['ShortName'].isin(highlight_countries)
    data['Label'] = data.apply(
        lambda r: f"{r['ShortName']} ({r['UHC_Index']:.1f}, {r['OOP_10_percent']:.1f})"
        if r['Highlight'] else "", axis=1
    )

    # ── Figure setup ──────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(PALETTE['background'])
    ax.set_facecolor(PALETTE['background'])

    # Grid styling
    ax.grid(True, color=PALETTE['grid'], linewidth=0.8, linestyle='--', alpha=0.9)
    ax.set_axisbelow(True)

    # ── Background (non-highlighted) countries ────────────────────────────────
    bg = data[~data['Highlight']]
    ax.scatter(
        bg['UHC_Index'], bg['OOP_10_percent'],
        color=PALETTE['dot_bg'], s=45, alpha=0.55,
        edgecolor='white', linewidths=0.4, zorder=1
    )

    # ── Highlighted countries ─────────────────────────────────────────────────
    hl = data[data['Highlight'] & (data['ShortName'] != 'Bangladesh')]
    ax.scatter(
        hl['UHC_Index'], hl['OOP_10_percent'],
        color=PALETTE['dot_highlight'],
        s=180, alpha=0.92,
        edgecolor='white', linewidths=1.5,
        zorder=3
    )

    # ── Bangladesh (glowing dot) ─────────────────────────────────────────────────
    bd = data[data['ShortName'] == 'Bangladesh']
    if not bd.empty:
        # Outer glow ring
        ax.scatter(
            bd['UHC_Index'], bd['OOP_10_percent'],
            color=PALETTE['dot_bd'], s=520, alpha=0.20,
            edgecolor='none', zorder=4
        )
        ax.scatter(
            bd['UHC_Index'], bd['OOP_10_percent'],
            color=PALETTE['dot_bd'], s=260,
            edgecolor='white', linewidths=2.0,
            zorder=5
        )

    # Manual offsets (dx, dy) per country to avoid overlaps
    offsets = {
        'Afghanistan':    (-95, 8),
        'India':          (8, 8),
        'Bangladesh':     (10, 20),
        'Pakistan':       (8, -14),
        'Sri Lanka':      (8, 8),
        'Nepal':          (-95, 8),
        'Bhutan':         (8, -14),
        'Maldives':       (-110, 8),
        'China':          (8, 8),
        'Japan':          (8, 8),
        'United Kingdom': (-130, -16),
        'United States':  (8, 8),
        'Mexico':         (-100, -16),
        'Brazil':         (8, 8),
        'South Africa':   (-10, -20),
        'Nigeria':        (8, 8),
        'Australia':      (-125, 4),
    }

    for _, row in data[data['Highlight']].iterrows():
        is_bd = row['ShortName'] == 'Bangladesh'
        dx, dy = offsets.get(row['ShortName'], (8, 6))
        ax.annotate(
            row['Label'],
            xy=(row['UHC_Index'], row['OOP_10_percent']),
            xytext=(dx, dy),
            textcoords='offset points',
            color=PALETTE['label_bd'] if is_bd else PALETTE['label_hl'],
            fontsize=10.5 if is_bd else 9.5,
            fontweight='bold' if is_bd else 'semibold',
            zorder=7,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='white')]
    )

    # ── Axes ──────────────────────────────────────────────────────────────────
    ax.set_xlim(20, 100)
    ax.set_xticks([20, 30, 40, 50, 60, 70, 80, 90, 100])

    # Add a small note near the axis origin
    ax.annotate('*axis starts at 20', 
                xy=(20, 0), 
                fontsize=8, 
            color=PALETTE['axis'],
            alpha=0.6,
            style='italic')
    ax.set_ylim(0, 60)
    ax.set_yticks([0,10,20,30,40,50,60])
    ax.tick_params(colors=PALETTE['axis'], labelsize=11)
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE['grid'])

    ax.set_xlabel('Universal Health Coverage (UHC) Index',
                  fontsize=13, fontweight='bold', color=PALETTE['axis'], labelpad=10)
    ax.set_ylabel('% Population Spending on Health >10% of HH budget',
                  fontsize=13, fontweight='bold', color=PALETTE['axis'], labelpad=10)

    # ── Title & subtitle ──────────────────────────────────────────────────────
    fig.text(0.2, 0.975,
             'The cost of care: OOP Expenditure vs UHC',
             fontsize=17, fontweight='bold', color=PALETTE['title'], va='top')
    fig.text(0.2, 0.95,
             'WHO World Health Statistics 2022  ·  Catastrophic out-of-pocket spending vs. UHC coverage',
             fontsize=10, color=PALETTE['title'], va='top', alpha=0.75)

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE['dot_bd'],
               markersize=11, label='Bangladesh', markeredgecolor='white', markeredgewidth=1.5),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE['dot_highlight'],
               markersize=9,  label='Selected countries', markeredgecolor='white', markeredgewidth=1.2),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE['dot_bg'],
               markersize=7,  label='Other countries', markeredgecolor='white', markeredgewidth=0.8),
    ]
    leg = ax.legend(
        handles=legend_elements,
        loc='upper right', frameon=True,
        framealpha=0.85, edgecolor=PALETTE['grid'],
        fontsize=10, labelcolor=PALETTE['axis'],
        facecolor=PALETTE['background'],
    )

    # ── Watermark ─────────────────────────────────────────────────────────────
    fig.text(0.98, 0.015, '#30DayChartChallenge',
             ha='right', fontsize=9, color='#AAAAAA')

    plt.tight_layout(rect=[0, 0.02, 1, 0.97])
    output_filename = os.path.join(script_dir, 'cost_of_care_python.png')
    plt.savefig(output_filename, dpi=300, facecolor=PALETTE['background'], bbox_inches='tight')
    print(f"Saved → {output_filename}")

if __name__ == '__main__':
    main()