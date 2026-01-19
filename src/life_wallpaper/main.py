import sys
import ctypes
from .config import load_config
from .renderer import WallpaperRenderer
from .themes.dashboard import DashboardRenderer


def set_wallpaper(path: str):
    """Sets the wallpaper on Windows."""
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
            print("Wallpaper Updated.")
        except Exception as e:
            print(f"Error setting wallpaper: {e}")
    else:
        print(f"Wallpaper generated at: {path}")


def main():
    """Main execution point."""
    print("Loading configuration...")
    config = load_config()

    print(f"Theme selected: {config.theme}")
    if config.theme == "original":
        app = DashboardRenderer(config)
    elif config.theme == "og":
        app = WallpaperRenderer(config)
    else:
        # Fallback
        print(f"Unknown theme '{config.theme}', defaulting to 'original' (Dashboard)")
        app = DashboardRenderer(config)

    output_path = app.render()

    set_wallpaper(output_path)


if __name__ == "__main__":
    main()
