from typing import Any, Dict, List, Optional, cast

import pytest

from fennec_dl.config.config import Config, ConfigEntryType
from fennec_dl.config.dynamic_config import DynamicConfig
from fennec_dl.config.static_config import StaticConfig
from fennec_dl.errors.config_loading_error import ConfigLoadingError
from fennec_dl.errors.readonly_error import ReadOnlyError


def test_init() -> None:
    _ = DynamicConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}, cast(Any, Config)._Config__secret)
    with pytest.raises(ConfigLoadingError):
        _ = DynamicConfig({"k": [{"a": 1, "b": 2}, {"c": 3, "d": 4}]}, cast(Any, Config)._Config__secret)


def test_eq() -> None:
    class MockConfig(StaticConfig):
        class MockSubconfig(StaticConfig):
            a: int
            b: int

        class MockConfig2(StaticConfig):
            class MockConfig21(StaticConfig):
                a: int
                b: int

            class MockConfig22(StaticConfig):
                c: int
                d: int

            a: MockConfig21
            c: MockConfig22

        class MockConfig3(StaticConfig):
            a: List[int]
            b: List[int]

        a: int
        b: float
        c: Optional[int]
        d: bool
        e: str
        f: List[int]
        g: MockSubconfig
        h: List[List[int]]
        i: MockConfig2
        j: MockConfig3

    a = DynamicConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}, cast(Any, Config)._Config__secret)
    b = DynamicConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}, cast(Any, Config)._Config__secret)
    c = MockConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}, cast(Any, Config)._Config__secret)
    d = DynamicConfig({"a": 1, "b": {"x": 3}}, cast(Any, Config)._Config__secret)
    assert a == b
    assert a == c
    assert a != d


def test_len() -> None:
    assert 0 == len(DynamicConfig({}, cast(Any, Config)._Config__secret))
    assert 3 == len(DynamicConfig({"a": 1, "b": {"x": 3}}, cast(Any, Config)._Config__secret))
    assert 20 == len(DynamicConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}, cast(Any, Config)._Config__secret))


def test_contains() -> None:
    config = cast(Any, DynamicConfig({"a": 1, "b": {"x": 3}}, cast(Any, Config)._Config__secret))
    assert "a" in config
    assert "b" in config
    assert "b.x" in config
    assert "c" not in config
    assert "c.x" not in config


def test_iter() -> None:
    assert set() == set(iter(cast(Any, DynamicConfig({}, cast(Any, Config)._Config__secret))))
    assert {"a", "b", "b.x"} == set(iter(cast(Any, DynamicConfig({"a": 1, "b": {"x": 3}}, cast(Any, Config)._Config__secret))))
    assert {"a", "b", "c", "d", "e", "f", "g", "g.a", "g.b", "h", "i", "i.a", "i.a.a", "i.a.b", "i.c", "i.c.c", "i.c.d", "j", "j.a", "j.b"} == set(iter(cast(Any, DynamicConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}, cast(Any, Config)._Config__secret))))


def test_keys() -> None:
    assert set() == cast(Any, DynamicConfig({}, cast(Any, Config)._Config__secret)).keys()
    assert {"a", "b", "b.x"} == cast(Any, DynamicConfig({"a": 1, "b": {"x": 3}}, cast(Any, Config)._Config__secret)).keys()
    assert {"a", "b", "c", "d", "e", "f", "g", "g.a", "g.b", "h", "i", "i.a", "i.a.a", "i.a.b", "i.c", "i.c.c", "i.c.d", "j", "j.a", "j.b"} == cast(Any, DynamicConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}, cast(Any, Config)._Config__secret)).keys()


def test_items() -> None:
    assert [] == cast(Any, DynamicConfig({}, cast(Any, Config)._Config__secret)).items()
    assert [("a", 1), ("b.x", 3)] == cast(Any, DynamicConfig({"a": 1, "b": {"x": 3}}, cast(Any, Config)._Config__secret)).items()
    assert [("a", 1), ("b", 0.1), ("c", None), ("d", True), ("e", "test"), ("f", [1, 2, 3]), ("g.a", 1), ("g.b", 2), ("h", [[1, 2], [3, 4]]), ("i.a.a", 1), ("i.a.b", 2), ("i.c.c", 3), ("i.c.d", 4), ("j.a", [1, 2]), ("j.b", [3, 4])] == cast(Any, DynamicConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}, cast(Any, Config)._Config__secret)).items()


def test_getattr() -> None:
    config = cast(Any, DynamicConfig({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    print(config.keys())
    assert config.a == 1
    assert config.b.c == 3
    with pytest.raises(AttributeError):
        config.c


def test_setattr() -> None:
    config = cast(Any, DynamicConfig({}, cast(Any, Config)._Config__secret))
    config.a = 1
    assert config.a == 1
    config.b = cast(Any, {"c": 3})
    config.b.c = 4
    assert config.b.c == 4
    config.freeze()
    with pytest.raises(ReadOnlyError):
        config.a = 2
    with pytest.raises(ReadOnlyError):
        config.b = cast(Any, 3)
    with pytest.raises(ReadOnlyError):
        config.b.c = 4


def test_del() -> None:
    config = cast(Any, DynamicConfig({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    with pytest.raises(AttributeError):
        del config.x
    del config.a
    assert "a" not in config
    del config.b.c
    assert "c" not in config.b
    assert "b" in config
    config.freeze()
    with pytest.raises(AttributeError):
        del config.x
    with pytest.raises(ReadOnlyError):
        del config.b


def test_getitem() -> None:
    config = cast(Any, DynamicConfig({"a": {"b": 1}}, cast(Any, Config)._Config__secret))
    assert config["a.b"] == 1
    with pytest.raises(AttributeError):
        config["b"]
    with pytest.raises(AttributeError):
        config["a.c"]
    with pytest.raises(AttributeError):
        config["b.b"]


def test_setitem() -> None:
    config = cast(Any, DynamicConfig({}, cast(Any, Config)._Config__secret))
    config["a"] = {"b": 1}
    config["a.b"] = 2
    assert config.a.b == 2
    config.freeze()
    with pytest.raises(ReadOnlyError):
        config["a.b"] = 3
    with pytest.raises(ReadOnlyError):
        config["a.c"] = 3


def test_delitem() -> None:
    config = cast(Any, DynamicConfig({"a": {"b": 1}}, cast(Any, Config)._Config__secret))
    with pytest.raises(AttributeError):
        del config["b"]
    with pytest.raises(AttributeError):
        del config["a.c"]
    del config["a.b"]
    assert "b" not in config.a
    config.freeze()
    with pytest.raises(AttributeError):
        del config["b"]
    with pytest.raises(ReadOnlyError):
        del config["a"]


def test_clone() -> None:
    config = DynamicConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}, cast(Any, Config)._Config__secret)
    clone = config.clone()
    assert config.keys() == clone.keys()
    for key in config.keys():
        print(key, config[key], clone[key])
        assert config[key] == clone[key]
        if not isinstance(config[key], (type(None), int, float, str)):
            assert config[key] is not clone[key]


def test_to_dict() -> None:
    dict_ = {"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}}
    config = DynamicConfig(cast(Dict[str, ConfigEntryType], dict_), cast(Any, Config)._Config__secret)
    assert config.to_dict() == dict_


def test_readonly() -> None:
    config = cast(Any, DynamicConfig({}, cast(Any, Config)._Config__secret))
    assert not config.readonly
    config.a = 1
    config.a = 2
    del config.a
    config.freeze()
    assert config.readonly
    with pytest.raises(ReadOnlyError):
        config.a = 1
    with pytest.raises(ReadOnlyError):
        config.a = 2
    with pytest.raises(AttributeError):
        del config.a
