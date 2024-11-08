# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from typing import TypeVar, AsyncIterator, Any, Optional, Sequence, Callable, Union

from broadcaster import Broadcast, BroadcastBackend
from fastapi import FastAPI, APIRouter
from fastapi_limiter.depends import WebSocketRateLimiter

from fastapi_channels.channels import FastAPIChannel
from fastapi_channels.permission import BasePermission
from fastapi_channels.throttling import ws_default_callback

ParentT = TypeVar("ParentT", APIRouter, FastAPI)


def add_channel(
        parent: ParentT,
        *,
        debug: bool = False,
        add_exception_handlers: bool = True,
        # init
        url: Optional[str] = None,
        backend: Optional[BroadcastBackend] = None,
        broadcast: Optional[Broadcast] = None,
        # fastapi-limiter
        limiter_url: Optional[str] = None,
        redis=None,
        prefix: str = "fastapi-channel",
        identifier: Optional[Callable] = None,
        http_callback: Optional[Callable] = None,
        ws_callback: Callable = ws_default_callback,
        # permission 权限
        permission_classes: Optional[Sequence[Union[BasePermission, str]]] = None,
        # throttling 限流器
        throttle_classes: Optional[WebSocketRateLimiter] = None,
        # pagination 分页器
        # pagination_class: Optional[Sequence] = None,
        # authentication
        query_token_key: Optional[str] = None,
        cookie_token_key: Optional[str] = None
) -> ParentT:
    router = parent.router if isinstance(parent, FastAPI) else parent  # type: ignore[attr-defined]
    _original_lifespan_context = router.lifespan_context

    # if pagination_class:
    #     import warnings
    #     warnings.warn("Sorry,it's Under development")

    @asynccontextmanager
    async def lifespan(app: Any) -> AsyncIterator[Any]:
        # 在原有的生命周期的基础上又追加了自己的生命周期 # 合并原来的生命周期
        try:
            await FastAPIChannel.init(
                # debug=debug,
                url=url,
                backend=backend,
                broadcast=broadcast,
                limiter_url=limiter_url,
                redis=redis,
                prefix=prefix,
                identifier=identifier,
                http_callback=http_callback,
                ws_callback=ws_callback,
                permission_classes=permission_classes,
                throttle_classes=throttle_classes,
                # pagination_class=pagination_class,
                query_token_key=query_token_key,
                cookie_token_key=cookie_token_key
            )
            async with _original_lifespan_context(app) as maybe_state:
                yield maybe_state
        finally:
            await FastAPIChannel.close()

    router.lifespan_context = lifespan

    if debug:
        import warnings
        warnings.warn("Sorry,it's Under development")
    if add_exception_handlers:
        from fastapi_channels.exceptions import WebSocketException, WebSocketExceptionHandler
        parent.add_exception_handler(WebSocketException, WebSocketExceptionHandler)  # type:ignore
    return parent
