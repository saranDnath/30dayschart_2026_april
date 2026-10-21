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

# Melt to get year and cases for the historical years 2010 to 2024
years = [y for y in range(2010, 2025)]
cases_melt = cases_bd.melt(id_vars=['Country / Region'], value_vars=years, var_name='Year', value_name='Cases')
cases_melt['Cases'] = cases_melt['Cases'].replace({',': ''}, regex=True).astype(float)
cases_melt = cases_melt.sort_values('Year')

# Append the manual crisis data for 2025 and 2026
new_cases = pd.DataFrame({
    'Country / Region': ['Bangladesh', 'Bangladesh'],
    'Year': [2025, 2026],
    'Cases': [125, 8534] # 8,534 suspected cases from the DGHS reports
})
cases_melt = pd.concat([cases_melt, new_cases], ignore_index=True)

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

# Append 2025 crisis coverage data (roughly 57%) 
new_cov = pd.DataFrame({
    'Year': [2025, 2026],
    'MCV1': [57, np.nan], # No finalized coverage data for 2026 yet
    'MCV2': [57, np.nan]
})
cov_merged = pd.concat([cov_merged, new_cov], ignore_index=True)
cov_merged = cov_merged.sort_values('Year')

# 3. Plotting the Chart
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Top Plot: Coverage
ax1.plot(cov_merged['Year'], cov_merged['MCV1'], marker='o', label='MCV1 Coverage', color='#1f77b4')
ax1.plot(cov_merged['Year'], cov_merged['MCV2'], marker='s', label='MCV2 Coverage', color='#ff7f0e')
ax1.axhline(y=95, color='#d62728', linestyle='--', label='Herd Immunity Threshold (~95%)')

# Highlight the Unrest Period
ax1.axvspan(2024, 2026, color='gray', alpha=0.15, label='Political Unrest / Crisis')
ax1.annotate('Coverage Plummets\nto ~57%', xy=(2025, 57), xytext=(2022, 65),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6))

ax1.set_ylabel('Vaccination Coverage (%)')
ax1.set_title('The Story of Measles in Bangladesh: When Coverage Drops, Outbreaks Surge')
# Moved legend to lower left to avoid the new datamark on the right
ax1.legend(loc='lower left')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(bottom=40, top=105)

# Bottom Plot: Cases
# Separate the 2026 bar to color it differently
ax2.bar(cases_melt['Year'][:-1], cases_melt['Cases'][:-1], color='#d62728', alpha=0.8, label='Reported Measles Cases')
# Add the 2026 bar with a distinct look since it's "suspected cases" mixed with confirmed
ax2.bar(cases_melt['Year'].iloc[-1:], cases_melt['Cases'].iloc[-1:], color='darkred', alpha=0.9, hatch='//', label='Suspected Outbreak Cases (2026)')

ax2.axvspan(2024, 2026, color='gray', alpha=0.15)
ax2.annotate('Massive Outbreak\n(8,534 Suspected cases)', xy=(2026, 8534), xytext=(2019, 7000),
             arrowprops=dict(facecolor='darkred', shrink=0.05, width=2, headwidth=8), color='darkred', weight='bold')

ax2.set_xlabel('Year')
ax2.set_ylabel('Number of Cases')
# Placed legend on upper left because 2026 bar fills up the upper right
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('measles_real_data_chart_v2.png', dpi=300)
print("Chart generated and saved as 'measles_real_data_chart_v2.png'")
