import os
import calendar
import platform
import datetime
from PIL import Image, ImageDraw, ImageFont

from ..config import AppConfig
from ..utils import load_font_family


class DashboardRenderer:
    """
    Renderer for the 'Dashboard' theme (formerly play2.py).
    """

    STYLE = {
        "resolution": (3840, 2160),  # 4K
        "colors": {
            "bg": (0, 0, 0),  # Pure Black
            "white": (255, 255, 255),
            "grey": (140, 140, 140),  # Subtle text
            "dark": (50, 50, 50),  # Labels
            "accent": (46, 213, 115),  # Spring Green
            "done": (55, 55, 55),  # Past days
            "todo": (20, 20, 20),  # Future days
            "bar_bg": (28, 28, 28),
        },
        "layout": {
            "margin": 180,
            "text_optical_offset_y": -4,
            "calendar_highlight_offset_y": -10,
        },
    }

    def __init__(self, config: AppConfig):
        self.config = config
        self.colors = self.STYLE["colors"]
        self.fonts = {}  # Will be loaded in render

    def _get_font(self, size, bold=False):
        """Smart font loader matching the original logic but adaptable."""
        # Using the project's utility if possible or falling back to original search
        # keeping original search for fidelity to the request "as default wallpaper"
        system = platform.system()
        fonts = []

        if system == "Windows":
            # Prioritize project fonts if available in system, otherwise fallbacks
            fonts = [
                "seguiemj.ttf",
                "arialbd.ttf" if bold else "arial.ttf",
                "calibri.ttf",
            ]
        elif system == "Darwin":
            fonts = ["/Library/Fonts/Arial.ttf", "/System/Library/Fonts/SFNS.ttf"]
        else:
            fonts = ["DejaVuSans.ttf", "FreeSans.ttf", "LiberationSans-Regular.ttf"]

        for f in fonts:
            try:
                return ImageFont.truetype(f, size)
            except OSError:
                continue

        print(f"Warning: Could not load preferred font size {size}. Using default.")
        return ImageFont.load_default()

    def _load_fonts(self):
        self.fonts = {
            "hero": self._get_font(180, True),
            "date": self._get_font(80),
            "sub": self._get_font(50, True),
            "medium": self._get_font(34),
            "small": self._get_font(24),
            "tiny": self._get_font(22),
            "cal_head": self._get_font(40, True),
            "cal_days": self._get_font(30),
            "cal_num": self._get_font(55),
        }

    def _draw_centered(self, draw, cx, cy, text, font, fill):
        draw.text((cx, cy), text, font=font, fill=fill, anchor="mm")

    def _draw_right_aligned(self, draw, x, y, text, font, fill):
        draw.text((x, y), text, font=font, fill=fill, anchor="ra")

    def _draw_glow(self, draw, cx, cy, radius, color):
        draw.ellipse(
            [cx - radius - 4, cy - radius - 4, cx + radius + 4, cy + radius + 4],
            outline=(30, 80, 50),
            width=1,
        )
        draw.ellipse(
            [cx - radius - 2, cy - radius - 2, cx + radius + 2, cy + radius + 2],
            outline=(40, 150, 80),
            width=1,
        )

    def draw_life_dashboard(self, draw, x, y):
        c = self.colors

        # Adaptation from config
        try:
            birth = self.config.profile.dob
        except:
            birth = datetime.date(1995, 1, 1)

        today = datetime.date.today()
        days_alive = (today - birth).days
        years_alive = days_alive / 365.25
        year_end = datetime.date(today.year, 12, 31)
        days_left = (year_end - today).days

        name_text = self.config.profile.name.title()
        self._draw_right_aligned(draw, x, y, name_text, self.fonts["hero"], c["accent"])

        stats_y = y + 180
        age_str = f"{years_alive:.1f} YEARS  •  {days_alive:,} DAYS"
        self._draw_right_aligned(
            draw, x, stats_y, age_str, self.fonts["sub"], c["white"]
        )

        mot_y = stats_y + 70
        mot_str = f"{days_left} DAYS LEFT IN {today.year}"
        self._draw_right_aligned(
            draw, x, mot_y, mot_str, self.fonts["small"], c["grey"]
        )

    def draw_year_progress(self, draw, x, y, width, date_obj):
        c = self.colors
        year = date_obj.year
        is_leap = calendar.isleap(year)
        total_days = 366 if is_leap else 365
        days_in_months = [calendar.monthrange(year, i)[1] for i in range(1, 13)]

        # Label
        pct = (date_obj.timetuple().tm_yday / total_days) * 100
        draw.text(
            (x, y - 60),
            f"{year} PROGRESS: {pct:.1f}%",
            fill=c["dark"],
            font=self.fonts["medium"],
        )

        height = 14
        gap = 8
        usable_width = width - (gap * 11)

        current_x = x
        month_labels = [
            "JAN",
            "FEB",
            "MAR",
            "APR",
            "MAY",
            "JUN",
            "JUL",
            "AUG",
            "SEP",
            "OCT",
            "NOV",
            "DEC",
        ]

        for i, d_count in enumerate(days_in_months):
            m_idx = i + 1
            seg_w = (d_count / total_days) * usable_width
            rect = [current_x, y, current_x + seg_w, y + height]

            if date_obj.month > m_idx:
                draw.rectangle(rect, fill=c["accent"])
            elif date_obj.month == m_idx:
                draw.rectangle(rect, fill=c["bar_bg"])
                fill_w = seg_w * (date_obj.day / d_count)
                draw.rectangle(
                    [current_x, y, current_x + fill_w, y + height], fill=c["accent"]
                )
                draw.rectangle(
                    [
                        current_x + fill_w - 1,
                        y - 3,
                        current_x + fill_w + 1,
                        y + height + 3,
                    ],
                    fill=c["white"],
                )
            else:
                draw.rectangle(rect, fill=c["bar_bg"])

            draw.text(
                (current_x + seg_w / 2, y + height + 22),
                month_labels[i],
                fill=c["dark"],
                font=self.fonts["tiny"],
                anchor="mt",
            )
            current_x += seg_w + gap

    def draw_calendar(self, draw, x, y, date_obj):
        c = self.colors
        opt_text_y = self.STYLE["layout"]["text_optical_offset_y"]
        opt_circle_y = self.STYLE["layout"]["calendar_highlight_offset_y"]
        cell_size = 110

        cal = calendar.Calendar(firstweekday=6)
        matrix = cal.monthdayscalendar(date_obj.year, date_obj.month)

        draw.text(
            (x, y - 80),
            date_obj.strftime("%B"),
            fill=c["white"],
            font=self.fonts["cal_head"],
        )

        headers = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        for i, h in enumerate(headers):
            cx = x + (i * cell_size) + (cell_size / 2)
            cy = y + (cell_size / 2)
            self._draw_centered(draw, cx, cy, h, self.fonts["cal_days"], c["dark"])

        grid_y = y + cell_size
        for r, week in enumerate(matrix):
            for col, day in enumerate(week):
                if day == 0:
                    continue

                cx = x + (col * cell_size) + (cell_size / 2)
                cy = grid_y + (r * cell_size) + (cell_size / 2)

                if day == date_obj.day:
                    rad = 42
                    cy_circle = cy + opt_circle_y
                    self._draw_glow(draw, cx, cy_circle, rad, c["accent"])
                    draw.ellipse(
                        [cx - rad, cy_circle - rad, cx + rad, cy_circle + rad],
                        fill=c["accent"],
                    )
                    self._draw_centered(
                        draw,
                        cx,
                        cy + opt_text_y,
                        str(day),
                        self.fonts["cal_num"],
                        c["bg"],
                    )
                elif day < date_obj.day:
                    self._draw_centered(
                        draw,
                        cx,
                        cy + opt_text_y,
                        str(day),
                        self.fonts["cal_num"],
                        c["done"],
                    )
                else:
                    self._draw_centered(
                        draw,
                        cx,
                        cy + opt_text_y,
                        str(day),
                        self.fonts["cal_num"],
                        c["grey"],
                    )

    def draw_year_grid(self, draw, right_x, center_y, date_obj):
        c = self.colors
        spacing = 38
        dot_r = 12

        grid_w = 53 * spacing
        grid_h = 7 * spacing

        start_x = right_x - grid_w
        start_y = center_y - (grid_h / 2)

        draw.text(
            (start_x, start_y - 120),
            f"{date_obj.year} OVERVIEW",
            fill=c["white"],
            font=self.fonts["sub"],
        )

        start_date = datetime.date(date_obj.year, 1, 1)
        # Fix offset to align correctly with days
        # weekday(): Mon=0, Sun=6. We want Sun to be top row (index 0) if our grid is row-per-day,
        # but the grid seems to be col-per-week.
        # Code from play2.py uses (day_idx % 7) * spacing for Y, so Y is day-of-week.
        offset = (start_date.weekday() + 1) % 7
        iter_date = start_date
        month_label_pos = {}

        while iter_date.year == date_obj.year:
            day_idx = (iter_date - start_date).days + offset
            dx = start_x + ((day_idx // 7) * spacing)
            dy = start_y + ((day_idx % 7) * spacing)

            m_name = iter_date.strftime("%b").upper()
            if m_name not in month_label_pos:
                month_label_pos[m_name] = dx

            if iter_date < date_obj:
                fill, outline = c["done"], None
            elif iter_date == date_obj:
                fill, outline = c["accent"], None
                self._draw_glow(draw, dx, dy, dot_r, c["accent"])
            else:
                fill, outline = c["todo"], None

            draw.ellipse(
                [dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r],
                fill=fill,
                outline=outline,
            )
            iter_date += datetime.timedelta(days=1)

        for m, mx in month_label_pos.items():
            draw.text((mx, start_y - 50), m, fill=c["dark"], font=self.fonts["tiny"])

        days = ["S", "", "T", "", "T", "", "S"]
        for i, d in enumerate(days):
            draw.text(
                (start_x - 35, start_y + (i * spacing)),
                d,
                fill=c["done"],
                font=self.fonts["tiny"],
                anchor="mm",
            )

    def render(self) -> str:
        """Generates the dashboard wallpaper."""
        self._load_fonts()

        W, H = self.STYLE["resolution"]
        img = Image.new("RGB", (W, H), self.colors["bg"])
        draw = ImageDraw.Draw(img)

        now = datetime.date.today()
        margin = self.STYLE["layout"]["margin"]

        # 1. Date Header
        draw.text(
            (margin, margin),
            now.strftime("%A"),
            fill=self.colors["accent"],
            font=self.fonts["hero"],
        )
        draw.text(
            (margin, margin + 210),
            now.strftime("%B %d, %Y"),
            fill=self.colors["white"],
            font=self.fonts["date"],
        )

        # 2. Progress Bar
        self.draw_year_progress(draw, margin, margin + 450, 900, now)

        # 3. Calendar
        cal_height = 9 * 110
        self.draw_calendar(draw, margin, H - cal_height, now)

        # 4. Life Stats (Right)
        self.draw_life_dashboard(draw, W - margin, margin)

        # 5. Year Grid (Right Center)
        self.draw_year_grid(draw, W - 250, H / 2, now)

        out_path = os.path.join(os.getcwd(), "life_wallpaper.png")
        img.save(out_path)
        return out_path
