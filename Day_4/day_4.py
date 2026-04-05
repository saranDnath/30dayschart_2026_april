import os
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.lines as mlines
import numpy as np

highlight_countries = [
    'Bangladesh', 'India', 'Pakistan', 'Sri Lanka', 'Nepal', 'Bhutan', 'Maldives', 'Afghanistan',
    'China', 'United Kingdom', 'United States', 'Mexico', 'Brazil', 'South Africa', 'Nigeria', 'Australia'
]

PALETTE = {
    'background': '#F7F3EE',
    'grid':       '#E0D9D0',
    'dot_doctor': '#2C6FA6',
    'dot_nurse':  '#E8A020',
    'line_default': '#C8BFB5',
    'line_bd':    '#D62828',
    'label_hl':   '#1A3D5C',
    'label_bd':   '#006A4E',
    'title':      '#1A1A2E',
    'axis':       '#4A4A5A',
}

def get_shortname(c_name):
    for k in highlight_countries:
        if k.lower() in str(c_name).lower():
            return k
    return c_name

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    url = 'https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx'
    file_path = os.path.join(script_dir, 'dataset_world_health_stat_2022.xlsx')
    if not os.path.exists(file_path):
        urllib.request.urlretrieve(url, file_path)

    df = pd.read_excel(file_path, sheet_name='Annex 2-3', header=None)
    data = df.iloc[5:].copy()
    # Col 0 = Country, Col 10 = Doctor density, Col 11 = Nurse density
    data = data[[0, 10, 11]]
    data.columns = ['Country', 'Doctors', 'Nurses']
    data['Doctors'] = pd.to_numeric(data['Doctors'], errors='coerce')
    data['Nurses']  = pd.to_numeric(data['Nurses'],  errors='coerce')
    data = data.dropna()
    data['ShortName'] = data['Country'].apply(get_shortname)
    data['Highlight'] = data['ShortName'].isin(highlight_countries)

    # Sort by doctor density for clean ordering
    plot_data = data[data['Highlight']].copy().sort_values('Doctors', ascending=True).reset_index(drop=True)
    plot_data['y'] = range(len(plot_data))

    fig, ax = plt.subplots(figsize=(13, 9))
    fig.patch.set_facecolor(PALETTE['background'])
    ax.set_facecolor(PALETTE['background'])
    ax.grid(True, axis='x', color=PALETTE['grid'], linewidth=0.8, linestyle='--', alpha=0.9)
    ax.set_axisbelow(True)

    for _, row in plot_data.iterrows():
        is_bd = row['ShortName'] == 'Bangladesh'
        lcolor = PALETTE['line_bd'] if is_bd else PALETTE['line_default']
        lw = 2.5 if is_bd else 1.5

        # Connecting line
        ax.plot(
            [row['Doctors'], row['Nurses']],
            [row['y'], row['y']],
            color=lcolor, linewidth=lw, zorder=1, alpha=0.8
        )

        # Doctor dot (left/smaller usually)
        ax.scatter(row['Doctors'], row['y'],
                   color=PALETTE['dot_doctor'], s=120,
                   edgecolor='white', linewidths=1.2, zorder=3)

        # Nurse dot
        ax.scatter(row['Nurses'], row['y'],
                   color=PALETTE['dot_nurse'], s=120,
                   edgecolor='white', linewidths=1.2, zorder=3)

        # Labels
        fcolor  = PALETTE['label_bd'] if is_bd else PALETTE['label_hl']
        fweight = 'bold' if is_bd else 'semibold'

        # Gap check for stacking labels vertically if they are too close
        dist = abs(row['Doctors'] - row['Nurses'])
        stack = dist < 7.0 # threshold for stacking

        # Doctor label
        ax.text(row['Doctors'] - (0 if stack else 1.5), 
                row['y'] + (0.28 if stack else 0), 
                f"{row['Doctors']:.1f}",
                ha='center' if stack else 'right', va='center', fontsize=8.5,
                color=fcolor, fontweight=fweight,
                path_effects=[pe.withStroke(linewidth=2, foreground='white')])

        # Nurse label
        ax.text(row['Nurses'] + (0 if stack else 1.5), 
                row['y'] - (0.28 if stack else 0), 
                f"{row['Nurses']:.1f}",
                ha='center' if stack else 'left', va='center', fontsize=8.5,
                color=fcolor, fontweight=fweight,
                path_effects=[pe.withStroke(linewidth=2, foreground='white')])

    # Y axis country labels
    ax.set_yticks(plot_data['y'])
    ax.set_yticklabels(plot_data['ShortName'], fontsize=11)
    # Bold Bangladesh manually
    for label, (_, row) in zip(ax.get_yticklabels(), plot_data.iterrows()):
        if row['ShortName'] == 'Bangladesh':
            label.set_color(PALETTE['label_bd'])
            label.set_fontweight('bold')
        else:
            label.set_color(PALETTE['label_hl'])

    ax.set_xlabel('Density per 10,000 population', fontsize=13,
                  fontweight='bold', color=PALETTE['axis'], labelpad=10)
    ax.tick_params(colors=PALETTE['axis'], labelsize=11)
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE['grid'])

    # Legend
    legend_elements = [
        mlines.Line2D([0], [0], marker='o', color='w',
                      markerfacecolor=PALETTE['dot_doctor'], markersize=10,
                      label='Medical Doctors', markeredgecolor='white'),
        mlines.Line2D([0], [0], marker='o', color='w',
                      markerfacecolor=PALETTE['dot_nurse'], markersize=10,
                      label='Nurses & Midwives', markeredgecolor='white'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True,
              framealpha=0.85, edgecolor=PALETTE['grid'], fontsize=10,
              labelcolor=PALETTE['axis'], facecolor=PALETTE['background'])

    fig.text(0.13, 0.975, 'Healthcare Workforce Gap: Doctors vs Nurses',
             fontsize=17, fontweight='bold', color=PALETTE['title'], va='top')
    fig.text(0.13, 0.950,
             'WHO World Health Statistics 2022  ·  Density per 10,000 population',
             fontsize=10, color=PALETTE['axis'], va='top', alpha=0.75)
    fig.text(0.98, 0.015, '#30DayChartChallenge',
             ha='right', fontsize=9, color='#AAAAAA')

    plt.tight_layout(rect=[0, 0.02, 1, 0.97])
    output_path = os.path.join(script_dir, 'day_4_python.png')
    plt.savefig(output_path, dpi=300, facecolor=PALETTE['background'], bbox_inches='tight')
    print(f"Saved → {output_path}")

if __name__ == '__main__':
    main()