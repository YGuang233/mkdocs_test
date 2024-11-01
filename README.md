# FastAPI-Channels

<p align="center">
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python&logoColor=white&labelColor=101010" alt="">
  </a>
  <a href="https://fastapi.tiangolo.com">
    <img src="https://img.shields.io/badge/FastAPI-0.111.0-00a393?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=101010" alt="">
  </a>
</p>
&nbsp;&nbsp;本项目主要为FastAPI的WebSocket接口通讯提供快捷方便的处理和管理库。特色在于少量代码就能实现基本的聊天室的功能。
<br>
&nbsp;&nbsp;本项目又集成了优秀的第三方库如:broadcaster、fastapi-limiter。在本项目均保留了自定义使用这些库的位置。
<br>
&nbsp;&nbsp;一般的，用户使用本库仅需考虑如何编写 `action` 来实现传输的目标,和对应的`action`访问的权限类即可

# 案例演示

```python
# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, WebSocket
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from fastapi_channels import add_channel, action, limiter
from fastapi_channels.used import PersonChannel, GroupChannel
from fastapi_channels.exceptions import PermissionDenied
from fastapi_channels.permission import AllowAny
from fastapi_channels.utils.path import TemplatePath

templates = Jinja2Templates(TemplatePath)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[dict]:
    print('FastAPI-Channel startUp!')
    yield {"name": "main.py"}
    print('FastAPI-Channel shutDown!')


app = FastAPI(lifespan=lifespan)
add_channel(
    app,
    url="redis://localhost:6379",
    limiter_url="redis://localhost:6379"
)


@app.get('/')
async def homepage(request: Request):
    template = "broadcaster.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


class PersonalChatRoom(PersonChannel):
    @limiter(times=2, seconds=3000)  # 请求超额 但是不关闭websocket
    @action('count')  # request exceeded but websocket not closed
    async def get_count(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        await self.broadcast_to_personal(
            websocket, str(await self.get_connection_count(channel)))

    @action('message')  # 广播消息 # broadcast message
    async def send_message(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        await self.broadcast_to_channel(channel, await self.encode(data))

    @action(deprecated=True)  # action被废弃不关闭websocket # action abandoned, websocket not closed
    async def deprecated_action(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        await self.broadcast_to_personal(websocket, '发送消息')

    @action("permission_denied", permission=False)  # 返回权限不足的错误响应 # return error response with insufficient permissions
    async def permission_false(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        await self.broadcast_to_channel(channel, data.get('message'))

    @action(permission=AllowAny)  # 抛出异常不但关闭websocket # raise an exception not only closes websocket
    async def error(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        raise PermissionDenied(close=False)

    @action()  # 通过action关闭websocket连接 # close websocket connection through action
    async def close(self, websocket: WebSocket, channel: str, data: dict, **kwargs):
        await websocket.close()


person_chatroom = PersonalChatRoom()


@app.websocket("/person", name='chatroom_ws')
async def person_chatroom_ws(websocket: WebSocket):
    await person_chatroom.connect(websocket)


class GroupChatRoom(GroupChannel):
    ...


group_chatroom = GroupChatRoom()


@app.websocket("/group", name='chatroom_ws')
async def group_chatroom_ws(websocket: WebSocket):
    await group_chatroom.connect(websocket)


async def join_room(websocket: WebSocket, channel: str, ):
    await group_chatroom.broadcast_to_personal(websocket, 'Join successfully')


async def leave_room(websocket: WebSocket, channel: str, ):
    # await group_chatroom.broadcast_to_personal(websocket, 'leave successfully')
    # error: 👆如果通过action离开房间会输出这个，但是客户端直接关闭会诱发websocket没有进行连接
    # 所以这一步只能`broadcast_to_channel`或者后续处理,而不是`broadcast_to_personal`
    #
    # error: 👆 If you leave the room through an action, it will output this,
    # but if the client closes it directly, it will trigger the websocket to not connect,
    # so this step can only be 'broadcast_to-uchannel' or processed later,
    # rather than 'broadcast_to-personal'`
    await group_chatroom.broadcast_to_channel(channel, 'leave successfully')


group_chatroom.add_event_handler('join', join_room)
group_chatroom.add_event_handler('leave', leave_room)


@limiter(seconds=3, times=1)
@group_chatroom.action('message')  # 消息发送解析和#装饰器异常
async def send_message(websocket: WebSocket, channel: str, data: dict, **kwargs):
    await group_chatroom.broadcast_to_channel(channel, data.get('message'))


@group_chatroom.action('error_true')  # 消息发送解析和异常
async def send_error_and_close(websocket: WebSocket, channel: str, data: dict, **kwargs):
    raise PermissionDenied(close=True)


@group_chatroom.action('error_false')  # 消息发送解析和异常
async def send_error(websocket: WebSocket, channel: str, data: dict, **kwargs):
    raise PermissionDenied(close=False)


@group_chatroom.action()  # 客户端发请求主机关闭
async def close(websocket: WebSocket, channel: str, data: dict, **kwargs):
    await websocket.close()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, port=8000)

```

# 功能和目标清单

- [x] 权限认证
    - [ ] 基础的用户验证的方案
- [x] 自定义异常和全局捕获,并且抛出异常可控连接状态
- [ ] 分页器
- [x] 限流器
    - [x] fastapi-limiter
- [ ] 兼容多种请求类型的支持
    - [ ] Text
    - [x] JSON
    - [ ] Binary
- [x] 频道事件
    - [x] 频道生命周期(lifespan、on_event)
- [ ] 可自定义数据传输的结构
    - [ ] 请求体
    - [ ] 响应体
    - [ ] 分页器
- [ ] 持久化
    - [ ] 历史记录的存储
    - [ ] 历史记录的读取
- [ ] 后台管理
    - [ ] Api接口控制
    - [ ] 定时管理
- [ ] 国际化开发。locales 基于依赖项对响应体的信息加以全局的语言选择
- [ ] 测试环境搭建
- [ ] 完善的doc

# 安装

```shell
pip install fastapi-channels
```

