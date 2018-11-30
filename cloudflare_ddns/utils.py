import inspect
from contextlib import suppress
from functools import wraps
# noinspection PyProtectedMember
from typing import Any, Dict, Optional, _SpecialForm

__all__ = ["get_str", "enforce_types"]


def get_str(data: Dict[str, Any],
            key: str,
            default: Optional[str] = None) -> Optional[str]:
    value = data.get(key)
    return value if isinstance(value, str) else default


# https://stackoverflow.com/a/50622643/3673259
def enforce_types(call):
    spec = inspect.getfullargspec(call)

    def check_types(*args, **kwargs):
        parameters = dict(zip(spec.args, args))
        parameters.update(kwargs)
        for name, value in parameters.items():
            # Assume un-annotated parameters can be any type
            with suppress(KeyError):
                type_hint = spec.annotations[name]
                # No check for typing.Any, typing.Union, typing.ClassVar
                # noinspection PyProtectedMember
                if isinstance(type_hint, _SpecialForm):
                    continue
                try:
                    actual_type = type_hint.__origin__
                except AttributeError:
                    actual_type = type_hint
                # noinspection PyProtectedMember
                if isinstance(actual_type, _SpecialForm):
                    # case of typing.Union[…] or typing.ClassVar[…]
                    actual_type = type_hint.__args__

                if not isinstance(value, actual_type):
                    raise TypeError(
                        f"Unexpected type for \"{name}\" "
                        f"(expected {type_hint} but found {type(value)})"
                    )

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check_types(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    if inspect.isclass(call):
        call.__init__ = decorate(call.__init__)
        return call

    return decorate(call)
