from life_wallpaper.config import AppConfig
from life_wallpaper.main import get_renderer
from life_wallpaper.themes.dashboard import DashboardRenderer
from life_wallpaper.renderer import WallpaperRenderer


def test_factory_returns_dashboard_by_default():
    config = AppConfig(
        profile={"name": "Test", "dob": "2000-01-01", "life_expectancy": 80},
        collections={"mantras": [], "footer_quotes": []},
    )
    # Default is "original"
    renderer = get_renderer(config)
    assert isinstance(renderer, DashboardRenderer)


def test_factory_returns_original_explicitly():
    config = AppConfig(
        theme="original",
        profile={"name": "Test", "dob": "2000-01-01", "life_expectancy": 80},
        collections={"mantras": [], "footer_quotes": []},
    )
    renderer = get_renderer(config)
    assert isinstance(renderer, DashboardRenderer)


def test_factory_returns_og_theme():
    config = AppConfig(
        theme="og",
        profile={"name": "Test", "dob": "2000-01-01", "life_expectancy": 80},
        collections={"mantras": [], "footer_quotes": []},
    )
    renderer = get_renderer(config)
    assert isinstance(renderer, WallpaperRenderer)


def test_factory_fallback():
    config = AppConfig(
        theme="invalid_value",
        profile={"name": "Test", "dob": "2000-01-01", "life_expectancy": 80},
        collections={"mantras": [], "footer_quotes": []},
    )
    renderer = get_renderer(config)
    assert isinstance(renderer, DashboardRenderer)
