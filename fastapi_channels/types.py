# -*- coding: utf-8 -*-
# @Time    : 2024/10/26 17:41
# @Author  : BXZDYG
# @Software: PyCharm
# @File    : types
# @Comment : 类型定义
from typing import (
    Any,
    AsyncIterator,
    Callable,
    # Coroutine,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    # Set,
    # Tuple,
    # Type,
    Union,
    TypeVar,
    AsyncContextManager,
    Generator
)
# from starlette.websockets import WebSocketType

_T = TypeVar("_T")
WebSocketType = TypeVar("WebSocketType")
ChannelName = TypeVar('ChannelName', bound=str)
ChannellessLifespan = Callable[[WebSocketType, ChannelName], AsyncContextManager[None]]
ChannelfulLifespan = Callable[[WebSocketType, ChannelName], AsyncContextManager[Mapping[str, Any]]]
Lifespan = Union[ChannellessLifespan[WebSocketType, ChannelName], ChannelfulLifespan[WebSocketType, ChannelName]]

Scope = Dict[str, Any]
Receive = Callable[[], Any]
Send = Callable[[Dict[str, Any]], Any]
DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])