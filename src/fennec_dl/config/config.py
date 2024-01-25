from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Set, Tuple, Union


BasicConfigEntryType = Union[type(None), bool, int, float, str]
ConfigEntryType = Union[BasicConfigEntryType, List["ConfigEntryType"], Dict[str, "ConfigEntryType"]]


class Config(ABC):
    __secret = object()

    def __init__(self, dict_: Dict[str, ConfigEntryType], secret: object = None) -> None:
        super().__init__()
        assert secret == Config.__secret
        self.__dict__["_Config__readonly"] = False

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        ...

    def __len__(self) -> int:
        return len(list(self.keys()))

    def __contains__(self, fqn: str) -> bool:
        for key in self.keys():
            if key.startswith(fqn) and (len(fqn) == len(fqn) or key[len(fqn)] == "."):
                return True
        return False

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    @abstractmethod
    def keys(self, _prefix: str = "") -> Set[str]:
        ...

    @abstractmethod
    def items(self, _prefix: str = "") -> List[Tuple[str, BasicConfigEntryType]]:
        ...

    @abstractmethod
    def __getitem__(self, fqn: str) -> Any:
        ...

    @abstractmethod
    def __setitem__(self, fqn: str, value: ConfigEntryType) -> Any:
        ...

    def clone(self) -> Config:
        return self.__class__(self.to_dict(), Config.__secret)

    @abstractmethod
    def to_dict(self) -> Dict[str, ConfigEntryType]:
        ...

    @property
    def readonly(self) -> bool:
        return self.__dict__["_Config__readonly"]

    def freeze(self) -> None:
        self.__dict__["_Config__readonly"] = True
