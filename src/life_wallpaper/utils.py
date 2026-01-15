from PIL import ImageFont
import os


def load_font_family(font_list: list[str], size_px: int) -> ImageFont.FreeTypeFont:
    """Attempts to load a font from the provided list, respecting preference order."""
    for name in font_list:
        try:
            return ImageFont.truetype(name, size_px)
        except Exception:
            continue
    return ImageFont.load_default()
