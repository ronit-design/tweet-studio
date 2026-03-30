# utils/helpers.py
# Tweet parsing, calendar generation, formatting utilities

from datetime import date, timedelta
from utils.data import CALENDAR_RELEASES, COUNTRY_COLORS


def parse_tweet_blocks(text: str) -> list[dict]:
    """Parse AI output into tweet blocks with angle labels"""
    segments = [s.strip() for s in text.split("\n\n") if s.strip()]
    blocks = []
    current = []

    for seg in segments:
        if seg.upper().startswith("ANGLE:"):
            if current:
                blocks.append({
                    "content": "\n\n".join(current),
                    "angle": seg.replace("ANGLE:", "").replace("Angle:", "").strip(),
                })
                current = []
        else:
            current.append(seg)

    if current:
        blocks.append({
            "content": "\n\n".join(current),
            "angle": f"variation {len(blocks) + 1}",
        })

    if not blocks:
        blocks.append({"content": text.strip(), "angle": "generated"})

    return blocks


def get_upcoming_releases(days_ahead: int = 42) -> list[dict]:
    """
    Generate upcoming release dates for the next N days.
    Dates are approximate based on known release schedules.
    """
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    items = []

    for release in CALENDAR_RELEASES:
        dates = _generate_dates(release, today, cutoff)
        for d in dates:
            items.append({
                **release,
                "date": d,
                "color": COUNTRY_COLORS.get(release["country"], "#666"),
                "is_today": d == today,
                "is_tomorrow": d == today + timedelta(days=1),
            })

    items.sort(key=lambda x: x["date"])
    return items


def _generate_dates(release: dict, today: date, cutoff: date) -> list[date]:
    """Generate upcoming dates for a single release based on frequency"""
    dates = []
    freq = release.get("freq", "monthly")
    offset = release.get("day_offset", 15)
    weekday = release.get("weekday")  # 0=Mon, 1=Tue ... 6=Sun

    if freq == "weekly" and weekday is not None:
        # Every week on a specific weekday
        days_until = (weekday - today.weekday()) % 7
        next_date = today + timedelta(days=days_until if days_until > 0 else 7)
        while next_date <= cutoff:
            dates.append(next_date)
            next_date += timedelta(days=7)

    elif freq == "monthly":
        # Approximate monthly — offset into current and next month
        for month_delta in range(3):
            if month_delta == 0:
                year, month = today.year, today.month
            elif month_delta == 1:
                year = today.year + (today.month // 12)
                month = (today.month % 12) + 1
            else:
                year = today.year + ((today.month + 1) // 12)
                month = ((today.month + 1) % 12) + 1

            day = min(offset, _days_in_month(year, month))
            try:
                d = date(year, month, day)
                if today < d <= cutoff:
                    dates.append(d)
            except ValueError:
                pass

    elif freq == "quarterly":
        # Roughly every 3 months
        for q in range(2):
            d = today + timedelta(days=offset + q * 91)
            if today < d <= cutoff:
                dates.append(d)

    elif freq in ("6-weekly", "6-per-year", "8-per-year"):
        # Central bank meeting style — every 6-8 weeks
        interval = 42 if "6" in freq else 45
        d = today + timedelta(days=offset % interval)
        if d <= today:
            d += timedelta(days=interval)
        while d <= cutoff:
            dates.append(d)
            d += timedelta(days=interval)

    return dates


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return (date(year + 1, 1, 1) - date(year, 12, 1)).days
    return (date(year, month + 1, 1) - date(year, month, 1)).days


def char_count_color(count: int) -> str:
    """Return color string based on character count vs 280 limit"""
    if count > 280:
        return "red"
    if count > 250:
        return "orange"
    return "normal"


def format_date_label(d: date) -> str:
    today = date.today()
    if d == today:
        return f"🔴 Today · {d.strftime('%a %b %-d')}"
    if d == today + timedelta(days=1):
        return f"Tomorrow · {d.strftime('%a %b %-d')}"
    return d.strftime("%A, %b %-d")
