# -*- coding: utf-8 -*-
from functools import wraps
from importlib.metadata import version
from math import ceil
from typing import Optional, Callable

from fastapi import WebSocket
from packaging import version as pkg_version

from fastapi_channels.exceptions import RateLimitExceeded

_current_version = version('fastapi-limiter')
_required_version = '0.1.6'

if pkg_version.parse(_current_version) > pkg_version.parse(_required_version):
    raise ImportError(
        f"fastapi-limiter version {_current_version} is higher than the required version {_required_version}. "
        "Please ensure compatibility with your application."
    )

from fastapi_limiter.depends import WebSocketRateLimiter


async def ws_default_callback(ws: WebSocket, pexpire: int) -> None:
    """
    default callback when too many requests
    :param ws:
    :param pexpire: The remaining milliseconds
    :return:
    """
    expire = ceil(pexpire / 1000)
    raise RateLimitExceeded(error_msg=f"Too Many Requests. Retry after {expire} seconds.")


async def ws_action_default_callback(ws: WebSocket, pexpire: int) -> None:
    """
    default callback when too many requests
    :param ws:
    :param pexpire: The remaining milliseconds
    :return:
    """
    expire = ceil(pexpire / 1000)
    raise RateLimitExceeded(error_msg=f"Too Many Requests. Retry after {expire} seconds.", close=False)


def limiter(
        times: int = 1,
        milliseconds: int = 0,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        identifier: Optional[Callable] = None,
        callback: Callable = ws_action_default_callback,
        _limiter: WebSocketRateLimiter = None
        # ratelimit: WebSocketRateLimiter = None
):
    def decorator(func):
        if not hasattr(func, 'action'):
            raise AttributeError(
                "The function is missing the 'action' attribute."
                " Ensure that the @action decorator is applied before @limiter."
            )

        action_name, _ = func.action

        @wraps(func)
        async def wrapper(*args, **kwargs):
            _channel = kwargs.get('channel', None)
            _context_key = [action_name]
            if _channel:
                _context_key.insert(0, _channel)
            context_key = ':'.join(_context_key)
            # fastapi-limiter:ws:127.0.0.1:/person/1:ws_example_user_channel_1:message
            # fastapi-limiter:ws:127.0.0.1:/person/1:message
            _additional_key = {}
            if identifier: _additional_key['identifier'] = identifier
            ratelimit = _limiter or WebSocketRateLimiter(
                times=times,
                milliseconds=milliseconds,
                seconds=seconds,
                minutes=minutes,
                hours=hours,
                callback=callback,
                **_additional_key
            )
            await ratelimit(ws=kwargs.get('websocket'), context_key=context_key)
            return await func(*args, **kwargs)

        func.call = wrapper
        return wrapper

    return decorator
# TODO: 以后还是不使用limiter，准备废弃
#
