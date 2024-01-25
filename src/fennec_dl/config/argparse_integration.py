import argparse
import itertools
from typing import List, Optional, Set, TypeVar

from fennec_dl.config.config import Config


def add_overwrite_args(config: Config, parser: argparse.ArgumentParser, exclude: Optional[Set[str]] = None, include: Optional[Set[str]] = None) -> None:
    for key, value in config.items():
        if include is not None and key not in include:
            continue
        if exclude is not None and key in exclude:
            continue
        if type(value) in [type(None), bool]:
            parser.add_argument("--" + key, action="extend", nargs="*", default=[], dest=key.replace(".", "_"), type=bool)
        else:
            parser.add_argument("--" + key, action="extend", nargs="*", default=[], dest=key.replace(".", "_"), type=type(value))


T = TypeVar("T", bound=Config)


def process_overwrite_args(config: T, args: argparse.Namespace) -> List[T]:
    overwrites = []
    for attr_name, attr in args.__dict__.items():
        if attr_name.startswith("_"):
            continue
        if attr == []:
            continue
        overwrites.append([(attr_name, x) for x in attr])
    configs = []
    for overwrite_combi in map(dict, itertools.product(*overwrites)):
        clone = config.clone()
        for key in clone.keys():
            if key.replace(".", "_") in overwrite_combi.keys():
                clone[key] = overwrite_combi[key.replace(".", "_")]
        configs.append(clone)
    return configs
