import os
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

highlight_countries = ['Bangladesh', 'India', 'Pakistan', 'Sri Lanka', 'Nepal', 'Bhutan', 'Maldives', 'Afghanistan', 'China', 'United Kingdom', 'United States', 'Mexico', 'Brazil', 'South Africa', 'Nigeria', 'Australia', 'Japan', 'Germany', 'Canada', 'Italy', 'France', 'Ghana', 'Egypt', 'Ethiopia', 'Indonesia', 'Kenya', 'Malaysia', 'Myanmar', 'Philippines', 'Thailand', 'Vietnam']

PALETTE = {
    'background':   '#F7F3EE', 'grid': '#E0D9D0', 'bar_overweight': '#E07A5F', 'bar_stunting': '#3D5A80',
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
    data = data[[0, 1, 5]]
    data.columns = ['Country', 'Stunting', 'overweight']
    data['Stunting'] = pd.to_numeric(data['Stunting'], errors='coerce')
    data['overweight'] = pd.to_numeric(data['overweight'], errors='coerce')
    data = data.dropna()
    data['ShortName'] = data['Country'].apply(get_shortname)
    data['Highlight'] = data['ShortName'].isin(highlight_countries)
    data = data[data['Highlight']].sort_values('Stunting', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(PALETTE['background'])
    ax.set_facecolor(PALETTE['background'])
    ax.grid(True, axis='x', color=PALETTE['grid'], linewidth=0.8, linestyle='--', alpha=0.9)
    ax.set_axisbelow(True)

    bars_o = ax.barh(data['ShortName'], -data['overweight'], color=PALETTE['bar_overweight'], label='Overweight', edgecolor='white', linewidth=1)
    bars_s = ax.barh(data['ShortName'], data['Stunting'], color=PALETTE['bar_stunting'], label='Stunting', edgecolor='white', linewidth=1)
    ax.axvline(0, color=PALETTE['axis'], linewidth=1.5)

    for bar in bars_o:
        ax.text(bar.get_width() - 0.5, bar.get_y() + bar.get_height()/2, f"{-bar.get_width():.1f}%", ha='right', va='center', fontsize=9, color=PALETTE['label_hl'])
    for bar in bars_s:
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.1f}%", ha='left', va='center', fontsize=9, color=PALETTE['label_hl'])

    max_val = max(data['Stunting'].max(), data['overweight'].max())
    ax.set_xlim(-max_val - 15, max_val + 10)

    ax.set_xticks([])
    for spine in ax.spines.values(): spine.set_visible(False)
    
    ax.tick_params(axis='y', pad=10)

    for label in ax.get_yticklabels():
        if label.get_text() == 'Bangladesh':
            label.set_color(PALETTE['label_bd'])
            label.set_weight('bold')
        else: label.set_color(PALETTE['label_hl'])

    fig.text(0.1, 0.95, 'Childhood Malnutrition: Overweight vs Stunting', fontsize=17, fontweight='bold', color=PALETTE['title'], va='top')
    fig.text(0.1, 0.92, 'WHO World Health Statistics 2022  ·  % Under-5s', fontsize=10, color=PALETTE['title'], va='top', alpha=0.75)
    ax.legend(loc='lower right', frameon=True, facecolor=PALETTE['background'], edgecolor=PALETTE['grid'])
    fig.text(0.98, 0.015, '#30DayChartChallenge', ha='right', fontsize=9, color='#AAAAAA')
    plt.tight_layout(rect=[0, 0.02, 1, 0.90])
    plt.savefig(os.path.join(script_dir, 'day_3_python.png'), dpi=300, facecolor=PALETTE['background'], bbox_inches='tight')

if __name__ == '__main__': main()
