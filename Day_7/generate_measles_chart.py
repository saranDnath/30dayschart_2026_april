import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# File paths
cases_file = 'Measles reported cases and incidence 2026-05-04 05-46 UTC.xlsx'
coverage_file = 'vaccine_coverage.xlsx'

# Load data
cases_df = pd.read_excel(cases_file)
cov_df = pd.read_excel(coverage_file)

# 1. Process Cases Data
# Filter for Bangladesh
cases_bd = cases_df[cases_df['Country / Region'] == 'Bangladesh'].copy()

# Melt to get year and cases for the years 2010 to 2024
years = [y for y in range(2000, 2025)]
cases_melt = cases_bd.melt(id_vars=['Country / Region'], value_vars=years, var_name='Year', value_name='Cases')
# Clean cases data (remove commas, handle NaNs)
cases_melt['Cases'] = cases_melt['Cases'].replace({',': ''}, regex=True).astype(float)
cases_melt = cases_melt.sort_values('Year')

# 2. Process Coverage Data
# Filter for Bangladesh and the WUENIC estimate category
cov_bd = cov_df[(cov_df['Country / Region'] == 'Bangladesh') & (cov_df['Category'] == 'WUENIC')].copy()

# Filter for the specific antigens
mcv1 = cov_bd[cov_bd['Disease / Antigen'] == 'Measles-containing vaccine, 1st dose']
mcv2 = cov_bd[cov_bd['Disease / Antigen'] == 'Measles-containing vaccine, 2nd dose']

# Process MCV1
mcv1_melt = mcv1.melt(id_vars=['Country / Region'], value_vars=years, var_name='Year', value_name='MCV1')
mcv1_melt['MCV1'] = mcv1_melt['MCV1'].astype(str).str.replace('%', '', regex=False).replace('nan', np.nan).astype(float)

# Process MCV2
mcv2_melt = mcv2.melt(id_vars=['Country / Region'], value_vars=years, var_name='Year', value_name='MCV2')
mcv2_melt['MCV2'] = mcv2_melt['MCV2'].astype(str).str.replace('%', '', regex=False).replace('nan', np.nan).astype(float)

# Merge coverage together
cov_merged = pd.merge(mcv1_melt[['Year', 'MCV1']], mcv2_melt[['Year', 'MCV2']], on='Year')
cov_merged = cov_merged.sort_values('Year')

# 3. Plotting the Chart
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Top Plot: Coverage
ax1.plot(cov_merged['Year'], cov_merged['MCV1'], marker='o', label='MCV1 Coverage', color='#1f77b4')
ax1.plot(cov_merged['Year'], cov_merged['MCV2'], marker='s', label='MCV2 Coverage', color='#ff7f0e')
ax1.axhline(y=95, color='#d62728', linestyle='--', label='Herd Immunity Threshold (~95%)')

ax1.set_ylabel('Vaccination Coverage (%)')
ax1.set_title('The Story of Measles in Bangladesh')
ax1.legend(loc='lower right')
ax1.grid(True, alpha=0.3)
# Set y-limits just to match typical aesthetics (e.g., 80 to 100 if appropriate)
ax1.set_ylim(bottom=max(50, cov_merged[['MCV1', 'MCV2']].min().min() - 5), top=100)

# Bottom Plot: Cases
ax2.bar(cases_melt['Year'], cases_melt['Cases'], color='#d62728', alpha=0.8, label='Reported Measles Cases')
ax2.set_xlabel('Year')
ax2.set_ylabel('Number of Cases')
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('measles_real_data_chart.png', dpi=300)
print("Chart generated and saved as 'measles_real_data_chart.png'")
