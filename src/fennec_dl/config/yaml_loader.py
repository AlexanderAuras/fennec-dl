from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, TextIO, cast

import yaml

from fennec_dl.config.loader import Loader


class YAMLLoader(Loader):
    @staticmethod
    def _load(stream: TextIO, _root: bool = True) -> "Config":  # type: ignore
        class _Loader(yaml.Loader):
            pass

        def load_intern(path: Path) -> "Config":  # type: ignore
            if not path.is_absolute():
                path = Path(stream.name).parent.joinpath(path).resolve()
            with open(path, "r", encoding="UTF-8") as stream2:
                return YAMLLoader._load(stream2, False)

        _Loader.add_constructor("!include", lambda l, n: load_intern(Path(cast(str, l.construct_scalar(cast(yaml.ScalarNode, n))))))

        class _Reference:
            def __init__(self, path: str) -> None:
                super().__init__()
                self.path = path.split(".")

        _Loader.add_constructor("!ref", lambda l, n: _Reference(cast(str, l.construct_scalar(cast(yaml.ScalarNode, n)))))

        def resolve_references(element: Any, _full_config: Optional[Mapping[str, Any]] = None) -> Any:
            if _full_config is None:
                _full_config = element
            if isinstance(element, _Reference):
                value = _full_config
                for path_part in element.path:
                    value = cast(Mapping[str, Any], value)[path_part]
                return value
            elif isinstance(element, Mapping):
                return {k: resolve_references(v, _full_config) for k, v in element.items()}
            elif isinstance(element, Sequence):
                return [resolve_references(x, _full_config) for x in element]
            return element

        data = yaml.load(stream, Loader=_Loader)
        if not isinstance(data, Mapping):
            raise RuntimeError("Configuration root element must be a mapping")
        if _root:
            data = resolve_references(data)

        return data
