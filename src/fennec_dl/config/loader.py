from __future__ import annotations

from abc import abstractmethod
from io import StringIO
from pathlib import Path
from typing import Any, Dict, TextIO, Type, TypeVar, Union, cast

from fennec_dl.config.config import Config, ConfigEntryType
from fennec_dl.config.dynamic_config import DynamicConfig
from fennec_dl.errors.config_loading_error import ConfigLoadingError


T = TypeVar("T", bound=Config)


class Loader:
    @classmethod
    def load_dynamic(cls: Type[Loader], path: Union[str, Path]) -> Any:
        try:
            with open(path, "r", encoding="UTF-8") as file:
                dict_ = cls._load(file)
        except:
            raise ConfigLoadingError(f"Failed to load configuration from {path}")
        return DynamicConfig(dict_, cast(Any, Config)._Config__secret)

    @classmethod
    def load_static(cls: Type[Loader], path: Union[str, Path], config_type: Type[T]) -> T:
        try:
            with open(path, "r", encoding="UTF-8") as file:
                dict_ = cls._load(file)
        except:
            raise ConfigLoadingError(f"Failed to load configuration from {path}")
        return config_type(dict_, cast(Any, Config)._Config__secret)

    @classmethod
    def parse_dynamic(cls: Type[Loader], string: str) -> Any:
        try:
            dict_ = cls._load(StringIO(string))
        except:
            raise ConfigLoadingError(f"Failed to parse configuration")
        return DynamicConfig(dict_, cast(Any, Config)._Config__secret)

    @classmethod
    def parse_static(cls: Type[Loader], string: str, config_type: Type[T]) -> T:
        try:
            dict_ = cls._load(StringIO(string))
        except:
            raise ConfigLoadingError(f"Failed to parse configuration")
        return config_type(dict_, cast(Any, Config)._Config__secret)

    @staticmethod
    @abstractmethod
    def _load(stream: TextIO) -> Dict[str, ConfigEntryType]:
        ...
