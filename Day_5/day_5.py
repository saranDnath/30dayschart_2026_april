import os
import urllib.request
import pandas as pd
import geopandas as gpd
import geodatasets
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm
import numpy as np

# ── What to map — change these to switch indicators ──────────────────────────
INDICATOR_SHEET  = 'Annex 2-1'
INDICATOR_COL    = 16          # column index (0-based after slicing)
INDICATOR_LABEL  = 'Tuberculosis incidence (per 100 000 population)'
INDICATOR_SHORT  = 'Tuberculosis'
OUTPUT_FILE      = 'day_5_tuberculosis_map.png'
# ─────────────────────────────────────────────────────────────────────────────

PALETTE = {
    'background': '#F7F3EE',
    'title':      '#1A1A2E',
    'axis':       '#4A4A5A',
    'missing':    '#D6D0C8',
    'bd_edge':    '#000000',
}

# Color ramp: light cream → deep teal
CMAP = LinearSegmentedColormap.from_list(
    'stunting', ['#FEF0D9', '#FDD49E', '#FC8D59', '#D7301F', '#7F0000'], N=256
)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ── 1. Download WHO dataset ───────────────────────────────────────────────
    url = 'https://datasafe-h5afbhf4gwctabaa.z01.azurefd.net/api/Download/STR/BE2BEEE/2022-05-21/be2beee_20220520_0.xlsx'
    file_path = os.path.join(script_dir, 'dataset_world_health_stat_2022.xlsx')
    if not os.path.exists(file_path):
        print("Downloading WHO dataset...")
        urllib.request.urlretrieve(url, file_path)

    # ── 2. Load indicator ─────────────────────────────────────────────────────
    df = pd.read_excel(file_path, sheet_name=INDICATOR_SHEET, header=None)
    data = df.iloc[5:].copy()
    data = data[[0, INDICATOR_COL]].copy()
    data.columns = ['Country', 'Value']
    # Clean string prefixes like '<1' so they don't become NaN
    data['Value'] = data['Value'].astype(str).str.replace('<', '').str.replace('>', '').str.strip()
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
    data = data.dropna(subset=['Value'])
    data['Country'] = data['Country'].str.strip()

    # ── 3. Download world shapefile (Natural Earth via GeoJSON URL) ───────────
    print("Loading world shapefile...")
    # Using official Natural Earth mirror for administrative boundaries (admin_0)
    world_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    world = gpd.read_file(world_url)

    # ── 4. Merge — fuzzy match on country name ────────────────────────────────
    # Manual overrides for known mismatches
    name_map = {
        'Bolivia': 'Bolivia (Plurinational State of)',
        'Bosnia and Herz.': 'Bosnia and Herzegovina',
        'Brunei': 'Brunei Darussalam',
        'Central African Rep.': 'Central African Republic',
        'Dem. Rep. Congo': 'Democratic Republic of the Congo',
        'Dominican Rep.': 'Dominican Republic',
        'Eq. Guinea': 'Equatorial Guinea',
        'Iran': 'Iran (Islamic Republic of)',
        'Laos': 'Lao People\'s Democratic Republic',
        'Moldova': 'Republic of Moldova',
        'North Korea': 'Democratic People\'s Republic of Korea',
        'Russia': 'Russian Federation',
        'S. Sudan': 'South Sudan',
        'Solomon Is.': 'Solomon Islands',
        'South Korea': 'Republic of Korea',
        'Syria': 'Syrian Arab Republic',
        'Tanzania': 'United Republic of Tanzania',
        'Venezuela': 'Venezuela (Bolivarian Republic of)',
        'Vietnam': 'Viet Nam',
        'eSwatini': 'Eswatini',
        'Côte d\'Ivoire': 'Côte d\'Ivoire',
        'Greenland': 'Denmark',
        'Puerto Rico': 'United States of America',
        'Falkland Is.': 'United Kingdom of Great Britain and Northern Ireland',
        'New Caledonia': 'France',
        'Fr. S. Antarctic Lands': 'France',
        'W. Sahara': 'Morocco',
        'Somaliland': 'Somalia',
        'Kosovo': 'Serbia',
        'N. Cyprus': 'Cyprus',
        'Taiwan': 'China' # sorry but I don't want to start a war
    }
    # Natural Earth GeoJSON uses 'NAME' or 'name' depending on the mirror.
    # We ensure we have a standard 'name' column for the mapping logic below.
    if 'name' not in world.columns and 'NAME' in world.columns:
        world['name'] = world['NAME']

    world['name_lookup'] = world['name'].replace(name_map)
    merged = world.merge(data, left_on='name_lookup', right_on='Country', how='left')

    # ── 5. Plot ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor(PALETTE['background'])
    ax.set_facecolor(PALETTE['background'])

    # Missing countries
    merged[merged['Value'].isna()].plot(
        ax=ax, color=PALETTE['missing'], edgecolor='white', linewidth=0.3
    )

    # Choropleth
    merged[merged['Value'].notna()].plot(
        ax=ax,
        column='Value',
        cmap=CMAP,
        edgecolor='white',
        linewidth=0.3,
        legend=False,
        vmin=0,
        vmax=merged['Value'].max()
    )

    # Highlight Bangladesh with red border
    bd = merged[merged['name_lookup'] == 'Bangladesh']
    if not bd.empty:
        bd.plot(ax=ax, facecolor='none',
                edgecolor=PALETTE['bd_edge'], linewidth=1, zorder=5)
        # Label Bangladesh
        bd_centroid = bd.geometry.centroid.iloc[0]
        ax.annotate(
            'Bangladesh',
            xy=(bd_centroid.x, bd_centroid.y),
            xytext=(20, -30), textcoords='offset points',
            fontsize=9, fontweight='bold', color=PALETTE['bd_edge'],
            path_effects=[pe.withStroke(linewidth=2, foreground='white')],
            arrowprops=dict(arrowstyle='->', color=PALETTE['bd_edge'], lw=1.2),
            zorder=6
        )

    # ── 6. Colorbar ───────────────────────────────────────────────────────────
    sm = cm.ScalarMappable(
        cmap=CMAP,
        norm=plt.Normalize(vmin=0, vmax=merged['Value'].max())
    )
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation='horizontal',
                        fraction=0.03, pad=0.02, aspect=40)
    cbar.set_label(INDICATOR_LABEL, fontsize=10,
                   color=PALETTE['axis'], labelpad=6)
    cbar.ax.tick_params(colors=PALETTE['axis'], labelsize=9)

    # ── 7. Titles & finishing touches ─────────────────────────────────────────
    ax.set_axis_off()
    fig.text(0.13, 0.95, f'Global {INDICATOR_SHORT} Prevalence',
             fontsize=19, fontweight='bold', color=PALETTE['title'], va='top')
    fig.text(0.13, 0.91,
             'WHO World Health Statistics 2022  ·  % children under 5',
             fontsize=10, color=PALETTE['axis'], va='top', alpha=0.75)
    fig.text(0.98, 0.02, '#30DayChartChallenge',
             ha='right', fontsize=9, color='#AAAAAA')

    plt.tight_layout(rect=[0, 0.05, 1, 0.93])
    output_path = os.path.join(script_dir, OUTPUT_FILE)
    plt.savefig(output_path, dpi=300,
                facecolor=PALETTE['background'], bbox_inches='tight')
    print(f"Saved → {output_path}")

if __name__ == '__main__':
    main()