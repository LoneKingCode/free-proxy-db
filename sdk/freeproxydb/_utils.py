from __future__ import annotations

from typing import Iterable, Optional, Union


def join_csv(value: Union[str, Iterable[str], None]) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return ",".join(str(item).strip() for item in value if str(item).strip())


def https_param(value: Optional[Union[bool, int, str]]) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)
