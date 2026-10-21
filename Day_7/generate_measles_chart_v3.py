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
cases_bd = cases_df[cases_df['Country / Region'] == 'Bangladesh'].copy()

# Melt to get year and cases for the historical years 2000 to 2024
years = [y for y in range(2000, 2025)]
cases_melt = cases_bd.melt(id_vars=['Country / Region'], value_vars=years, var_name='Year', value_name='Cases')
cases_melt['Cases'] = cases_melt['Cases'].replace({',': ''}, regex=True).astype(float)
cases_melt = cases_melt.sort_values('Year')

# Append the manual crisis data for 2025 and 2026
new_cases = pd.DataFrame({
    'Country / Region': ['Bangladesh', 'Bangladesh'],
    'Year': [2025, 2026],
    'Cases': [125, 8534] # From DGHS / MoH
})
cases_melt = pd.concat([cases_melt, new_cases], ignore_index=True)

# 2. Process Coverage Data
cov_bd = cov_df[(cov_df['Country / Region'] == 'Bangladesh') & (cov_df['Category'] == 'WUENIC')].copy()

mcv1 = cov_bd[cov_bd['Disease / Antigen'] == 'Measles-containing vaccine, 1st dose']
mcv2 = cov_bd[cov_bd['Disease / Antigen'] == 'Measles-containing vaccine, 2nd dose']

mcv1_melt = mcv1.melt(id_vars=['Country / Region'], value_vars=years, var_name='Year', value_name='MCV1')
mcv1_melt['MCV1'] = mcv1_melt['MCV1'].astype(str).str.replace('%', '', regex=False).replace('nan', np.nan).astype(float)

mcv2_melt = mcv2.melt(id_vars=['Country / Region'], value_vars=years, var_name='Year', value_name='MCV2')
mcv2_melt['MCV2'] = mcv2_melt['MCV2'].astype(str).str.replace('%', '', regex=False).replace('nan', np.nan).astype(float)

cov_merged = pd.merge(mcv1_melt[['Year', 'MCV1']], mcv2_melt[['Year', 'MCV2']], on='Year')

# Append 2025 crisis coverage data (59.6% based on news)
new_cov = pd.DataFrame({
    'Year': [2025, 2026],
    'MCV1': [59.6, np.nan], 
    'MCV2': [59.6, np.nan]
})
cov_merged = pd.concat([cov_merged, new_cov], ignore_index=True)
cov_merged = cov_merged.sort_values('Year')

# 3. Plotting the Chart
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), sharex=True)

# Top Plot: Coverage
ax1.plot(cov_merged['Year'], cov_merged['MCV1'], marker='o', label='MCV1 Coverage', color='#1f77b4')
ax1.plot(cov_merged['Year'], cov_merged['MCV2'], marker='s', label='MCV2 Coverage', color='#ff7f0e')
ax1.axhline(y=95, color='#d62728', linestyle='--', label='Herd Immunity Threshold (~95%)')

# Highlight the custom data period denoting Ministry of Health reporting vs WHO
ax1.axvspan(2024.5, 2026.5, color='gray', alpha=0.15, label='MoH / News Reports (2025-2026)')
ax1.annotate('Coverage Plummets\nto 59.6%', xy=(2025, 59.6), xytext=(2019, 65),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6))

ax1.set_ylabel('Vaccination Coverage (%)')
ax1.set_title('The Story of Measles in Bangladesh')
ax1.legend(loc='lower left')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(bottom=40, top=105)

# Bottom Plot: Cases
# Separate the 2026 bar to color it differently
ax2.bar(cases_melt['Year'][:-2], cases_melt['Cases'][:-2], color='#d62728', alpha=0.8, label='WHO Reported Measles Cases')
# 2025 bar is also MoH, but let's just color it standard since it's confirmed
ax2.bar(cases_melt['Year'].iloc[-2:-1], cases_melt['Cases'].iloc[-2:-1], color='#d62728', alpha=0.8) 
# Add the 2026 bar with a distinct look (suspected)
ax2.bar(cases_melt['Year'].iloc[-1:], cases_melt['Cases'].iloc[-1:], color='darkred', alpha=0.9, hatch='//', label='MoH Suspected Outbreak Cases (2026)')

ax2.axvspan(2024.5, 2026.5, color='gray', alpha=0.15)
ax2.annotate('Massive Outbreak\n(8,534 Suspected cases)', xy=(2026, 8534), xytext=(2014, 7000),
             arrowprops=dict(facecolor='darkred', shrink=0.05, width=2, headwidth=8), color='darkred', weight='bold')

ax2.set_xlabel('Year')
ax2.set_ylabel('Number of Cases')

# Fix fractional years on the x-axis
ax2.set_xticks([y for y in range(2000, 2027, 2)])

ax2.legend(loc='upper center')
ax2.grid(True, alpha=0.3)

# Add overarching source text
plt.figtext(0.5, 0.02, 'Source: 2000-2024 WHO Immunization Portal | 2025-2026 Ministry of Health / IFRC & News Reports', 
            ha='center', fontsize=10, style='italic', color='dimgrey')

plt.subplots_adjust(bottom=0.08) # Make room for footer text
plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig('measles_real_data_chart_v3.png', dpi=300)
print("Chart generated and saved as 'measles_real_data_chart_v3.png'")
