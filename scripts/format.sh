#!/usr/bin/env bash
set -x

ruff check fastapi-channels tests docs_src scripts --fix
ruff format fastapi-channels tests docs_src scripts
