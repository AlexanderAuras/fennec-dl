from typing import Any, Dict, List, Optional, Union, cast

import pytest

from fennec_dl.config.config import Config, ConfigEntryType
from fennec_dl.config.dynamic_config import DynamicConfig
from fennec_dl.config.static_config import StaticConfig
from fennec_dl.errors.config_loading_error import ConfigLoadingError
from fennec_dl.errors.invalid_operation_error import InvalidOperationError
from fennec_dl.errors.readonly_error import ReadOnlyError


class MockConfigEmpty(StaticConfig):
    pass


class MockConfigSmall(StaticConfig):
    class MockConfigSmall2(StaticConfig):
        c: int

    a: int
    b: MockConfigSmall2


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
    k: Union[bool, int]


def test_init() -> None:
    _ = MockConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}, cast(Any, Config)._Config__secret)
    with pytest.raises(ConfigLoadingError):
        _ = MockConfig({"k": [{"a": 1, "b": 2}, {"c": 3, "d": 4}]}, cast(Any, Config)._Config__secret)

    with pytest.raises(ConfigLoadingError):
        _ = MockConfigSmall({"a": 1, "b": {"c": "3"}}, cast(Any, Config)._Config__secret)

    class TypeErrorMockConfig(StaticConfig):
        a: List[Dict[str, int]]

    with pytest.raises(AttributeError):
        _ = TypeErrorMockConfig({"a": {"b": [1, 2, 3]}}, cast(Any, Config)._Config__secret)


def test_eq() -> None:
    a = MockConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}, cast(Any, Config)._Config__secret)
    b = MockConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}, cast(Any, Config)._Config__secret)
    c = DynamicConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}, cast(Any, Config)._Config__secret)
    d = MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret)
    assert a == b
    assert a == c
    assert a != d


def test_len() -> None:
    assert 0 == len(MockConfigEmpty({}, cast(Any, Config)._Config__secret))
    assert 3 == len(MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    assert 21 == len(MockConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}, cast(Any, Config)._Config__secret))


def test_contains() -> None:
    config = cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    assert "a" in config
    assert "b" in config
    assert "b.c" in config
    assert "c" not in config
    assert "c.x" not in config


def test_iter() -> None:
    assert set() == set(iter(cast(Any, MockConfigEmpty({}, cast(Any, Config)._Config__secret))))
    assert {"a", "b", "b.c"} == set(iter(cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))))
    assert {"a", "b", "c", "d", "e", "f", "g", "g.a", "g.b", "h", "i", "i.a", "i.a.a", "i.a.b", "i.c", "i.c.c", "i.c.d", "j", "j.a", "j.b", "k"} == set(iter(cast(Any, MockConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}, cast(Any, Config)._Config__secret))))


def test_keys() -> None:
    assert set() == cast(Any, MockConfigEmpty({}, cast(Any, Config)._Config__secret)).keys()
    assert {"a", "b", "b.c"} == cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret)).keys()
    assert {"a", "b", "c", "d", "e", "f", "g", "g.a", "g.b", "h", "i", "i.a", "i.a.a", "i.a.b", "i.c", "i.c.c", "i.c.d", "j", "j.a", "j.b", "k"} == cast(Any, MockConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}, cast(Any, Config)._Config__secret)).keys()


def test_items() -> None:
    assert [] == cast(Any, MockConfigEmpty({}, cast(Any, Config)._Config__secret)).items()
    assert [("a", 1), ("b.c", 3)] == cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret)).items()
    assert [("a", 1), ("b", 0.1), ("c", None), ("d", True), ("e", "test"), ("f", [1, 2, 3]), ("g.a", 1), ("g.b", 2), ("h", [[1, 2], [3, 4]]), ("i.a.a", 1), ("i.a.b", 2), ("i.c.c", 3), ("i.c.d", 4), ("j.a", [1, 2]), ("j.b", [3, 4]), ("k", 1)] == cast(Any, MockConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}, cast(Any, Config)._Config__secret)).items()


def test_getattr() -> None:
    config = cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    print(config.keys())
    assert config.a == 1
    assert config.b.c == 3
    with pytest.raises(AttributeError):
        config.c


def test_setattr() -> None:
    config = cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    config.a = 2
    assert config.a == 2
    with pytest.raises(AttributeError):
        config.c = 5
    config.freeze()
    with pytest.raises(ReadOnlyError):
        config.a = 2
    with pytest.raises(ReadOnlyError):
        config.b = cast(Any, 3)
    with pytest.raises(ReadOnlyError):
        config.b.c = 4


def test_del() -> None:
    config = cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    with pytest.raises(InvalidOperationError):
        del config.x
    with pytest.raises(InvalidOperationError):
        del config.a
    config.freeze()
    with pytest.raises(InvalidOperationError):
        del config.x
    with pytest.raises(InvalidOperationError):
        del config.a


def test_getitem() -> None:
    config = cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    assert config["b.c"] == 3
    with pytest.raises(AttributeError):
        config["c"]
    with pytest.raises(AttributeError):
        config["a.c"]
    with pytest.raises(AttributeError):
        config["b.b"]


def test_setitem() -> None:
    config = cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    config["a"] = 2
    assert config.a == 2
    config.freeze()
    with pytest.raises(ReadOnlyError):
        config["a"] = 3
    with pytest.raises(AttributeError):
        config["a.c"] = 3


def test_delitem() -> None:
    config = cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    with pytest.raises(InvalidOperationError):
        del config["b"]
    with pytest.raises(InvalidOperationError):
        del config["a"]
    config.freeze()
    with pytest.raises(InvalidOperationError):
        del config["b"]
    with pytest.raises(InvalidOperationError):
        del config["a"]


def test_clone() -> None:
    config = MockConfig({"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}, cast(Any, Config)._Config__secret)
    clone = config.clone()
    assert config.keys() == clone.keys()
    for key in config.keys():
        assert config[key] == clone[key]
        if not isinstance(config[key], (type(None), int, float, str)):
            assert config[key] is not clone[key]


def test_to_dict() -> None:
    dict_ = {"a": 1, "b": 0.1, "c": None, "d": True, "e": "test", "f": [1, 2, 3], "g": {"a": 1, "b": 2}, "h": [[1, 2], [3, 4]], "i": {"a": {"a": 1, "b": 2}, "c": {"c": 3, "d": 4}}, "j": {"a": [1, 2], "b": [3, 4]}, "k": 1}
    config = MockConfig(cast(Dict[str, ConfigEntryType], dict_), cast(Any, Config)._Config__secret)
    assert config.to_dict() == dict_


def test_readonly() -> None:
    config = cast(Any, MockConfigSmall({"a": 1, "b": {"c": 3}}, cast(Any, Config)._Config__secret))
    assert not config.readonly
    config.a = 2
    config.freeze()
    assert config.readonly
    with pytest.raises(ReadOnlyError):
        config.a = 2
