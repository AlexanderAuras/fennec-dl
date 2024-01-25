import tempfile
from pathlib import Path

import pytest

from fennec_dl.config.static_config import StaticConfig
from fennec_dl.config.yaml_loader import YAMLLoader
from fennec_dl.errors.config_loading_error import ConfigLoadingError


def test_load_dynamic() -> None:
    with pytest.raises(ConfigLoadingError):
        YAMLLoader.load_dynamic("nonexistent.yaml")
    with pytest.raises(ConfigLoadingError):
        YAMLLoader.load_dynamic("invalid path")
    Path(tempfile.gettempdir(), "fennec_dl").mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.gettempdir(), "fennec_dl", "loader_test_test_load_dynamic_1.yaml").resolve()
    with open(path, "w", encoding="UTF-8") as file:
        file.write("invalid yaml")
    with pytest.raises(ConfigLoadingError):
        config = YAMLLoader.load_dynamic(path)

    with open(path, "w", encoding="UTF-8") as file:
        file.write("a: 1\nb:\n  a: 2\n  c: 3\n")
    config = YAMLLoader.load_dynamic(path)
    path.unlink()
    assert config.a == 1
    assert config.b.a == 2
    assert config.b.c == 3


def test_load_static() -> None:
    class MockConfig(StaticConfig):
        class MockSubConfig(StaticConfig):
            a: int
            c: int

        a: int
        b: MockSubConfig

    with pytest.raises(ConfigLoadingError):
        YAMLLoader.load_static("nonexistent.yaml", MockConfig)
    with pytest.raises(ConfigLoadingError):
        YAMLLoader.load_static("invalid path", MockConfig)
    Path(tempfile.gettempdir(), "fennec_dl").mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.gettempdir(), "fennec_dl", "loader_test_test_load_static_1.yaml").resolve()
    with open(path, "w", encoding="UTF-8") as file:
        file.write("invalid yaml")
    with pytest.raises(ConfigLoadingError):
        config = YAMLLoader.load_static(path, MockConfig)

    with open(path, "w", encoding="UTF-8") as file:
        file.write("a: 1\nb:\n  a: 2\n  c: 3\n")
    config = YAMLLoader.load_static(path, MockConfig)
    path.unlink()
    assert config.a == 1
    assert config.b.a == 2
    assert config.b.c == 3


def test_parse_dynamic() -> None:
    with pytest.raises(ConfigLoadingError):
        YAMLLoader.parse_dynamic("invalid")
    config = YAMLLoader.parse_dynamic("a: 1\nb:\n  a: 2\n  c: 3\n")
    assert config.a == 1
    assert config.b.a == 2
    assert config.b.c == 3


def test_parse_static() -> None:
    class MockConfig(StaticConfig):
        class MockSubConfig(StaticConfig):
            a: int
            c: int

        a: int
        b: MockSubConfig

    with pytest.raises(ConfigLoadingError):
        YAMLLoader.parse_static("invalid", MockConfig)
    config = YAMLLoader.parse_static("a: 1\nb:\n  a: 2\n  c: 3\n", MockConfig)
    assert config.a == 1
    assert config.b.a == 2
    assert config.b.c == 3
