from __future__ import annotations

import inspect
import typing
import warnings
from typing import Any, Callable, Dict, List, Literal, Optional, Set, Tuple, Type, TypeVar, Union, cast

from fennec_dl.config.config import BasicConfigEntryType, Config
from fennec_dl.config.dynamic_config import ConfigEntryType
from fennec_dl.errors.config_loading_error import ConfigLoadingError
from fennec_dl.errors.invalid_operation_error import InvalidOperationError
from fennec_dl.errors.readonly_error import ReadOnlyError


class StaticConfig(Config):
    def __init__(self, dict_: Dict[str, ConfigEntryType], secret: object = None) -> None:
        super().__init__(dict_, secret)

        # Check type annotations
        def validate_type_hint(hint: Type[Any], in_list: bool = False) -> bool:
            if inspect.isclass(hint) and issubclass(hint, Config):
                return not in_list
            elif typing.get_origin(hint) == list:
                return validate_type_hint(typing.get_args(hint)[0], True)
            elif hint in [bool, int, float, str]:
                return True
            elif typing.get_origin(hint) == Union:
                if len(list(filter(lambda x: x != type(None), typing.get_args(hint)))) == 0:
                    return False
                for arg in typing.get_args(hint):
                    if arg == type(None):
                        continue
                    if not validate_type_hint(arg):
                        return False
                return True
            elif typing.get_origin(hint) == Literal:
                return validate_type_hint(type(typing.get_args(hint)[0]))
            else:
                return False

        type_hints = typing.get_type_hints(self.__class__)
        for attr_name, type_hint in sorted(type_hints.items()):
            if not validate_type_hint(type_hint):
                raise AttributeError(f'Invalid type hint "{type_hint}" for attribute "{attr_name}"')

        for attr_name, attr in sorted(self.__class__.__dict__.items()):
            if attr_name.startswith("_") or inspect.isclass(attr):
                continue
            elif inspect.isfunction(attr):
                warnings.warn(f'StaticConfig classes should not contain methods or functions (found method/function "{attr_name}")')
            elif attr_name not in type_hints.keys():
                warnings.warn(f'Attribute "{attr_name}" is not annotated and will be ignored')

        # Initialize
        def convert(value: Any, hint: Type[Any], in_list: bool = False) -> Any:
            if inspect.isclass(hint) and issubclass(hint, Config):
                if in_list:
                    raise ConfigLoadingError(f'Lists of configs are not allowed (found at "{type_hints[attr_name]})"')
                return hint(value, cast(Any, Config)._Config__secret)
            elif typing.get_origin(hint) == list:
                if not isinstance(value, List):
                    raise ConfigLoadingError(f'Attribute "{attr_name}" has type "{type(dict_[attr_name])}" but should match "{type_hints[attr_name]}"')
                return [convert(entry, typing.get_args(hint)[0], True) for entry in value]
            elif hint in [bool, int, float, str]:
                if not isinstance(value, hint):
                    raise ConfigLoadingError(f'Attribute "{attr_name}" has type "{type(dict_[attr_name])}" but should match "{type_hints[attr_name]}"')
                return value
            elif typing.get_origin(hint) == Union:
                for arg in typing.get_args(hint):
                    if arg == type(None):
                        if value is None:
                            return None
                        continue
                    try:
                        return convert(value, arg)
                    except:
                        pass
                raise ConfigLoadingError(f'Attribute "{attr_name}" has type "{type(dict_[attr_name])}" but should match "{type_hints[attr_name]}"')
            elif typing.get_origin(hint) == Literal:
                if value != typing.get_args(hint)[0]:
                    raise ConfigLoadingError(f'Attribute "{attr_name}" has type "{type(dict_[attr_name])}" but should match "{type_hints[attr_name]}"')
                return value

        if len(dict_.keys() - type_hints.keys()) > 0:
            warnings.warn(f"Superfluous config values \"{(chr(34)+', '+chr(34)).join(sorted(dict_.keys() - type_hints.keys()))}\"")
        if len(type_hints.keys() - dict_.keys()) > 0:
            raise ConfigLoadingError(f"Missing config values \"{(chr(34)+', '+chr(34)).join(sorted(type_hints.keys() - dict_.keys()))}\"")

        for attr_name, type_hint in sorted(type_hints.items()):
            value = convert(dict_[attr_name], type_hint)
            self.__dict__[attr_name] = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Config):
            return False
        for key, value in self.items():
            if key not in other:
                return False
            if value != other[key]:
                return False
        return True

    def __setattr__(self, key: str, value: ConfigEntryType) -> None:
        if self.readonly:
            raise ReadOnlyError("Config is read-only")
        if key not in self:
            raise AttributeError(f'Config has no attribute "{key}"')
        super().__setattr__(key, value)

    def __delattr__(self, fqn: str) -> Any:
        raise InvalidOperationError()

    def keys(self, _prefix: str = "") -> Set[str]:
        keys = set()
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, Config):
                keys.add(("" if len(_prefix) == 0 else _prefix + ".") + k)
                keys = keys.union(v.keys(("" if len(_prefix) == 0 else _prefix + ".") + k))
            else:
                keys.add(("" if len(_prefix) == 0 else _prefix + ".") + k)
        return keys

    def items(self, _prefix: str = "") -> List[Tuple[str, BasicConfigEntryType]]:
        items = []
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, Config):
                items.extend(v.items(("" if len(_prefix) == 0 else _prefix + ".") + k))
            else:
                items.append((("" if len(_prefix) == 0 else _prefix + ".") + k, v))
        return items

    def __do_by_fqn(self, fqn: str, _i: int, func: Union[Callable[[Any, str], Optional[Any]], Callable[[Any, str, Any], Optional[Any]]], *params: Any) -> Any:
        fqn_parts = fqn.strip().split(".")[_i:]
        print(fqn, _i, fqn_parts)
        if not hasattr(self, "__dict__") or fqn_parts[0] not in self.__dict__.keys():
            raise AttributeError(f'Config has no attribute "{".".join(fqn_parts[:(_i+2)])}"')
        if len(fqn_parts) == 1:
            return func(self, fqn_parts[0], *params)
        return getattr(self, fqn_parts[0]).__do_by_fqn(fqn, _i + 1, func, *params)

    def __getitem__(self, fqn: str) -> Any:
        return self.__do_by_fqn(fqn, 0, getattr)

    def __setitem__(self, fqn: str, value: Any) -> Any:
        if fqn not in self:
            raise AttributeError(f'Config has no attribute "{fqn}"')
        return self.__do_by_fqn(fqn, 0, setattr, value)

    def __delitem__(self, fqn: str) -> Any:
        raise InvalidOperationError()

    def _to_dict(self, value: ConfigEntryType) -> ConfigEntryType:
        if isinstance(value, StaticConfig):
            return value.to_dict()
        else:
            return value

    def to_dict(self) -> Dict[str, ConfigEntryType]:
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            result[key] = self._to_dict(value)
        return result

    def freeze(self) -> None:
        super().freeze()
        for attr in self.__dict__.values():
            if isinstance(attr, Config):
                attr.freeze()
