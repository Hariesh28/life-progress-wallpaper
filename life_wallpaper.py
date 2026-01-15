"""
Generates a high-fidelity 4K wallpaper dashboard visualizing life progress,
calendar data, and motivational quotes.
"""

import os
import sys
import json
import ctypes
import math
import random
from datetime import date, datetime
import calendar
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CONFIG_FILE = "life_config.json"

# Canvas Constraints (4K Native)
WIDTH = 3840
HEIGHT = 2160
SCALE = 1

# Layout Anchors relative to canvas height
Y_HEADER = 0.10
Y_GRID_CENTER = 0.38
Y_LIFE_CENTER = 0.64
Y_BOTTOM_WIDGETS = 0.75

# Color Palette ("Midnight Gold" Theme)
C_BG = (0, 0, 0)
C_ACCENT = (212, 175, 55)
C_ACCENT_DIM = (60, 50, 16)
C_TEXT_HEAD = (255, 255, 255)
C_TEXT_SUB = (122, 122, 122)
C_TEXT_LABEL = (107, 107, 107)
C_TEXT_DIM = (90, 90, 90)
C_DOT_EMPTY = (30, 30, 30)
C_DOT_PASSED = (90, 90, 90)
C_RAIL_FUTURE = (18, 18, 18)
C_RAIL_PAST = (180, 180, 180)

# Font Priorities
FONTS_HEAD = ["montserrat-semibold.ttf", "bebasneue.ttf", "arialbd.ttf"]
FONTS_BODY = ["inter-medium.ttf", "roboto-medium.ttf", "arial.ttf"]
FONTS_REG = ["inter-regular.ttf", "roboto-regular.ttf", "arial.ttf"]
FONTS_BOLD = ["inter-semibold.ttf", "roboto-bold.ttf", "arialbd.ttf"]

DEFAULT_DATA = {
    "name": "User",
    "dob": "2000-01-01",
    "life_expectancy": 80,
    "mantra": "THIS DAY WILL NOT COME AGAIN",
    "quote_bottom": "TIME IS THE ONLY NON-RENEWABLE RESOURCE",
}


class LifeLedger:
    """
    Main controller for generating the wallpaper visualization.
    Handles data loading, image drawing, and post-processing.
    """

    def __init__(self):
        self.raw_config = self._load_config()
        self.data = {
            "name": self.raw_config.get("profile", {}).get("name", "User"),
            "dob": self.raw_config.get("profile", {}).get("dob", "2000-01-01"),
            "life_expectancy": self.raw_config.get("profile", {}).get(
                "life_expectancy", 80
            ),
            "mantra": random.choice(
                self.raw_config.get("collections", {}).get("mantras", ["CARPE DIEM"])
            ),
            "quote_bottom": random.choice(
                self.raw_config.get("collections", {}).get(
                    "footer_quotes", ["TIME FLIES"]
                )
            ),
        }

        self.W = WIDTH * SCALE
        self.H = HEIGHT * SCALE
        self.s = self.H / 2160

        self.img = Image.new("RGB", (self.W, self.H), C_BG)
        self.draw = ImageDraw.Draw(self.img, "RGBA")

        # Initialize Fonts
        self.f_hero = self._load_font(FONTS_HEAD, 120)
        self.f_sub = self._load_font(FONTS_REG, 26)
        self.f_h2 = self._load_font(FONTS_HEAD, 24)
        self.f_body = self._load_font(FONTS_BOLD, 22)
        self.f_cal = self._load_font(FONTS_BOLD, 28)
        self.f_bold = self._load_font(FONTS_BOLD, 22)
        self.f_med = self._load_font(FONTS_BODY, 20)
        self.f_tiny = self._load_font(FONTS_REG, 16)
        self.f_nano = self._load_font(FONTS_REG, 14)
        self.f_big_pct = self._load_font(FONTS_HEAD, 54)

    def _load_config(self):
        """Load configuration from JSON file or return default data."""
        try:
            with open(os.path.join(os.path.dirname(__file__), CONFIG_FILE), "r") as f:
                return json.load(f)
        except Exception as e:
            return DEFAULT_DATA

    def _load_font(self, font_list, size_pt):
        """Attempts to load a font from the provided list, respecting preference order."""
        size_px = int(size_pt * self.s * SCALE)
        for name in font_list:
            try:
                return ImageFont.truetype(name, size_px)
            except Exception:
                continue
        return ImageFont.load_default()

    def _draw_text_centered(self, x, y, text, font, fill, align_vertical=False):
        """Draws text centered horizontally at the given coordinates."""
        bbox = self.draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x_pos = x - w / 2

        if align_vertical:
            y_pos = y - (h / 2) - (4 * self.s)
        else:
            y_pos = y

        self.draw.text((x_pos, y_pos), text, font=font, fill=fill)

    def _draw_text_right(self, x, y, text, font, fill):
        """Draws text right-aligned at the given x coordinate."""
        bbox = self.draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        self.draw.text((x - w, y), text, font=font, fill=fill)

    def _draw_matte_gold_circle(self, cx, cy, radius, halo=False):
        """Draws a stylized gold circle, optionally with a glow effect."""
        if halo:
            blur_r = 22 * self.s
            pad = int(radius + blur_r * 3)
            overlay = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
            d_ov = ImageDraw.Draw(overlay)
            d_ov.ellipse(
                (pad - radius, pad - radius, pad + radius, pad + radius),
                fill=(212, 175, 55, 30),
            )
            overlay = overlay.filter(ImageFilter.GaussianBlur(blur_r))
            self.img.paste(overlay, (int(cx - pad), int(cy - pad)), overlay)
            self.draw = ImageDraw.Draw(self.img, "RGBA")

        self.draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius), fill=C_ACCENT
        )
        shine_r = radius * 0.8
        self.draw.ellipse(
            (cx - shine_r, cy - radius, cx + shine_r, cy - radius + shine_r),
            fill=(246, 215, 123, 40),
        )

    # --- RENDERERS ---

    def draw_header(self):
        """Renders the top header with date and mantra."""
        today = date.today()
        date_str = today.strftime("%A %d").upper()
        mantra = self.data.get("mantra", "AMOR FATI").upper()

        y_pos = self.H * Y_HEADER
        self._draw_text_centered(self.W / 2, y_pos, date_str, self.f_hero, C_TEXT_HEAD)
        self._draw_text_centered(
            self.W / 2, y_pos + 170 * self.s, mantra, self.f_sub, (255, 255, 255, 70)
        )

    def draw_grid_system(self):
        """Renders the main year grid and annual progress bar."""
        today = date.today()
        day_of_year = int(today.strftime("%j"))

        # Grid Layout Configuration
        cols, rows = 52, 7
        dot_diam = 22 * self.s
        spacing = 54 * self.s

        grid_w = (cols - 1) * spacing
        grid_h = (rows - 1) * spacing

        start_x = (self.W - grid_w) / 2
        start_y = (self.H * Y_GRID_CENTER) - (grid_h / 2)

        for i in range(364):
            c, r = i // 7, i % 7
            cx = start_x + c * spacing
            cy = start_y + r * spacing
            day_num = i + 1

            if day_num < day_of_year:
                self.draw.ellipse(
                    (
                        cx - dot_diam / 2,
                        cy - dot_diam / 2,
                        cx + dot_diam / 2,
                        cy + dot_diam / 2,
                    ),
                    fill=C_DOT_PASSED,
                )
            elif day_num == day_of_year:
                r_today = (dot_diam / 2) * 1.3
                self._draw_matte_gold_circle(cx, cy, r_today, halo=True)
            else:
                self.draw.ellipse(
                    (
                        cx - dot_diam / 2,
                        cy - dot_diam / 2,
                        cx + dot_diam / 2,
                        cy + dot_diam / 2,
                    ),
                    fill=C_DOT_EMPTY,
                )

        # Year Progress Bar
        y_bar = start_y + grid_h + 80 * self.s
        bar_w = grid_w + dot_diam
        bar_h = 6 * self.s
        bar_x = (self.W - bar_w) / 2
        pct = day_of_year / 365.0

        # Background Track
        self.draw.rectangle(
            (bar_x, y_bar, bar_x + bar_w, y_bar + bar_h), fill=C_DOT_EMPTY
        )

        # Filled Progress
        fill_w = bar_w * pct
        self.draw.rectangle(
            (bar_x, y_bar, bar_x + fill_w, y_bar + bar_h), fill=C_ACCENT
        )

        # Month Ticks
        for i in range(1, 12):
            tick_x = bar_x + (bar_w * (i / 12.0))
            self.draw.rectangle(
                (tick_x, y_bar, tick_x + 2 * self.s, y_bar + bar_h), fill=C_BG
            )

        # Current Position Indicator
        caret_size = 8 * self.s
        cx_caret = bar_x + fill_w
        cy_caret = y_bar + bar_h + caret_size
        points = [
            (cx_caret, y_bar + bar_h),
            (cx_caret - caret_size, cy_caret),
            (cx_caret + caret_size, cy_caret),
        ]
        self.draw.polygon(points, fill=C_ACCENT)

        # Progress Label
        label_text = f"YEAR PROGRESS — {pct*100:.1f}%"
        self._draw_text_centered(
            self.W / 2, y_bar + 30 * self.s, label_text, self.f_tiny, C_TEXT_LABEL
        )

    def draw_life_trajectory(self):
        """Renders the life expectancy progress bar."""
        today = date.today()
        dob = datetime.strptime(self.data.get("dob", "2000-01-01"), "%Y-%m-%d").date()
        expectancy = self.data.get("life_expectancy", 80)
        death = date(dob.year + expectancy, dob.month, dob.day)

        days_lived = (today - dob).days
        total_days = (death - dob).days
        pct = max(0, min(1, days_lived / total_days))

        years_lived = days_lived / 365.25
        weeks_lived = days_lived / 7

        bar_w = self.W * 0.45
        bar_h = 2 * self.s
        bar_x = (self.W - bar_w) / 2
        bar_y = self.H * Y_LIFE_CENTER

        # Progress Bar Rail
        self.draw.rectangle(
            (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), fill=C_RAIL_FUTURE
        )
        fill_w = bar_w * pct
        self.draw.rectangle(
            (bar_x, bar_y, bar_x + fill_w, bar_y + bar_h), fill=C_RAIL_PAST
        )

        # Decade Ticks
        tick_h = 6 * self.s
        for i in range(1, expectancy // 10):
            tx = bar_x + (bar_w * (i * 10 / expectancy))
            self.draw.rectangle(
                (tx, bar_y + bar_h, tx + 2 * self.s, bar_y + bar_h + tick_h),
                fill=C_DOT_PASSED,
            )

        # Current Position Marker
        mx = bar_x + fill_w
        self._draw_matte_gold_circle(mx, bar_y + bar_h / 2, 4 * self.s, halo=False)
        self._draw_text_centered(
            mx, bar_y - 20 * self.s, "YOU ARE HERE", self.f_nano, (255, 255, 255, 70)
        )

        # Life Statistics
        name = self.data.get("name", "USER").upper()
        stats_txt = f"{name}  •  {int(years_lived)} YEARS  //  {int(weeks_lived):,} WEEKS  //  {int(days_lived):,} DAYS"
        self._draw_text_right(
            bar_x + bar_w, bar_y - 20 * self.s, stats_txt, self.f_tiny, C_ACCENT
        )

        # Footer Quote
        quote = self.data.get("quote_bottom", "TIME IS THE ONLY NON-RENEWABLE RESOURCE")
        self._draw_text_centered(
            self.W / 2, bar_y + 60 * self.s, quote, self.f_nano, (90, 90, 90)
        )

    def draw_calendar(self):
        """Renders the current month's calendar."""
        today = date.today()
        cal = calendar.monthcalendar(today.year, today.month)

        margin_left = 120 * self.s
        start_y = self.H * Y_BOTTOM_WIDGETS

        self.draw.text(
            (margin_left, start_y),
            calendar.month_name[today.month].upper(),
            font=self.f_h2,
            fill=C_TEXT_HEAD,
        )

        cell_s = 55 * self.s
        gap = 16 * self.s
        grid_y = start_y + 80 * self.s

        for i, d in enumerate("MTWTFSS"):
            dx = margin_left + i * (cell_s + gap) + cell_s / 2
            self._draw_text_centered(dx, grid_y, d, self.f_tiny, C_TEXT_DIM)

        grid_y += 50 * self.s

        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    continue

                dx = margin_left + c * (cell_s + gap) + cell_s / 2
                dy = grid_y + r * (cell_s + gap)

                if day == today.day:
                    r_c = cell_s / 2
                    self.draw.ellipse(
                        (dx - r_c, dy - r_c, dx + r_c, dy + r_c), fill=C_ACCENT
                    )
                    text_col = (0, 0, 0)
                    font = self.f_cal
                else:
                    text_col = C_TEXT_LABEL
                    font = self.f_body

                self._draw_text_centered(
                    dx, dy, str(day), font, text_col, align_vertical=True
                )

    def draw_time_cluster(self):
        """Renders the monthly progress ring."""
        margin_right = 120 * self.s
        cx = self.W - margin_right - 95 * self.s
        cy = self.H * Y_BOTTOM_WIDGETS + 140 * self.s

        today = date.today()
        days_in_m = calendar.monthrange(today.year, today.month)[1]
        pct = today.day / days_in_m

        r_ring = 95 * self.s
        w_ring = 6 * self.s

        self.draw.arc(
            (cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring),
            start=0,
            end=360,
            fill=C_DOT_EMPTY,
            width=int(w_ring),
        )
        self.draw.arc(
            (cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring),
            start=-90,
            end=-90 + (pct * 360),
            fill=C_ACCENT,
            width=int(w_ring),
        )

        ang = math.radians(-90 + (pct * 360))
        tick_len = 10 * self.s
        ix = cx + (r_ring - 15 * self.s) * math.cos(ang)
        iy = cy + (r_ring - 15 * self.s) * math.sin(ang)
        ox = cx + (r_ring - 15 * self.s - tick_len) * math.cos(ang)
        oy = cy + (r_ring - 15 * self.s - tick_len) * math.sin(ang)
        self.draw.line([ix, iy, ox, oy], fill=C_ACCENT, width=4)

        self._draw_text_centered(
            cx, cy, f"{int(pct*100)}%", self.f_big_pct, C_TEXT_HEAD, align_vertical=True
        )
        self._draw_text_centered(
            cx, cy + 120 * self.s, "MONTH", self.f_tiny, C_TEXT_LABEL
        )

    def apply_grain_and_vignette(self):
        """Applies cinematic grain and vignette properties to the final image."""
        vignette = Image.new("L", (self.W, self.H), 255)
        d_v = ImageDraw.Draw(vignette)
        d_v.ellipse((0, 0, self.W, self.H), fill=0)
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=300 * self.s))
        black = Image.new("RGB", (self.W, self.H), (0, 0, 0))
        vignette = vignette.point(lambda p: p * 0.08)
        self.img.paste(black, (0, 0), vignette)

        noise_size = (int(self.W / 4), int(self.H / 4))
        noise_data = os.urandom(noise_size[0] * noise_size[1])
        noise_img = Image.frombytes("L", noise_size, noise_data)
        noise_img = noise_img.resize((self.W, self.H), Image.NEAREST)
        noise_layer = Image.new("RGB", (self.W, self.H), (30, 30, 30))
        mask = noise_img.point(lambda p: p * 0.015)
        self.img.paste(noise_layer, (0, 0), mask)

    def generate(self):
        """Execution pipeline."""
        print("Rendering Life Ledger (4K)...")
        self.draw_header()
        self.draw_grid_system()
        self.draw_life_trajectory()
        self.draw_calendar()
        self.draw_time_cluster()

        print("Applying post-processing...")
        self.apply_grain_and_vignette()

        out_path = os.path.join(os.path.dirname(__file__), "life_wallpaper.png")
        self.img.save(out_path, quality=100)
        return out_path


if __name__ == "__main__":
    app = LifeLedger()
    path = app.generate()

    if sys.platform == "win32":
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
            print("Wallpaper Updated.")
        except Exception as e:
            print(f"Error setting wallpaper: {e}")
    else:
        print(f"Generated: {path}")
