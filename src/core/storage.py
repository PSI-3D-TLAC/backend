\
\
\
\
\
\
\
\
from __future__ import annotations

from itertools import count
from threading import RLock
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, TypeVar

T = TypeVar("T")

class Repository:
\

    def __init__(self, name: str) -> None:
        self.name = name
        self._items: Dict[int, Any] = {}
        self._ids = count(start=1)
        self._lock = RLock()

    def next_id(self) -> int:
        with self._lock:
            return next(self._ids)

    def add(self, entity: Any) -> Any:
        with self._lock:
            if getattr(entity, "id", None) is None:
                entity.id = next(self._ids)
            else:
                                                                       
                self._ids = count(start=max(entity.id + 1, len(self._items) + 2))
            self._items[entity.id] = entity
            return entity

    def get(self, entity_id: int) -> Optional[Any]:
        return self._items.get(entity_id)

    def require(self, entity_id: int) -> Any:
        from .exceptions import NotFoundError

        obj = self._items.get(entity_id)
        if obj is None:
            raise NotFoundError(f"{self.name} with id={entity_id} not found")
        return obj

    def remove(self, entity_id: int) -> bool:
        with self._lock:
            return self._items.pop(entity_id, None) is not None

    def all(self) -> List[Any]:
        return list(self._items.values())

    def find(self, predicate: Callable[[Any], bool]) -> List[Any]:
        return [e for e in self._items.values() if predicate(e)]

    def first(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        for e in self._items.values():
            if predicate(e):
                return e
        return None

    def __iter__(self) -> Iterator[Any]:
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

class Database:
\

    def __init__(self) -> None:
        self._repos: Dict[str, Repository] = {}

    def repo(self, name: str) -> Repository:
        if name not in self._repos:
            self._repos[name] = Repository(name)
        return self._repos[name]

    def names(self) -> Iterable[str]:
        return self._repos.keys()

                                                   
db = Database()
