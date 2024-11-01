# -*- coding: utf-8 -*-
from functools import wraps
from typing import Optional, Any

from fastapi_channels.exceptions import ActionIsDeprecated
from fastapi_channels.permission import BasePermission
from fastapi_channels.types import DecoratedCallable


def action(
        name: Optional[str] = None,
        permission: Optional[Any] = None,
        detached: bool = False,
        deprecated: bool = False,
) -> DecoratedCallable:
    if detached:
        raise NotImplementedError(
            'Sorry, the detached function has not been implemented yet and is currently only used for placeholder')

    def decorator(func):
        _name = name if name else func.__name__
        func.action = (_name, func.__doc__)
        perm_desc = 'Allow Anyone'
        if isinstance(permission, type) and issubclass(permission, BasePermission):
            perm_desc = permission.__doc__ or permission.has_permission.__doc__
        elif callable(permission):
            perm_desc = permission.__doc__
        elif isinstance(permission, bool):
            if not permission:
                perm_desc = 'Not Allow Anyone'
        func.permission = (permission, perm_desc)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if deprecated:
                raise ActionIsDeprecated(error_msg=f"The action '{_name}' is deprecated.", close=False)
            return await func(*args, **kwargs)

        # func.call = wrapper
        return wrapper

    return decorator
