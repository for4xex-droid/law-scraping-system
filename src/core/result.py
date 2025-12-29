from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T
    is_success: bool = True


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E
    is_success: bool = False


Result = Union[Ok[T], Err[E]]
