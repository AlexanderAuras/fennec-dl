import tempfile
from pathlib import Path
from typing import List

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
    path = Path(tempfile.gettempdir(), "fennec_dl", "yaml_loader_test_test_load_dynamic_1.yaml").resolve()
    path2 = Path(tempfile.gettempdir(), "fennec_dl", "yaml_loader_test_test_load_dynamic_2.yaml").resolve()
    with open(path, "w", encoding="UTF-8") as file:
        file.write("invalid yaml")
    with pytest.raises(ConfigLoadingError):
        config = YAMLLoader.load_dynamic(path)

    with open(path, "w", encoding="UTF-8") as file:
        file.write('a: 1\nb:\n  a: !include "yaml_loader_test_test_load_dynamic_2.yaml"\n  c: !ref a\n  d: !ref b.a.x\n  e: [1,2,3]\n')
    with open(path2, "w", encoding="UTF-8") as file:
        file.write("x: 7\ny: 2\n")
    config = YAMLLoader.load_dynamic(path)
    path.unlink()
    path2.unlink()
    assert config.a == 1
    assert config.b.a.x == 7
    assert config.b.a.y == 2
    assert config.b.c == 1
    assert config.b.d == 7


def test_load_static() -> None:
    class MockConfig(StaticConfig):
        class MockSubConfig(StaticConfig):
            class MockSubConfig2(StaticConfig):
                x: int
                y: int

            a: MockSubConfig2
            c: int
            d: int
            e: List[int]

        a: int
        b: MockSubConfig

    with pytest.raises(ConfigLoadingError):
        YAMLLoader.load_static("nonexistent.yaml", MockConfig)
    with pytest.raises(ConfigLoadingError):
        YAMLLoader.load_static("invalid path", MockConfig)
    Path(tempfile.gettempdir(), "fennec_dl").mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.gettempdir(), "fennec_dl", "yaml_loader_test_test_load_static_1.yaml").resolve()
    path2 = Path(tempfile.gettempdir(), "fennec_dl", "yaml_loader_test_test_load_static_2.yaml").resolve()
    with open(path, "w", encoding="UTF-8") as file:
        file.write("invalid yaml")
    with pytest.raises(ConfigLoadingError):
        config = YAMLLoader.load_static(path, MockConfig)

    with open(path, "w", encoding="UTF-8") as file:
        file.write('a: 1\nb:\n  a: !include "yaml_loader_test_test_load_static_2.yaml"\n  c: !ref a\n  d: !ref b.a.x\n  e: [1,2,3]\n')
    with open(path2, "w", encoding="UTF-8") as file:
        file.write("x: 7\ny: 2\n")
    config = YAMLLoader.load_static(path, MockConfig)
    path.unlink()
    path2.unlink()
    assert config.a == 1
    assert config.b.a.x == 7
    assert config.b.a.y == 2
    assert config.b.c == 1
    assert config.b.d == 7


test_load_dynamic()
