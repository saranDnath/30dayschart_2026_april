from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import urllib.request, sys
np.random.seed(42)

LOCAL_FB = Path(__file__).parent / "WID_Data_10042026-163159.xlsx"
WID_URL  = "https://wid.world/www-site/generated-files/exports/WID_Data_10042026-163159.xlsx"

# ── 1. LOAD DATA ──────────────────────────────────────────────
def load_wid(url, local):
    try:
        tmp = Path(__file__).parent / "_tmp.xlsx"
        urllib.request.urlretrieve(url, tmp); return tmp
    except: pass
    if local.exists(): return local
    sys.exit("No data file found.")

xlsx   = load_wid(WID_URL, LOCAL_FB)
df_raw = pd.read_excel(xlsx, sheet_name="Data", header=0)
cols   = df_raw.columns.tolist()
col_map = {}
for i, c in enumerate(cols[2:], start=2):
    parts = str(c).split('\n')
    if len(parts) >= 4:
        col_map[i] = (parts[0].replace('shweal_z_','').strip(),
                      parts[3].strip(), cols[i])
df_idx = df_raw.set_index(df_raw.columns[0])

records = []
for i, (code, name, col) in col_map.items():
    if any(code.startswith(p) for p in ['Q','OE','OJ','OA','OB','OC','OD','OI',
                                         'OH','OL','OK','XB','XF','XL','XN','XR','XS','WO']):
        continue
    try:
        p0p50   = float(df_idx.loc['p0p50',   col] or 0)
        p90p100 = float(df_idx.loc['p90p100', col] or 0)
        p99p100 = float(df_idx.loc['p99p100', col] or 0)
        if p99p100 > 0 and p90p100 > 0:
            records.append({'code':code,'country':name,
                            'bot50':p0p50,
                            'mid40':max(0,1-p90p100-p0p50),
                            'next9':max(0,p90p100-p99p100),
                            'top1': p99p100})
    except: pass
data = pd.DataFrame(records)

# ── 2. REGION MAP & COLORS ────────────────────────────────────
REGIONS = {
    'SAARC':             ['BD','IN','PK','LK','NP','AF','BT','MV'],
    'MENA':              ['IQ','YE','BH','OM','LB','TN','SA','EG','AE','DZ','JO','MA','LY','IR','KW'],
    'Sub-Saharan Africa':['ZA','ZW','MZ','AO','ZM','CD','UG','TZ','NG','GH','KE','ET'],
    'North America':     ['MX','US','CA'],
    'Latin America':     ['UY','CL','BR','CO','PE','VE','BO','AR','EC'],
    'Western Europe':    ['CH','AT','DE','FR','SE','PT','ES','NO','IE','IT','GB','DK','FI','BE','NL'],
    'Eastern Europe':    ['RU','GE','HU','PL','CZ','BG','RO','UA','SK'],
    'East Asia':         ['HK','CN','TW','KR','JP','MN'],
    'SE Asia':           ['TH','SG','PH','MY','KH','VN','MM','ID'],
    'Oceania':           ['FJ','PG','AU','NZ'],
}
REG_COLORS = {
    'SAARC':             '#F97316',
    'MENA':              '#CA8A04',
    'Sub-Saharan Africa':'#16A34A',
    'North America':     '#2563EB',
    'Latin America':     '#0891B2',
    'Western Europe':    '#7C3AED',
    'Eastern Europe':    '#DB2777',
    'East Asia':         '#DC2626',
    'SE Asia':           '#E879A0',
    'Oceania':           '#0D9488',
}

# ── 3. COMPUTE REGIONAL AVERAGES ─────────────────────────────
def region_avg(codes):
    rdf = data[data['code'].isin(codes)].copy()
    rdf['bot50'] = rdf['bot50'].clip(lower=0)
    # Normalise so tiers sum exactly to 1
    tot = rdf[['bot50','mid40','next9','top1']].sum(axis=1)
    for c in ['bot50','mid40','next9','top1']:
        rdf[c] = rdf[c] / tot
    return {
        'bot50': rdf['bot50'].mean(),
        'mid40': rdf['mid40'].mean(),
        'next9': rdf['next9'].mean(),
        'top1':  rdf['top1'].mean(),
    }

reg_avgs = {reg: region_avg(codes) for reg, codes in REGIONS.items()}

# World (PPP) direct from WID
WORLD = {'bot50':0.0225, 'mid40':0.2396, 'next9':0.3735, 'top1':0.3644}

# Bangladesh
bd_row = data[data['code']=='BD'].iloc[0]
BANGLADESH = {
    'bot50': max(0, bd_row['bot50']),
    'mid40': bd_row['mid40'],
    'next9': bd_row['next9'],
    'top1':  bd_row['top1'],
}

# SAARC average (already computed above)
SAARC_AVG = reg_avgs['SAARC']

# ── SHARED STYLE ──────────────────────────────────────────────
BG     = '#FAFAF9'
C_BOT  = '#E0E7FF'
C_MID  = '#93C5FD'
C_NEXT = '#3B82F6'
FS_LBL = 9.5
BAR_H  = 0.55

TIERS    = ['bot50','mid40','next9','top1']
TIER_LBL = ['Bottom 50%','Middle 40%','Next 9%','Top 1%']
TIER_C   = [C_BOT, C_MID, C_NEXT, None]   # None = region/accent color

def draw_fingerprint_bar(ax, y, d, accent, bar_h=BAR_H, label_left=None,
                          show_pct=True, label_fs=FS_LBL,
                          label_color='#1C1917', label_fw='normal',
                          highlight=False):
    """Draw one stacked bar at position y."""
    left = 0
    colors = [C_BOT, C_MID, C_NEXT, accent]
    for tier, color in zip(TIERS, colors):
        val = d[tier]
        ax.barh(y, val, bar_h, left=left, color=color,
                linewidth=0.4, edgecolor='white', zorder=3)
        # Value label inside bar (only if wide enough)
        if val > 0.07:
            ax.text(left + val/2, y, f"{val:.0%}",
                    color='white' if color not in [C_BOT] else '#374151',
                    fontsize=6.8, va='center', ha='center',
                    fontweight='bold', zorder=5)
        left += val

    # Country/region label on left
    if label_left:
        ax.text(-0.012, y, label_left,
                color=label_color, fontsize=label_fs,
                fontweight=label_fw, va='center', ha='right', zorder=6)

    # Top1% callout on right
    if show_pct:
        fc = label_color if highlight else accent
        ax.text(1.008, y, f"Top 1% = {d['top1']:.1%}",
                color=fc, fontsize=7.0, fontweight='bold' if highlight else 'normal',
                va='center', ha='left', zorder=6)

def style_ax(ax, n_bars, title, title_color, subtitle=None):
    ax.set_xlim(-0.30, 1.28)
    ax.set_ylim(-0.8, n_bars - 0.2)
    ax.set_yticks([])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(['0%','25%','50%','75%','100%'],
                       color='#9CA3AF', fontsize=7.5)
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    for xv in [0.25, 0.5, 0.75, 1.0]:
        ax.axvline(xv, color='#F3F4F6', lw=0.8, zorder=1)
    ax.set_title(title, color=title_color, fontsize=13,
                 fontweight='bold', pad=9, loc='left')
    if subtitle:
        ax.text(0, n_bars - 0.05, subtitle,
                color='#9CA3AF', fontsize=7.5,
                va='bottom', ha='left', transform=ax.transData)

def global_legend(fig):
    patches = [
        mpatches.Patch(color=C_BOT,   label='Bottom 50%'),
        mpatches.Patch(color=C_MID,   label='Middle 40%'),
        mpatches.Patch(color=C_NEXT,  label='Next 9%'),
        mpatches.Patch(color='#6B7280',label='Top 1%  (bar color = region / subject)'),
    ]
    fig.legend(handles=patches, loc='lower center', ncol=4,
               fontsize=9.5, frameon=True, facecolor='white',
               edgecolor='#E5E7EB', labelcolor='#374151',
               framealpha=0.97, handlelength=1.4,
               handletextpad=0.5, columnspacing=1.5,
               bbox_to_anchor=(0.5, 0.05))

# ════════════════════════════════════════════════════════════
# CHART 2 — Regional Fingerprints (one bar per region)
# ════════════════════════════════════════════════════════════
reg_order = [
    'Sub-Saharan Africa','Latin America','North America','MENA',
    'Eastern Europe','East Asia','SE Asia','SAARC','Oceania','Western Europe'
]   # sorted roughly high→low top1

fig2, ax2 = plt.subplots(figsize=(13, 8))
fig2.patch.set_facecolor(BG)
ax2.set_facecolor(BG)

n = len(reg_order)
for i, reg in enumerate(reg_order):
    y   = n - 1 - i     # top = most unequal
    d   = reg_avgs[reg]
    rc  = REG_COLORS[reg]
    draw_fingerprint_bar(ax2, y, d, accent=rc,
                         label_left=reg, label_fs=10,
                         label_color=rc, label_fw='bold')

style_ax(ax2, n,
         title='Regional Wealth Fingerprints',
         title_color='#1C1917',
         subtitle='Each bar = regional average across all countries in that group  ·  sorted by Top 1% share (high → low)')

# World average reference line
ax2.axvline(WORLD['top1'] + WORLD['next9'] + WORLD['mid40'],
            ymin=0, ymax=1, color='#F59E0B',
            lw=1.3, ls='--', alpha=0.7, zorder=2)
ax2.text(1.0 + 0.002, -0.5,
         f"World Top 1%+\nnext 9% = {(WORLD['top1']+WORLD['next9']):.0%}",
         color='#D97706', fontsize=7, va='top',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFBEB',
                   edgecolor='#F59E0B', lw=0.8, alpha=0.95))

global_legend(fig2)

fig2.text(0.5, 0.97,
          'Regional Wealth Fingerprints — Average Distribution per Region',
          color='#1C1917', fontsize=17, fontweight='bold',
          fontfamily='DejaVu Serif', ha='center', va='top')
fig2.text(0.5, 0.952,
          'Average Top 1%, Next 9%, Middle 40%, Bottom 50% wealth share by region  ·  WID.world 2024',
          color='#6B7280', fontsize=9.5, ha='center', va='top')
fig2.text(0.5, 0.012,
          'Data: WID.world · Net personal wealth share (shweal992j), 2024  |  '
          '#30DayChartChallenge April 2026 · Day 09: Distributions — Wealth  |  #DataViz #Python',
          color='#9CA3AF', fontsize=7.8, ha='center', va='bottom')

plt.tight_layout(rect=[0, 0.10, 1, 0.945])
out2 = Path(__file__).parent / "day_09_chart2_regions.png"
fig2.savefig(out2, dpi=300, bbox_inches='tight', facecolor=BG, edgecolor='none')
print(f"✅ Chart 2 saved: {out2}")

# ════════════════════════════════════════════════════════════
# CHART 3 — Global vs SAARC vs Bangladesh
# ════════════════════════════════════════════════════════════
SUBJECTS = [
    # (label, data_dict, accent_color, is_highlight, subtitle_note)
    ('World Average',   WORLD,       '#6B7280', False, 'All countries · WID.world PPP 2024'),
    ('SAARC Average',   SAARC_AVG,   '#F97316', False, 'Average of 8 SAARC member states'),
    ('Bangladesh',      BANGLADESH,  '#CC2200', True,  'Net personal wealth share · WID.world 2024'),
]

fig3, ax3 = plt.subplots(figsize=(13, 5.5))
fig3.patch.set_facecolor(BG)
ax3.set_facecolor(BG)

n3 = len(SUBJECTS)
for i, (label, d, accent, highlight, note) in enumerate(SUBJECTS):
    y  = n3 - 1 - i
    fw = 'bold' if highlight else 'bold'
    fc = accent
    draw_fingerprint_bar(ax3, y, d, accent=accent,
                         bar_h=0.62,
                         label_left=label,
                         label_fs=11.5,
                         label_color=fc,
                         label_fw='bold',
                         highlight=highlight,
                         show_pct=True)
    # Subtitle note below label
    ax3.text(-0.012, y - 0.28, note,
             color='#9CA3AF', fontsize=7.2,
             va='center', ha='right', zorder=6)

# Divider lines between bars
for yy in [0.5, 1.5]:
    ax3.axhline(yy, color='#E5E7EB', lw=0.8, zorder=1)

style_ax(ax3, n3,
         title='Bangladesh in Context',
         title_color='#CC2200')

# Annotate the gap story
# Arrow: Bangladesh top1 vs World top1
bd_top1_x = 1 - BANGLADESH['top1']   # left edge of top1 segment
w_top1_x  = 1 - WORLD['top1']
ax3.annotate('',
    xy=(1 - WORLD['top1'],      2.55),
    xytext=(1 - BANGLADESH['top1'], 2.55),
    arrowprops=dict(arrowstyle='<->', color='#6B7280', lw=1.2))
ax3.text((bd_top1_x + w_top1_x)/2, 2.72,
         f"Δ Top 1%: {WORLD['top1']-BANGLADESH['top1']:.1%}\n(World richer by this)",
         color='#6B7280', fontsize=7.5, ha='center', va='bottom')

global_legend(fig3)

fig3.text(0.5, 0.97,
          'Bangladesh vs SAARC Average vs World — Wealth Distribution',
          color='#1C1917', fontsize=17, fontweight='bold',
          fontfamily='DejaVu Serif', ha='center', va='top')
fig3.text(0.5, 0.925,
          'How does Bangladesh\'s wealth distribution compare to its region and the world?  ·  WID.world 2024',
          color='#6B7280', fontsize=9.5, ha='center', va='top')
fig3.text(0.5, 0.012,
          'Data: WID.world · Net personal wealth share (shweal992j), 2024  |  '
          '#30DayChartChallenge April 2026 · Day 09: Distributions — Wealth  |  #DataViz #Python',
          color='#9CA3AF', fontsize=7.8, ha='center', va='bottom')

plt.tight_layout(rect=[0, 0.10, 1, 0.935])
out3 = Path(__file__).parent / "day_09_chart3_bd_context.png"
fig3.savefig(out3, dpi=300, bbox_inches='tight', facecolor=BG, edgecolor='none')
print(f"✅ Chart 3 saved: {out3}")