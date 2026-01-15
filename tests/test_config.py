from datetime import date
from life_wallpaper.config import load_config, AppConfig


def test_load_default_config():
    """Test that default values are loaded when no config file exists (or invalid path)."""
    config = load_config("non_existent_file.json")
    assert isinstance(config, AppConfig)
    assert config.profile.name == "User"
    assert config.profile.life_expectancy == 80


def test_config_structure():
    """Test the Pydantic model structure."""
    config = AppConfig(
        profile={"name": "Test User", "dob": "1990-01-01", "life_expectancy": 90},
        collections={"mantras": ["Test Mantra"], "footer_quotes": ["Test Quote"]},
    )
    assert config.profile.name == "Test User"
    assert config.profile.dob == date(1990, 1, 1)
    assert config.collections.mantras[0] == "Test Mantra"
