from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple, cast

from fennec_dl.config.config import BasicConfigEntryType, Config, ConfigEntryType
from fennec_dl.errors.config_loading_error import ConfigLoadingError
from fennec_dl.errors.readonly_error import ReadOnlyError


class DynamicConfig(Config):
    def __init__(self, dict_: Dict[str, ConfigEntryType], secret: object = None) -> None:
        super().__init__(dict_, secret)
        self.__dict__["_DynamicConfig__data"] = {k: DynamicConfig._parse(v) for k, v in dict_.items()}

    @staticmethod
    def _parse(value: ConfigEntryType, in_list: bool = False) -> Any:
        if isinstance(value, Dict):
            if in_list:
                raise ConfigLoadingError(f'Lists of configs are not allowed (found at "{value}")')
            return DynamicConfig(value, cast(Any, Config)._Config__secret)
        elif isinstance(value, List) and not isinstance(value, str):
            return [DynamicConfig._parse(x, True) for x in value]
        else:
            return value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Config):
            return False
        for key, value in self.items():
            if key not in other:
                return False
            if value != other[key]:
                return False
        return True

    def keys(self, _prefix: str = "") -> Set[str]:
        keys = set()
        for k, v in self.__dict__["_DynamicConfig__data"].items():
            if isinstance(v, DynamicConfig):
                keys.add(("" if len(_prefix) == 0 else _prefix + ".") + k)
                keys = keys.union(v.keys(("" if len(_prefix) == 0 else _prefix + ".") + k))
            else:
                keys.add(("" if len(_prefix) == 0 else _prefix + ".") + k)
        return keys

    def items(self, _prefix: str = "") -> List[Tuple[str, BasicConfigEntryType]]:
        items = []
        for k, v in self.__dict__["_DynamicConfig__data"].items():
            if isinstance(v, DynamicConfig):
                items.extend(v.items(("" if len(_prefix) == 0 else _prefix + ".") + k))
            else:
                items.append((("" if len(_prefix) == 0 else _prefix + ".") + k, v))
        return items

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_") and name in self.__dict__:
            return self.__dict__[name]
        if name not in self.__dict__["_DynamicConfig__data"]:
            raise AttributeError(f'Config has no attribute "{name}"')
        return self.__dict__["_DynamicConfig__data"][name]

    def __setattr__(self, name: str, value: ConfigEntryType) -> None:
        if name.startswith("_") and name in self.__dict__:
            self.__dict__[name] = value
            return
        if self.readonly:
            raise ReadOnlyError("Config is read-only")
        self.__dict__["_DynamicConfig__data"][name] = DynamicConfig._parse(value)

    def __delattr__(self, name: str) -> None:
        if name not in self.__dict__["_DynamicConfig__data"]:
            raise AttributeError(f'Config has no attribute "{name}"')
        if self.readonly:
            raise ReadOnlyError("DynamicConfig is read-only")
        del self.__dict__["_DynamicConfig__data"][name]

    def __getitem__(self, fqn: str) -> Any:
        return self.__get_parent_dict_by_fqn(fqn).__getattr__(fqn.split(".")[-1])

    def __setitem__(self, fqn: str, value: ConfigEntryType) -> None:
        self.__get_parent_dict_by_fqn(fqn).__setattr__(fqn.split(".")[-1], value)

    def __delitem__(self, fqn: str) -> None:
        self.__get_parent_dict_by_fqn(fqn).__delattr__(fqn.split(".")[-1])

    def __get_parent_dict_by_fqn(self, fqn: str) -> DynamicConfig:
        fqn_parts = fqn.strip().split(".")
        parent = self
        for i, part in enumerate(fqn_parts[:-1]):
            if part not in parent:
                raise AttributeError(f'Config has no attribute "{".".join(fqn_parts[:i])}"')
            parent = getattr(parent, part)
        return parent

    def _to_dict(self, value: ConfigEntryType) -> ConfigEntryType:
        if isinstance(value, DynamicConfig):
            return value.to_dict()
        else:
            return value

    def to_dict(self) -> Dict[str, ConfigEntryType]:
        result = {}
        for key, value in self.__dict__["_DynamicConfig__data"].items():
            result[key] = self._to_dict(value)
        return result

    def freeze(self) -> None:
        super().freeze()
        for entry in self.__dict__["_DynamicConfig__data"].values():
            if isinstance(entry, DynamicConfig):
                entry.freeze()
