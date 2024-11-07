# -*- coding: utf-8 -*-
from typing import (
    Any,
    Callable,
    Dict,
    Mapping,
    Union,
    TypeVar,
    AsyncContextManager
)
_T = TypeVar("_T")
WebSocketType = TypeVar("WebSocketType")
ChannelName = TypeVar('ChannelName', bound=str)
ChannellessLifespan = Callable[[WebSocketType, ChannelName], AsyncContextManager[None]]
ChannelfulLifespan = Callable[[WebSocketType, ChannelName], AsyncContextManager[Mapping[str, Any]]]
Lifespan = Union[ChannellessLifespan[WebSocketType, ChannelName], ChannelfulLifespan[WebSocketType, ChannelName]]

Scope = Dict[str, Any]
Receive = Callable[[], Any]
Send = Callable[[Dict[str, Any]], Any]