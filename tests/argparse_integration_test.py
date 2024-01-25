import argparse
from typing import Optional

from fennec_dl.config.argparse_integration import add_overwrite_args, process_overwrite_args
from fennec_dl.config.static_config import StaticConfig
from fennec_dl.config.yaml_loader import YAMLLoader


class MockConfig(StaticConfig):
    class MockConfig2(StaticConfig):
        c: int
        d: Optional[bool]

    a: int
    b: MockConfig2


def test_add_overwrite_args() -> None:
    static_config = YAMLLoader.parse_static("a: 2\nb:\n  c: 4\n  d: null\n", MockConfig)
    parser = argparse.ArgumentParser()
    add_overwrite_args(static_config, parser)
    args = parser.parse_args(["--a", "1", "--a", "3", "--b.c", "3", "--b.c", "5", "--b.d", "True"])
    assert args.a == [1, 3]
    assert args.b_c == [3, 5]
    assert args.b_d == [True]

    dynamic_config = YAMLLoader.parse_dynamic("a: 2\nb:\n  c: 4\n  d: null\n")
    parser = argparse.ArgumentParser()
    add_overwrite_args(dynamic_config, parser)
    args = parser.parse_args(["--a", "1", "--a", "3", "--b.c", "3", "--b.c", "5", "--b.d", "True"])
    assert args.a == [1, 3]
    assert args.b_c == [3, 5]
    assert args.b_d == [True]


def test_process_overwrite_args() -> None:
    static_config = YAMLLoader.parse_static("a: 2\nb:\n  c: 4\n  d: null\n", MockConfig)
    parser = argparse.ArgumentParser()
    add_overwrite_args(static_config, parser)
    args = parser.parse_args(["--a", "1", "--a", "3", "--b.c", "3", "--b.c", "5", "--b.d", "True"])
    configs = process_overwrite_args(static_config, args)
    assert len(configs) == 4
    assert configs[0].a == 1
    assert configs[0].b.c == 3
    assert configs[0].b.d == True
    assert configs[1].a == 1
    assert configs[1].b.c == 5
    assert configs[1].b.d == True
    assert configs[2].a == 3
    assert configs[2].b.c == 3
    assert configs[2].b.d == True
    assert configs[3].a == 3
    assert configs[3].b.c == 5
    assert configs[3].b.d == True

    dynamic_config = YAMLLoader.parse_dynamic("a: 2\nb:\n  c: 4\n  d: null\n")
    parser = argparse.ArgumentParser()
    add_overwrite_args(dynamic_config, parser)
    args = parser.parse_args(["--a", "1", "--a", "3", "--b.c", "3", "--b.c", "5", "--b.d", "True"])
    configs = process_overwrite_args(dynamic_config, args)
    assert len(configs) == 4
    assert configs[0].a == 1
    assert configs[0].b.c == 3
    assert configs[0].b.d == True
    assert configs[1].a == 1
    assert configs[1].b.c == 5
    assert configs[1].b.d == True
    assert configs[2].a == 3
    assert configs[2].b.c == 3
    assert configs[2].b.d == True
    assert configs[3].a == 3
    assert configs[3].b.c == 5
    assert configs[3].b.d == True
