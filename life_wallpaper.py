"""
life_wallpaper_elegant.py

Generates a pitch-black, high-clarity wallpaper sized to the primary display,
renders a day-by-day grid for the year, a circular progress ring, and extra stats.
Saves the PNG in the same folder as the script and sets it as Windows wallpaper.

Requires:
    pip install pillow

Run:
    python life_wallpaper_elegant.py
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import date, datetime
import calendar
import math
import os
import ctypes
import sys

# ---------------- USER CONFIG ----------------
SCALE = 2  # supersampling factor (2 is a good balance)
BG_COLOR = (0, 0, 0)  # pitch black
ACCENT = (255, 120, 45)  # orange accent
DOT_ACTIVE = (240, 240, 240)
DOT_INACTIVE = (50, 50, 50)
DOT_TODAY = (255, 160, 95)
TEXT_MAIN = (230, 230, 230)
TEXT_SECOND = (160, 160, 160)
CAPTION = "Make today count."  # short, subtle nudge (optional)
OUT_BASENAME = "life_wallpaper"  # file written into script folder (date appended)
MIN_DOT_DIAM_PIXEL = 6
MARGIN_X_RATIO = 0.10
MARGIN_Y_RATIO = 0.14
# ---------------------------------------------


def get_primary_monitor_size():
    """Return (width, height) of primary monitor on Windows."""
    user32 = ctypes.windll.user32
    # try to get true pixels (for high DPI displays)
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height


def script_dir():
    """Return directory where this script lives; fallback to cwd."""
    try:
        return os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    except NameError:
        return os.getcwd()


def load_font(preferred_size):
    """Try several fonts and fall back to PIL default if none available."""
    # order of preference
    candidates = [
        "segoeui.ttf",  # Windows modern UI
        "Segoe UI.ttf",
        "arial.ttf",
        "DejaVuSans.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, preferred_size)
        except Exception:
            continue
    return ImageFont.load_default()


def compute_grid_params(width, height, total_days):
    """Compute columns, rows, diameter & gap so a clean grid fits the area."""
    margin_x = int(width * MARGIN_X_RATIO)
    margin_y = int(height * MARGIN_Y_RATIO)

    # initial estimate for diameter based on width
    guess_diameter = max(MIN_DOT_DIAM_PIXEL, width // 140)

    gap = max(4, guess_diameter // 2)
    avail_w = width - 2 * margin_x
    columns = max(8, min(total_days, avail_w // (guess_diameter + gap)))

    # refine
    diameter = (avail_w - (columns - 1) * gap) // columns
    diameter = max(MIN_DOT_DIAM_PIXEL, diameter)
    gap = max(3, gap)

    rows = math.ceil(total_days / columns)
    avail_h = height - 2 * margin_y
    total_grid_h = rows * diameter + (rows - 1) * gap

    # shrink diameter or increase columns until it fits vertically
    while total_grid_h > avail_h and diameter > MIN_DOT_DIAM_PIXEL:
        diameter -= 1
        rows = math.ceil(total_days / columns)
        total_grid_h = rows * diameter + (rows - 1) * gap
        if diameter <= MIN_DOT_DIAM_PIXEL and total_grid_h > avail_h:
            columns = min(total_days, columns + 2)
            diameter = max(
                MIN_DOT_DIAM_PIXEL, (avail_w - (columns - 1) * gap) // columns
            )
            rows = math.ceil(total_days / columns)
            total_grid_h = rows * diameter + (rows - 1) * gap
            if columns >= total_days:
                break

    return {
        "margin_x": margin_x,
        "margin_y": margin_y,
        "columns": columns,
        "rows": rows,
        "diameter": diameter,
        "gap": gap,
    }


def draw_progress_ring(draw, center, radius, thickness, percent, accent, bg):
    """Draw a ring (donut) showing percent; percent is 0..100."""
    # outer box
    x0 = center[0] - radius
    y0 = center[1] - radius
    x1 = center[0] + radius
    y1 = center[1] + radius

    # angle: PIL pieslice uses degrees counterclockwise from +x (starting at 3 o'clock).
    # We want top (12 o'clock) as 0 and go clockwise. Convert:
    start_angle = -90
    end_angle = start_angle + (percent / 100.0) * 360.0

    # filled arc (outer)
    draw.pieslice([x0, y0, x1, y1], start=start_angle, end=end_angle, fill=accent)

    # carve inner circle with BG color to create ring
    inner_r = radius - thickness
    ix0 = center[0] - inner_r
    iy0 = center[1] - inner_r
    ix1 = center[0] + inner_r
    iy1 = center[1] + inner_r
    draw.ellipse([ix0, iy0, ix1, iy1], fill=bg)


def generate_wallpaper():
    # date & stats
    today = date.today()
    now = datetime.now()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)
    day_of_year = (today - year_start).days + 1
    total_days = (year_end - year_start).days + 1
    percent_year = (day_of_year / total_days) * 100.0

    # month stats
    month_days = calendar.monthrange(today.year, today.month)[1]
    day_of_month = today.day
    percent_month = (day_of_month / month_days) * 100.0

    # week stats (ISO week)
    week_of_year = today.isocalendar()[1]
    # week progress (0..100) based on weekday (Mon=1..Sun=7)
    weekday = today.isoweekday()
    percent_week = ((weekday - 1) / 7.0) * 100.0 + (now.hour / 24.0) * (100.0 / 7.0)

    # quarter
    quarter = (today.month - 1) // 3 + 1
    quarter_start_month = 3 * (quarter - 1) + 1
    quarter_end_month = quarter_start_month + 2
    # compute days in quarter
    q_start = date(today.year, quarter_start_month, 1)
    q_end = date(
        today.year,
        quarter_end_month,
        calendar.monthrange(today.year, quarter_end_month)[1],
    )
    days_in_quarter = (q_end - q_start).days + 1
    days_into_quarter = (today - q_start).days + 1
    percent_quarter = (days_into_quarter / days_in_quarter) * 100.0

    days_left = total_days - day_of_year

    # display size (native)
    width, height = get_primary_monitor_size()
    W = width * SCALE
    H = height * SCALE

    # grid params computed in final native pixels then scaled for supersample
    params = compute_grid_params(width, height, total_days)
    diameter = params["diameter"] * SCALE
    gap = params["gap"] * SCALE
    margin_x = params["margin_x"] * SCALE
    margin_y = params["margin_y"] * SCALE
    columns = params["columns"]
    rows = math.ceil(total_days / columns)

    # create high-res canvas
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # fonts at scaled sizes
    try:
        font_big = load_font(56 * SCALE)
        font_med = load_font(20 * SCALE)
        font_small = load_font(14 * SCALE)
        font_caps = load_font(12 * SCALE)
    except Exception:
        font_big = font_med = font_small = font_caps = ImageFont.load_default()

    # Draw grid of dots (left-middle)
    grid_left = margin_x
    grid_top = margin_y
    # center grid vertically if there is spare space
    total_grid_h = rows * diameter + (rows - 1) * gap
    spare_v = (H - 2 * margin_y) - total_grid_h
    if spare_v > 0:
        grid_top += spare_v // 2

    for i in range(total_days):
        row = i // columns
        col = i % columns

        x = grid_left + col * (diameter + gap)
        y = grid_top + row * (diameter + gap)
        bbox = (x, y, x + diameter, y + diameter)

        idx_day = i + 1
        if idx_day < day_of_year:
            color = DOT_ACTIVE
        elif idx_day == day_of_year:
            color = DOT_TODAY
        else:
            color = DOT_INACTIVE

        # draw slightly softened circles (no stroke)
        draw.ellipse(bbox, fill=color)

    # Draw a crisp circular year progress ring on the right area
    ring_radius = min(width // 8, height // 6) * SCALE
    ring_thickness = int(ring_radius * 0.23)
    ring_center = (int(W - margin_x - ring_radius - (40 * SCALE)), int(H // 3))

    # background faint ring for remainder
    # draw base (subtle grey ring)
    draw.ellipse(
        [
            ring_center[0] - ring_radius,
            ring_center[1] - ring_radius,
            ring_center[0] + ring_radius,
            ring_center[1] + ring_radius,
        ],
        fill=(18, 18, 18),
    )
    # draw percent arc
    draw_progress_ring(
        draw, ring_center, ring_radius, ring_thickness, percent_year, ACCENT, BG_COLOR
    )

    # percentage text centered inside ring
    perc_text = f"{percent_year:.2f}%"
    w_perc, h_perc = draw.textsize(perc_text, font=font_big)
    draw.text(
        (ring_center[0] - w_perc // 2, ring_center[1] - h_perc // 2 - int(6 * SCALE)),
        perc_text,
        font=font_big,
        fill=TEXT_MAIN,
    )

    # small label under percent
    label = "of year"
    w_lab, h_lab = draw.textsize(label, font=font_small)
    draw.text(
        (ring_center[0] - w_lab // 2, ring_center[1] + h_perc // 2 + int(2 * SCALE)),
        label,
        font=font_small,
        fill=TEXT_SECOND,
    )

    # Draw additional stats in a neat column below the ring
    stats_x = ring_center[0] - ring_radius - int(10 * SCALE)
    stats_y = ring_center[1] + ring_radius + int(20 * SCALE)

    lines = [
        (f"Today: {today.isoformat()}", TEXT_MAIN),
        (f"Day {day_of_year} / {total_days} • {days_left} days left", TEXT_SECOND),
        (f"Week {week_of_year} • {percent_week:.1f}% through week", TEXT_SECOND),
        (
            f"Month {today.strftime('%b')}: {day_of_month}/{month_days} • {percent_month:.1f}%",
            TEXT_SECOND,
        ),
        (
            f"Quarter {quarter}: {days_into_quarter}/{days_in_quarter} • {percent_quarter:.1f}%",
            TEXT_SECOND,
        ),
    ]

    y = stats_y
    for txt, col in lines:
        w, h = draw.textsize(txt, font=font_med)
        # center aligned with ring center x
        draw.text((ring_center[0] - w // 2, y), txt, font=font_med, fill=col)
        y += int(26 * SCALE)

    # small footer caption centered near bottom
    footer_y = H - int(60 * SCALE)
    f_w, f_h = draw.textsize(CAPTION, font=font_caps)
    draw.text((W // 2 - f_w // 2, footer_y), CAPTION, font=font_caps, fill=TEXT_SECOND)

    # small legend bottom-left
    legend_x = margin_x
    legend_y = H - int(90 * SCALE)
    small_r = int(6 * SCALE)
    draw.ellipse(
        (legend_x, legend_y, legend_x + small_r * 2, legend_y + small_r * 2),
        fill=DOT_ACTIVE,
    )
    draw.text(
        (legend_x + small_r * 2 + int(8 * SCALE), legend_y),
        "Days passed",
        font=font_small,
        fill=TEXT_SECOND,
    )
    legend_x += int(220 * SCALE)
    draw.ellipse(
        (legend_x, legend_y, legend_x + small_r * 2, legend_y + small_r * 2),
        fill=DOT_TODAY,
    )
    draw.text(
        (legend_x + small_r * 2 + int(8 * SCALE), legend_y),
        "Today",
        font=font_small,
        fill=TEXT_SECOND,
    )
    legend_x += int(140 * SCALE)
    draw.ellipse(
        (legend_x, legend_y, legend_x + small_r * 2, legend_y + small_r * 2),
        fill=DOT_INACTIVE,
    )
    draw.text(
        (legend_x + small_r * 2 + int(8 * SCALE), legend_y),
        "Remaining",
        font=font_small,
        fill=TEXT_SECOND,
    )

    # Downsample to native resolution with Lanczos for high clarity
    final = img.resize((width, height), resample=Image.LANCZOS)

    # Save to script directory
    out_dir = script_dir()
    today_str = today.isoformat()
    out_name = f"{OUT_BASENAME}_{today_str}.png"
    out_path = os.path.join(out_dir, out_name)

    final.save(out_path, optimize=True)
    print(f"Saved wallpaper to: {out_path}")
    return out_path


def set_wallpaper_windows(path):
    """Set wallpaper using SystemParametersInfoW (unicode)."""
    SPI_SETDESKWALLPAPER = 20
    res = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)
    if not res:
        raise ctypes.WinError()
    print("Wallpaper set successfully.")


if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script is designed for Windows (primary monitor). Exiting.")
        sys.exit(1)

    out = generate_wallpaper()
    # try:
    #     set_wallpaper_windows(out)
    # except Exception as e:
    #     print("Failed to set wallpaper automatically:", e)
    #     print("You can set the file manually:", out)
