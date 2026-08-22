"""Memoize hashable-arg Phase 11/12 builder and status-summary calls.

Default (zero-arg) builder calls re-enter the entire upstream cascade. Caching
those hashable-argument paths, then returning a ``deepcopy``, keeps ``doctor``
and the status-summary snapshot behavior-identical while collapsing the
repeated work. Calls with unhashable mappings (caller-supplied records) skip
the cache and run the original function.
"""

from __future__ import annotations

import copy
import functools
import inspect
from collections.abc import Callable, MutableMapping
from typing import Any


def memoize_hashable_calls(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Cache ``fn`` when every argument is hashable; deepcopy the cached value."""

    cache: dict[tuple[Any, ...], Any] = {}

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            key = (args, tuple(sorted(kwargs.items())))
            hash(key)
        except TypeError:
            return fn(*args, **kwargs)
        if key not in cache:
            cache[key] = fn(*args, **kwargs)
        return copy.deepcopy(cache[key])

    wrapper.cache_clear = cache.clear  # type: ignore[attr-defined]
    return wrapper


def _should_memoize(name: str, obj: object) -> bool:
    if not inspect.isfunction(obj):
        return False
    if name.startswith("_") or name.startswith("validate_") or name.startswith("Phase"):
        return False
    if name.endswith("_status_summary"):
        return True
    if name.startswith(("phase11", "phase12", "rejected_phase11", "rejected_phase12")):
        return True
    return False


def install_builder_cache(module_globals: MutableMapping[str, Any]) -> None:
    """Wrap public builders and ``*_status_summary`` functions in ``module_globals``."""

    for name, obj in list(module_globals.items()):
        if _should_memoize(name, obj):
            module_globals[name] = memoize_hashable_calls(obj)
