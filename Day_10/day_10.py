import matplotlib
matplotlib.use("Agg")   # must be set BEFORE importing pyplot

from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import io
import base64
import kagglehub
import textwrap
import os
from pathlib import Path

# ─────────────────────────────────────────
# 1. Data
# ─────────────────────────────────────────
print("Fetching latest data from Kaggle...")
path = kagglehub.dataset_download(
    "sarandebnath/coke-studio-bangla-youtube-metric-daily-update"
)
csv_file_path = os.path.join(path, "coke_studio_bangla_raw.csv")

df = pd.read_csv(csv_file_path)
for col in ["Views", "Likes", "Comments"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

def season_key(s: str):
    """Sort 'Season 2' before 'Season 10' (numeric, not alphabetical)."""
    digits = "".join(ch for ch in str(s) if ch.isdigit())
    return (int(digits) if digits else float("inf"), str(s))


seasons = ["All"] + sorted(df["Season"].dropna().unique().tolist(), key=season_key)
all_genres = set(
    g.strip()
    for sublist in df["Genre"].dropna().str.split(",")
    for g in sublist
)
genres = sorted(all_genres - {"Not Applicable"})
categories = ["All"] + sorted(df["Video_Type"].dropna().unique().tolist())


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────
def fmt_short(n: float) -> str:
    """113_920_349 → '113.9M',  50_000 → '50K'"""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))


SEASON_COLORS = {
    "Season 1": "#E63946",
    "Season 2": "#F4A261",
    "Season 3": "#2A9D8F",
    "Season 4": "#457B9D",
    "Season 5": "#9B5DE5",
    "Season 6": "#F15BB5",
    "Season 7": "#E9C46A",
    "Season 8": "#6A994E",
    "Season 9": "#00BBF9",
    "Season 10": "#8D6E63",
}
DEFAULT_COLOR = "#264653"


def _fig_to_src(fig) -> str:
    """Encode a Matplotlib figure as a base64 PNG data-URI."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return f"data:image/png;base64,{b64}"


_CSS_PATH = Path(__file__).parent / "styles.css"
_INLINE_CSS = _CSS_PATH.read_text(encoding="utf-8") if _CSS_PATH.exists() else ""

# ─────────────────────────────────────────
# 2. UI
# ─────────────────────────────────────────

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("🎛️ Filters"),
        ui.input_select("season_filter", "Select Season:",
                        choices=seasons, selected="All"),
        ui.input_selectize("genre_filter", "Select Genre(s):",
                           choices=genres, multiple=True,
                           options={"placeholder": "All genres"}),
        ui.input_select("category_filter", "Select Category:",
                        choices=categories, selected="All"),
        ui.hr(),
        ui.input_select(
            "rank_by", "Rank Top 5 By:",
            choices={"Views": "👁 Views",
                     "Likes": "❤️ Likes",
                     "Comments": "💬 Comments"},
            selected="Views",
        ),
        ui.hr(),
        ui.input_slider(
            "view_filter", "Min Views (Millions):",
            min=0, max=int(df["Views"].max() / 1_000_000) + 1,
            value=0, step=1,
        ),
        ui.input_slider(
            "like_filter", "Min Likes:",
            min=0, max=int(df["Likes"].max()),
            value=0, step=10_000,
        ),
        ui.input_slider(
            "comment_filter", "Min Comments:",
            min=0, max=int(df["Comments"].max()),
            value=0, step=500,
        ),
    ),
    ui.tags.style(_INLINE_CSS),
    ui.card(
        ui.output_ui("top_videos_plot"),
    ),
    title="🎵 Coke Studio Bangla · Top Music Videos",
)


# ─────────────────────────────────────────
# 3. Server
# ─────────────────────────────────────────
def server(input, output, session):

    @reactive.calc
    def filtered_data():
        data = df.copy()

        if input.season_filter() != "All":
            data = data[data["Season"] == input.season_filter()]
        selected_genres = set(input.genre_filter())
        if selected_genres:  # nothing selected = all genres
            # Genre cells are comma-separated, e.g. "Folk, Hip-Hop" → keep if ANY matches
            data = data[data["Genre"].fillna("").apply(
                lambda g: bool(selected_genres & {x.strip() for x in g.split(",")})
            )]
        if input.category_filter() != "All":
            data = data[data["Video_Type"] == input.category_filter()]

        data = data[
            (data["Views"]    >= input.view_filter() * 1_000_000)
            & (data["Likes"]    >= input.like_filter())
            & (data["Comments"] >= input.comment_filter())
        ]
        rank_col = input.rank_by()
        return data.nlargest(5, rank_col).sort_values(rank_col, ascending=True)

    def build_figure() -> plt.Figure:
        data     = filtered_data()
        rank_col = input.rank_by()

        # ── Empty state ─────────────────────────────────────────
        if data.empty:
            fig, ax = plt.subplots(figsize=(12, 7), facecolor="#FAFAFA")
            ax.set_facecolor("#FAFAFA")
            ax.text(0.5, 0.5, "No videos match the current filters.",
                    ha="center", va="center", fontsize=15,
                    color="#888", style="italic")
            ax.axis("off")
            plt.tight_layout()
            return fig

        # ── Wrap titles ──────────────────────────────────────────
        # Different videos can share a title → add the video type so rows stay distinct
        dup_titles = data["Title"].duplicated(keep=False)
        titles = [
            f"{t} ({vt})" if dup else t
            for t, vt, dup in zip(data["Title"], data["Video_Type"], dup_titles)
        ]
        wrapped    = ["\n".join(textwrap.wrap(t, width=38)) for t in titles]
        bar_colors = [SEASON_COLORS.get(s, DEFAULT_COLOR) for s in data["Season"]]
        values     = data[rank_col].values
        max_val    = float(values.max())

        # ── Figure ───────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(12, 7), facecolor="#FAFAFA")
        ax.set_facecolor("#F7F7F7")

        # Numeric y positions: one row per video even if labels repeat
        y_pos = range(len(values))
        bars = ax.barh(
            y_pos, values,
            color=bar_colors,
            edgecolor="white", linewidth=1.2,
            height=0.55,
        )
        ax.set_yticks(list(y_pos), wrapped)

        # ── Short value labels at end of bars ───────────────────
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_width() + max_val * 0.012,
                bar.get_y() + bar.get_height() / 2,
                fmt_short(val),
                va="center", ha="left",
                fontsize=11, fontweight="bold", color="#222",
            )

        # ── X-axis: human-readable (50K / 1M / 50M …) ──────────
        def human_fmt(x, _):
            if x >= 1_000_000:
                v = x / 1_000_000
                return f"{v:.0f}M" if v == int(v) else f"{v:.1f}M"
            if x >= 1_000:
                v = x / 1_000
                return f"{v:.0f}K" if v == int(v) else f"{v:.1f}K"
            return f"{int(x)}"

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(human_fmt))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6, integer=False))

        # ── Grid & spines ────────────────────────────────────────
        ax.set_axisbelow(True)
        ax.xaxis.grid(True, linestyle="--", alpha=0.45, color="#BDBDBD")
        ax.yaxis.grid(False)
        for sp in ["top", "right", "left"]:
            ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color("#CCCCCC")

        # ── Title & axis labels ──────────────────────────────────
        rank_label = rank_col  # "Views" / "Likes" / "Comments"
        ax.set_title(
            f"Top 5 Coke Studio Bangla Videos  —  Ranked by {rank_label}",
            fontsize=14, fontweight="bold", color="#111",
            loc="left", pad=14,
        )
        ax.set_xlabel(f"Total {rank_label}", fontsize=11, color="#555", labelpad=8)
        ax.set_ylabel("")
        ax.tick_params(axis="x", labelsize=9.5, colors="#555")
        ax.tick_params(axis="y", labelsize=8.5, colors="#333", pad=4)

        # ── Season legend → outside the plot on the right (never covers labels) ──
        seasons_present = data["Season"].dropna().unique()
        patches = [
            mpatches.Patch(
                color=SEASON_COLORS.get(s, DEFAULT_COLOR), label=s
            )
            for s in sorted(seasons_present, key=season_key)
        ]
        ax.legend(
            handles=patches,
            loc="upper left",
            bbox_to_anchor=(1.01, 1.0),
            borderaxespad=0,
            title="Season", title_fontsize=8.5,
            fontsize=8.5,
            frameon=True, framealpha=0.92,
            facecolor="white", edgecolor="#DDDDDD",
            borderpad=0.8,
        )

        ax.set_xlim(0, max_val * 1.22)
        plt.tight_layout(pad=1.8)
        return fig

    @render.ui
    def top_videos_plot():
        fig = build_figure()
        src = _fig_to_src(fig)
        return ui.tags.img(
            src=src,
            style="width:100%; height:auto; border-radius:6px;",
        )


app = App(app_ui, server)