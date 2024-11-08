# -*- coding: utf-8 -*-
# @Time    : 2024/11/2 16:11
# @Author  : BXZDYG
# @Software: PyCharm
# @File    : params
# @Comment :
from fastapi import Cookie, Query, WebSocket, FastAPI, Body, Header
# from typing import TypeVar
from fastapi_channels.types import ChannelName

able_parse_models = [Cookie, WebSocket, ChannelName, Body, Header, str]
# fastapi特色的请求体中有Path、Query和Form没有被我们考虑因为ws连接建立这几个就是固定的值,除非之后真的fastapi-channel真的夺舍了@app.websocket的这个接口
# 为什么将这些放在函数的参数上面，除了根据参数进行处理外就是为了生成API文档

# from fastapi_channels import add_channel
# from fastapi_channels.channels import Channel

# channel = Channel()
app = FastAPI()
# add_channel(
#     app,
#     url="redis://:r1e3d1i4s520@192.168.129.128:6379/14",
#     limiter_url="redis://:r1e3d1i4s520@192.168.129.128:6379/14"
# )


# @app.websocket('/ws')  # 如果用户很反感两者之间的反复调用，那么是不是可以直接在add_channel中帮助用户直接注册，只需要写下面的就行了(可选项？)
# async def ws_endpoint(websocket: WebSocket):
#     # await websocket.accept()
#     # async for message in websocket.iter_text():
#     #     print(message)
#     await channel.connect(websocket)

# @channel.action()

# @app.get("",response_model_by_alias=True)
@app.websocket('/ws')
async def message(
        websocket: WebSocket,
        channel_: ChannelName,
        data: dict={"data":1},
        token: str = Query(),
        user_id: int = Cookie(default=1),
):
    print(channel_)
    print(data)
    print(token)
    print(user_id)
    # 疑问建立websocket连接时query可以不可以变，变更的效果?
    print(websocket.query_params)
    print(websocket.session)
    print(websocket.cookies)
    from pprint import pprint
    pprint(websocket.scope)


#
# @channel.action()
# async def message(
#         websocket: WebSocket,
#         channel_: ChannelName,
#         original_text: str,
#         # fastapi中这里会被直接当作Query,我这里想来点不一样的，这样写就直接返回原来的str类型，
#         # 算了还是从Query中解析拿到数据吧另起一个，
#         token: str = Query(),
#         user_id: int = Cookie(),
# ):
#     # 疑问建立websocket连接时query可以不可以变，变更的效果?
#     print(websocket.query_params)
#     print(websocket.session)
#     print(websocket.cookies)
#     from pprint import pprint
#     pprint(websocket.scope)


# from fastapi import FastAPI, Request
#
# app = FastAPI()
#
#
# @app.post("/upload/")
# async def upload_data(request: Request):
#     # 获取请求体的原始字节数据
#     raw_data = await request.body()
#
#     # 打印或处理原始数据
#     print(raw_data)
#
#     # 返回数据长度作为响应
#     return {"data_length": len(raw_data)}
#
#
import uvicorn

uvicorn.run(app)
