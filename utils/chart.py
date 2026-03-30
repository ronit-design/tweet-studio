# utils/chart.py
# Bloomberg GP-style chart renderer

import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ── Bloomberg palette ──────────────────────────────────────────────────────────
BG       = "#000000"
ORANGE   = "#FF6600"
HDR_BOX  = "#CC3300"
AMBER    = "#FF8C00"
CYAN     = "#00E5FF"
YELLOW   = "#FFE600"
GREEN    = "#00FF41"
MAGENTA  = "#FF44FF"
PINK     = "#FF6EC7"
LIME     = "#7FFF00"
GRID_COL = "#1C1C1C"
TEXT_COL = "#FFFFFF"
SUB_COL  = "#AAAAAA"
DIM_COL  = "#444444"
MONO     = "Courier New"

SERIES_COLORS = [AMBER, CYAN, YELLOW, GREEN, MAGENTA, PINK, LIME]


# ── Data helpers ──────────────────────────────────────────────────────────────

def parse_pasted_data(raw: str) -> pd.DataFrame:
    """Parse tab-separated (Excel paste) or comma-separated data."""
    raw = raw.strip()
    sep = "\t" if "\t" in raw else ","
    df = pd.read_csv(io.StringIO(raw), sep=sep, thousands=",")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def detect_date_col(df: pd.DataFrame) -> str | None:
    """Return the first column that parses cleanly as dates, or None."""
    for col in df.columns:
        try:
            parsed = pd.to_datetime(df[col], infer_datetime_format=True)
            if parsed.notna().sum() > len(df) * 0.7:
                return col
        except Exception:
            pass
    return None


# ── Chart renderer ────────────────────────────────────────────────────────────

def render_bloomberg_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str],
    title: str = "",
    is_time_series: bool = True,
) -> bytes:
    """Render a Bloomberg GP-style chart and return PNG bytes."""

    # ── Prepare x values ──────────────────────────────────────────────────────
    if is_time_series:
        x_vals = pd.to_datetime(df[x_col], infer_datetime_format=True)
    else:
        x_vals = df[x_col].astype(str)

    # ── Figure + axes layout ──────────────────────────────────────────────────
    fig = plt.figure(figsize=(14, 7.5), facecolor=BG, dpi=150)

    # Manual placement: [left, bottom, width, height] in figure fraction
    ax_hdr    = fig.add_axes([0.000, 0.930, 1.000, 0.060])   # orange header
    ax_main   = fig.add_axes([0.050, 0.145, 0.900, 0.775])   # chart
    ax_period = fig.add_axes([0.000, 0.055, 1.000, 0.055])   # period bar
    ax_footer = fig.add_axes([0.000, 0.000, 1.000, 0.040])   # footer

    # ── Header bar ────────────────────────────────────────────────────────────
    ax_hdr.set_facecolor(ORANGE)
    ax_hdr.set_xlim(0, 1)
    ax_hdr.set_ylim(0, 1)
    ax_hdr.axis("off")

    # "GP" function box
    ax_hdr.add_patch(mpatches.Rectangle((0.003, 0.08), 0.038, 0.84,
                                         color=HDR_BOX, zorder=2))
    ax_hdr.text(0.022, 0.50, "GP", color=TEXT_COL, fontsize=8.5,
                fontfamily=MONO, fontweight="bold",
                ha="center", va="center", zorder=3)

    # Title in header
    hdr_label = (title.upper() if title else "CHART") + "  <EQUITY> GP"
    ax_hdr.text(0.050, 0.50, hdr_label, color=BG, fontsize=8.5,
                fontfamily=MONO, fontweight="bold",
                ha="left", va="center")

    # Timestamp top-right
    ax_hdr.text(0.997, 0.50,
                datetime.now().strftime("%m/%d/%Y  %H:%M:%S"),
                color=BG, fontsize=7, fontfamily=MONO,
                ha="right", va="center")

    # ── Main chart ────────────────────────────────────────────────────────────
    ax_main.set_facecolor(BG)

    # Spines in orange
    for spine in ax_main.spines.values():
        spine.set_edgecolor(ORANGE)
        spine.set_linewidth(0.8)

    # Grid
    ax_main.grid(True, color=GRID_COL, linewidth=0.6,
                 linestyle="-", which="major", zorder=0)
    ax_main.set_axisbelow(True)

    # y-axis on the right (Bloomberg default)
    ax_main.yaxis.tick_right()
    ax_main.yaxis.set_label_position("right")

    # ── Plot series ───────────────────────────────────────────────────────────
    y_min_global, y_max_global = np.inf, -np.inf

    for idx, col in enumerate(y_cols):
        color  = SERIES_COLORS[idx % len(SERIES_COLORS)]
        y_vals = pd.to_numeric(df[col], errors="coerce")

        if is_time_series:
            ax_main.plot(x_vals, y_vals, color=color, linewidth=1.3,
                         label=col, solid_capstyle="butt", zorder=3)
        else:
            bars = ax_main.bar(range(len(x_vals)), y_vals, color=color,
                               label=col, alpha=0.85, zorder=3,
                               width=0.6)

        # Last-value indicator: dashed horizontal + dot
        valid = y_vals.dropna()
        if not valid.empty:
            last_y = valid.iloc[-1]
            last_x = x_vals.iloc[len(valid) - 1] if is_time_series else len(valid) - 1

            ax_main.axhline(last_y, color=color, linewidth=0.4,
                            linestyle="--", alpha=0.45, zorder=2)
            ax_main.scatter([last_x], [last_y], color=color,
                            s=22, zorder=5, linewidths=0)

            # Annotate last value on right spine
            ax_main.annotate(
                f"{last_y:,.2f}" if abs(last_y) < 1000 else f"{last_y:,.0f}",
                xy=(1, last_y), xycoords=("axes fraction", "data"),
                xytext=(6, 0), textcoords="offset points",
                color=color, fontsize=6.5, fontfamily=MONO,
                va="center",
            )

            y_min_global = min(y_min_global, valid.min())
            y_max_global = max(y_max_global, valid.max())

    # y-axis range
    if y_min_global != np.inf:
        pad = (y_max_global - y_min_global) * 0.06 or abs(y_max_global) * 0.05 or 1
        ax_main.set_ylim(y_min_global - pad, y_max_global + pad)

    # ── x-axis formatting ─────────────────────────────────────────────────────
    if is_time_series:
        span_days = (x_vals.max() - x_vals.min()).days
        if span_days <= 90:
            ax_main.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
            ax_main.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        elif span_days <= 548:
            ax_main.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
            ax_main.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        elif span_days <= 1825:
            ax_main.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
            ax_main.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        else:
            ax_main.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
            ax_main.xaxis.set_major_locator(mdates.YearLocator())
    else:
        ax_main.set_xticks(range(len(x_vals)))
        ax_main.set_xticklabels(list(x_vals), rotation=40, ha="right")

    # ── Tick + label styling ──────────────────────────────────────────────────
    ax_main.tick_params(axis="both", colors=TEXT_COL, labelsize=7,
                        length=3, width=0.5, pad=4)
    for lbl in ax_main.get_xticklabels() + ax_main.get_yticklabels():
        lbl.set_fontfamily(MONO)
        lbl.set_color(TEXT_COL)
        lbl.set_fontsize(7)

    # y-axis number format
    ax_main.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v:,.1f}" if abs(v) < 10_000 else f"{v:,.0f}"
    ))

    # Subtitle: series names below header
    ax_main.set_title(
        "  |  ".join(y_cols),
        color=SUB_COL, fontsize=7, fontfamily=MONO,
        loc="left", pad=5,
    )

    # Legend for multi-series
    if len(y_cols) > 1:
        ax_main.legend(
            loc="upper left",
            facecolor="#080808",
            edgecolor=ORANGE,
            labelcolor=TEXT_COL,
            prop={"family": MONO, "size": 6.5},
            framealpha=0.92,
            borderpad=0.6,
        )

    # ── Period selector bar ───────────────────────────────────────────────────
    ax_period.set_facecolor("#080808")
    ax_period.set_xlim(0, 1)
    ax_period.set_ylim(0, 1)
    ax_period.axis("off")

    for spine in ax_period.spines.values():
        spine.set_edgecolor(ORANGE)
        spine.set_linewidth(0.5)

    periods = ["1M", "3M", "6M", "YTD", "1Y", "2Y", "5Y", "10Y", "ALL"]
    for i, p in enumerate(periods):
        active = (i == 4)  # "1Y" highlighted by default
        ax_period.text(
            0.01 + i * 0.09 + 0.025, 0.50, p,
            color=BG if active else SUB_COL,
            fontsize=6.5, fontfamily=MONO,
            va="center", ha="center",
            bbox=dict(
                facecolor=ORANGE if active else "#1A1A1A",
                edgecolor=ORANGE if active else "#333333",
                boxstyle="square,pad=0.35",
                linewidth=0.5,
            ),
        )

    ax_period.text(0.978, 0.50, "Source: User Data", color="#555555",
                   fontsize=5.5, fontfamily=MONO, va="center", ha="right")

    # ── Footer ────────────────────────────────────────────────────────────────
    ax_footer.set_facecolor(BG)
    ax_footer.axis("off")
    ax_footer.text(
        0.005, 0.50,
        "Copyright 2025 Bloomberg Finance L.P.  All rights reserved.  "
        "This information may not be reproduced or recirculated without prior written permission.",
        color=DIM_COL, fontsize=5, fontfamily=MONO, va="center",
    )

    # ── Export PNG ────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG, dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
