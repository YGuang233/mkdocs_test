# -*- coding: utf-8 -*-
# @Time    : 2024/10/29 19:38
# @Author  : BXZDYG
# @Software: PyCharm
# @File    : setup
# @Comment :
import setuptools  # 导入setuptools打包工具

from fastapi_channels import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name="fastapi-channels",
    version=__version__,
    author="BXZDYG",
    author_email="banxingzhedeyangguang@gmail.com",
    description="This project provides a simple setup for creating WebSocket communication channels using FastAPI.",
    # 包的简述
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/YGuang233/fastapi-channels",
    packages=setuptools.find_packages(),
    install_requires=[
        'fastapi>=0.110.0',
        'broadcaster>=0.3.1',
        'fastapi_limiter<=0.1.6'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
