# utils/chart.py
# Bloomberg GP-style chart renderer — v2

import csv
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
BG          = "#000000"
ORANGE_HDR  = "#FF6600"
HDR_BOX_BG  = "#CC3300"
BLUE_1      = "#3399FF"
ORANGE_2    = "#FF9900"
GREEN_3     = "#33FF99"
MAGENTA_4   = "#FF33CC"
YELLOW_5    = "#FFFF33"
GRID_H      = "#2A2A2A"
TEXT_W      = "#FFFFFF"
TEXT_DIM    = "#888888"
TEXT_FAINT  = "#505050"
LEGEND_BG   = "#000000"
LEGEND_BD   = "#333333"
XBOX_BG     = "#0D0D0D"
XLINE_COL   = "#FFFFFF"
MONO        = "Courier New"

SERIES_COLORS = [ORANGE_2, BLUE_1, GREEN_3, MAGENTA_4, YELLOW_5]


# ── Data helpers ───────────────────────────────────────────────────────────────

def _looks_like_date(s: str) -> bool:
    try:
        pd.to_datetime(str(s).strip())
        return True
    except Exception:
        return False


def parse_pasted_data(raw: str) -> pd.DataFrame:
    """Parse tab-separated (Excel paste) or comma/semicolon-separated data.
    Auto-detects transposed layout (dates as column headers)."""

    # Normalise line endings
    raw = raw.strip().replace("\r\n", "\n").replace("\r", "\n")

    # Detect delimiter from the first line
    first_line = raw.split("\n")[0]
    if "\t" in first_line:
        sep = "\t"
    else:
        try:
            dialect = csv.Sniffer().sniff(raw[:2048], delimiters=",;|")
            sep = dialect.delimiter
        except Exception:
            sep = ","

    # Avoid using comma as both column separator and thousands separator
    thousands = "," if sep != "," else None

    df = pd.read_csv(io.StringIO(raw), sep=sep, thousands=thousands)
    df.columns = [str(c).strip() for c in df.columns]

    # Auto-detect transposed layout: if most column headers look like dates,
    # flip the dataframe to long format (dates become rows)
    date_col_count = sum(1 for c in df.columns if _looks_like_date(c))
    if date_col_count >= len(df.columns) * 0.7 and len(df.columns) > 3:
        df = df.T.reset_index()
        n_val_cols = len(df.columns) - 1
        df.columns = ["Date"] + (
            ["Value"] if n_val_cols == 1
            else [f"Series {i + 1}" for i in range(n_val_cols)]
        )

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


# ── Chart renderer ─────────────────────────────────────────────────────────────

def render_bloomberg_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    is_time_series: bool = True,
) -> bytes:
    """Render a Bloomberg GP-style chart. Returns PNG bytes."""

    # Prepare x values
    if is_time_series:
        x_vals = pd.to_datetime(df[x_col], infer_datetime_format=True)
    else:
        x_vals = df[x_col].astype(str)

    # ── Figure ─────────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(14, 7.5), facecolor=BG, dpi=150)

    # No header bar — Bloomberg chart view is pure black.
    # Leave right margin for y-axis pills, bottom for x-axis boxes + footer.
    L, R = 0.02, 0.88
    W    = R - L

    ax_main   = fig.add_axes([L,    0.095, W,    0.890])   # main plot
    ax_xbox   = fig.add_axes([L,    0.035, W,    0.060])   # boxed x-axis
    ax_footer = fig.add_axes([0.00, 0.000, 1.00, 0.035])   # footer

    # ── MAIN CHART ─────────────────────────────────────────────────────────────
    ax_main.set_facecolor(BG)

    # Only the right spine visible (thin grey)
    ax_main.spines["top"].set_visible(False)
    ax_main.spines["left"].set_visible(False)
    ax_main.spines["bottom"].set_visible(False)
    ax_main.spines["right"].set_edgecolor("#444444")
    ax_main.spines["right"].set_linewidth(0.5)

    # Horizontal gridlines only, no vertical
    ax_main.yaxis.grid(True, color=GRID_H, linewidth=0.6, linestyle="-")
    ax_main.xaxis.grid(False)
    ax_main.set_axisbelow(True)

    # y-axis on the right, suppress x-axis labels (boxed x handles them)
    ax_main.yaxis.tick_right()
    ax_main.yaxis.set_label_position("right")
    ax_main.tick_params(axis="x", which="both", bottom=False, labelbottom=False)

    # ── PLOT SERIES ─────────────────────────────────────────────────────────────
    y_min_g, y_max_g = np.inf, -np.inf
    last_vals: dict[str, tuple[str, float]] = {}  # col -> (color, last_value)

    for idx, col in enumerate(y_cols):
        color  = SERIES_COLORS[idx % len(SERIES_COLORS)]
        y_vals = pd.to_numeric(df[col], errors="coerce")

        if is_time_series:
            ax_main.plot(x_vals, y_vals, color=color, linewidth=1.4,
                         solid_capstyle="round", zorder=3)
        else:
            ax_main.plot(range(len(x_vals)), y_vals, color=color,
                         linewidth=1.4, solid_capstyle="round", zorder=3)

        valid = y_vals.dropna()
        if not valid.empty:
            last_vals[col] = (color, float(valid.iloc[-1]))
            y_min_g = min(y_min_g, float(valid.min()))
            y_max_g = max(y_max_g, float(valid.max()))

    # y-axis range with padding
    if y_min_g != np.inf:
        span = y_max_g - y_min_g or abs(y_max_g) or 1
        ax_main.set_ylim(y_min_g - span * 0.08, y_max_g + span * 0.08)

    # y-axis tick styling
    ax_main.tick_params(axis="y", colors=TEXT_W, labelsize=7, length=3,
                        width=0.4, pad=4)
    for lbl in ax_main.get_yticklabels():
        lbl.set_fontfamily(MONO)
        lbl.set_color(TEXT_W)
        lbl.set_fontsize(7)

    ax_main.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v:,.0f}" if abs(v) >= 10 else f"{v:.2f}"
    ))

    if y_label:
        ax_main.set_ylabel(y_label, color=TEXT_DIM, fontsize=7,
                           fontfamily=MONO, labelpad=8)

    # ── Y-AXIS PILLS ───────────────────────────────────────────────────────────
    # Color-matched filled boxes overlaying the right y-axis at current value
    for col, (color, last_val) in last_vals.items():
        val_str = f"{last_val:.0f}" if abs(last_val) >= 1 else f"{last_val:.2f}"
        ax_main.annotate(
            f"  {val_str}  ",
            xy=(1.0, last_val),
            xycoords=("axes fraction", "data"),
            xytext=(3, 0),
            textcoords="offset points",
            color=BG,
            fontsize=7,
            fontfamily=MONO,
            fontweight="bold",
            va="center",
            annotation_clip=False,
            zorder=10,
            bbox=dict(facecolor=color, edgecolor="none", boxstyle="square,pad=0.2"),
        )

    # ── CUSTOM LEGEND ──────────────────────────────────────────────────────────
    # Black box, dark grey border, left-aligned labels, right-aligned values
    n       = len(y_cols)
    line_h  = 0.075
    pad_v   = 0.022
    leg_w   = 0.30
    leg_h   = n * line_h + pad_v * 2
    leg_x   = 0.012
    leg_top = 0.988

    ax_main.add_patch(mpatches.FancyBboxPatch(
        (leg_x, leg_top - leg_h), leg_w, leg_h,
        transform=ax_main.transAxes,
        facecolor=LEGEND_BG, edgecolor=LEGEND_BD,
        linewidth=0.7, boxstyle="square,pad=0",
        zorder=9, clip_on=False,
    ))

    for i, col in enumerate(y_cols):
        color  = SERIES_COLORS[i % len(SERIES_COLORS)]
        row_y  = leg_top - pad_v - (i + 0.5) * line_h

        # Colour line sample
        ax_main.plot(
            [leg_x + 0.008, leg_x + 0.040], [row_y, row_y],
            color=color, linewidth=1.6,
            transform=ax_main.transAxes, zorder=11, clip_on=False,
        )
        # Label
        ax_main.text(
            leg_x + 0.048, row_y, col,
            color=TEXT_W, fontsize=6, fontfamily=MONO,
            transform=ax_main.transAxes, va="center", zorder=11,
        )
        # Current value — right-aligned
        if col in last_vals:
            _, lv = last_vals[col]
            val_str = f"{lv:.0f}" if abs(lv) >= 1 else f"{lv:.2f}"
            ax_main.text(
                leg_x + leg_w - 0.008, row_y, val_str,
                color=color, fontsize=6, fontfamily=MONO, fontweight="bold",
                transform=ax_main.transAxes, va="center", ha="right", zorder=11,
            )

    # ── BOXED X-AXIS ───────────────────────────────────────────────────────────
    # Solid vertical white lines separating years, year labels centred in each cell
    ax_xbox.set_facecolor(XBOX_BG)
    ax_xbox.set_ylim(0, 1)
    ax_xbox.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)
    # All 4 spines white — creates the outer box, inner cells made by axvlines
    for sp in ax_xbox.spines.values():
        sp.set_edgecolor(XLINE_COL)
        sp.set_linewidth(0.8)

    if is_time_series:
        xlim  = ax_main.get_xlim()
        ax_xbox.set_xlim(xlim)

        t_min = mdates.num2date(xlim[0]).replace(tzinfo=None)
        t_max = mdates.num2date(xlim[1]).replace(tzinfo=None)

        # Collect boundary x-positions (Jan 1 of each year within range)
        boundaries = []
        for yr in range(t_min.year, t_max.year + 2):
            xn = mdates.date2num(pd.Timestamp(f"{yr}-01-01"))
            if xlim[0] < xn < xlim[1]:
                boundaries.append((yr, xn))

        # Draw separators and labels
        prev_x = xlim[0]
        prev_yr = t_min.year

        for yr, xn in boundaries:
            ax_xbox.axvline(xn, color=XLINE_COL, linewidth=0.7, zorder=3)
            mid = (prev_x + xn) / 2
            ax_xbox.text(mid, 0.50, str(prev_yr),
                         color=TEXT_W, fontsize=7, fontfamily=MONO,
                         ha="center", va="center", zorder=4)
            prev_x  = xn
            prev_yr = yr

        # Last cell
        mid = (prev_x + xlim[1]) / 2
        ax_xbox.text(mid, 0.50, str(prev_yr),
                     color=TEXT_W, fontsize=7, fontfamily=MONO,
                     ha="center", va="center", zorder=4)

    else:
        n_cats = len(x_vals)
        ax_xbox.set_xlim(-0.5, n_cats - 0.5)
        for i in range(1, n_cats):
            ax_xbox.axvline(i - 0.5, color=XLINE_COL, linewidth=0.7)
        for i, lbl in enumerate(x_vals):
            ax_xbox.text(i, 0.50, str(lbl), color=TEXT_W, fontsize=6.5,
                         fontfamily=MONO, ha="center", va="center")

    if x_label:
        ax_xbox.set_xlabel(x_label, color=TEXT_DIM, fontsize=7,
                           fontfamily=MONO, labelpad=3)

    # ── FOOTER ─────────────────────────────────────────────────────────────────
    ax_footer.set_facecolor(BG)
    ax_footer.axis("off")
    ts = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    footer_left  = f"  {title}  " + f"Copyright\u00ae {datetime.now().year} Bloomberg Finance L.P.  All rights reserved."
    ax_footer.text(0.005, 0.50, footer_left,
                   color=TEXT_FAINT, fontsize=5.5, fontfamily=MONO, va="center")
    ax_footer.text(0.995, 0.50, ts,
                   color=TEXT_FAINT, fontsize=5.5, fontfamily=MONO,
                   va="center", ha="right")

    # ── EXPORT ─────────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG, dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
