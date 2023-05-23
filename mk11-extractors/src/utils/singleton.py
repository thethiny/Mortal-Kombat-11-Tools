from typing import Any


class Singleton(type):
    _SINGLETON = None
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls._SINGLETON is None:
            cls._SINGLETON = super().__call__(*args, **kwargs)
        return cls._SINGLETON