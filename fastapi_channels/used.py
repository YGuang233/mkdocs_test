# -*- coding: utf-8 -*-
# @Time    : 2024/10/26 17:58
# @Author  : BXZDYG
# @Software: PyCharm
# @File    : used
# @Comment :
from fastapi_channels.channels import Channel


class GroupChannel(Channel):
    """
    群聊频道的常用封装
    """
    max_connection: int = 200


class PersonChannel(Channel):
    """
    私聊频道的常用封装
    """
    max_connection: int = 2
