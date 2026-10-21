# ============================================================
# #30DayChartChallenge — Day 08: Circular
# Sugar-Sweetened Beverage Intake (g/day) · GDD 2018
# Grouped Packed Bubble Chart  
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import circlify
import os

# ── 1. Load & filter ────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(script_dir, "sugar_intake_country_wise_2018.csv"))

data = (
    df[
        (df["year"]   == 2018) &
        (df["age"]    == 999)  &
        (df["female"] == 999)  &
        (df["urban"]  == 999)  &
        (df["edu"]    == 999)
    ]
    .copy()
    .reset_index(drop=True)
)
# Clip near-zero values so every country stays visible
data["plot_val"] = data["median"].clip(lower=1.0)

# ── 2. Palette & labels ──────────────────────────────────────
PALETTE = {
    "LAC":   "#E94B35",
    "SSA":   "#F5A623",
    "MENA":  "#9B59B6",
    "Asia":  "#27AE60",
    "HIC":   "#2E86C1",
    "FSU":   "#17A589",
    "SAARC": "#E67E22",
}
REGION_LABELS = {
    "LAC":   "Latin America & Caribbean",
    "SSA":   "Sub-Saharan Africa",
    "MENA":  "Middle East & N. Africa",
    "Asia":  "East & SE Asia",
    "HIC":   "High-Income Countries",
    "FSU":   "Former Soviet Union",
    "SAARC": "South Asia",
}

BG = "#0D1B2A"

# iso3 → region lookup (used when drawing level-2 circles)
iso_region = dict(zip(data["iso3"], data["superregion2"]))

# ── 3. Build hierarchical input ──────────────────────────────
# Sort regions by total intake so the two largest clusters
# (SSA and LAC) end up placed centrally by the packer
region_order = (
    data.groupby("superregion2")["plot_val"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)

hier = []
for region in region_order:
    grp = data[data["superregion2"] == region].sort_values("plot_val", ascending=False)
    children = [{"id": r["iso3"], "datum": r["plot_val"]} for _, r in grp.iterrows()]
    hier.append({
        "id":       region,
        "datum":    sum(c["datum"] for c in children),
        "children": children,
    })

# ── 4. Pack circles ──────────────────────────────────────────
# show_enclosure=False → no outer bounding circle drawn
circles = circlify.circlify(hier, show_enclosure=False)
# level 1 = regional cluster envelopes
# level 2 = individual country circles

# ── 5. Canvas ────────────────────────────────────────────────
S   = 490      # scale factor: circlify unit coords → plot units
PAD = 1.09     # axis padding around the packed layout

fig = plt.figure(figsize=(13, 14.5), facecolor=BG)
ax  = fig.add_axes([0.02, 0.09, 0.96, 0.84])
ax.set_facecolor(BG)
ax.set_aspect("equal")
ax.axis("off")

# ── 6. Draw circles ──────────────────────────────────────────
for c in circles:
    cx, cy, r = c.x * S, c.y * S, c.r * S
    col = PALETTE.get(c.ex["id"] if c.level == 1 else iso_region.get(c.ex["id"], "HIC"), "#888")

    if c.level == 1:
        # Soft tinted cluster background
        ax.add_patch(plt.Circle((cx, cy), r, color=col, alpha=0.10, linewidth=0, zorder=1))
        # Dashed cluster border
        ax.add_patch(plt.Circle((cx, cy), r, fill=False, edgecolor=col,
                                linewidth=0.9, alpha=0.50, linestyle="--", zorder=2))
        # Region name just above the cluster
        ax.text(
            cx, cy + r + 7,
            REGION_LABELS[c.ex["id"]],
            ha="center", va="bottom",
            fontsize=7.2, fontweight="bold",
            color=col, alpha=0.90,
            path_effects=[pe.withStroke(linewidth=2.5, foreground=BG)],
        )

    elif c.level == 2:
        iso        = c.ex["id"]
        median_val = data.loc[data["iso3"] == iso, "median"].values[0]

        # Filled country circle
        ax.add_patch(plt.Circle((cx, cy), r, color=col, alpha=0.84, linewidth=0, zorder=3))

        # Subtle white rim on larger circles for separation
        if r > 4:
            ax.add_patch(plt.Circle((cx, cy), r, fill=False, edgecolor="white",
                                    linewidth=0.22, alpha=0.35, zorder=4))

        # ISO label: only for countries above the intake threshold
        if median_val >= 55:
            fs = 9.0  if median_val >= 220 else 6.8
            fw = "bold" if median_val >= 150 else "normal"
            ax.text(cx, cy, iso, ha="center", va="center",
                    fontsize=fs, fontweight=fw,
                    color="white", alpha=0.95, zorder=5)

ax.set_xlim(-S * PAD, S * PAD)
ax.set_ylim(-S * PAD, S * PAD)

# ── 7. Title & subtitle ──────────────────────────────────────
fig.text(0.5, 0.982,
         "Sugar-Sweetened Beverage Consumption",
         ha="center", va="top",
         fontsize=20, fontweight="bold", color="white")
fig.text(0.5, 0.963,
         "Mean daily intake (g/day) across 180 countries · GDD 2018  ·  Circles grouped by world region",
         ha="center", va="top", fontsize=10, color="#8AABB8")

# ── 8. Legend ────────────────────────────────────────────────
handles = [
    mpatches.Patch(color=PALETTE[k], label=REGION_LABELS[k], alpha=0.85)
    for k in region_order
]
fig.legend(
    handles=handles,
    loc="lower center",
    bbox_to_anchor=(0.5, 0.005),
    ncol=4,
    frameon=False,
    fontsize=8.5,
    labelcolor="#CCCCCC",
    handlelength=1.0,
    handleheight=0.85,
    columnspacing=1.1,
    handletextpad=0.5,
)

# ── 9. Caption ───────────────────────────────────────────────
fig.text(0.5, 0.047,
         "Source: Global Dietary Database (GDD) 2018  ·  #30DayChartChallenge Day 08 — Circular",
         ha="center", fontsize=7.5, color="#4A6070")

# ── 10. Save ─────────────────────────────────────────────────
save_path = os.path.join(script_dir, "day_8.png")
plt.savefig(
    save_path,
    dpi=300, bbox_inches="tight",
    facecolor=BG,
)
plt.show()
print(f"Saved: {save_path}")