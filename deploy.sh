#!/bin/bash

# 安装依赖
poetry install --extras server

# 在后台运行服务器，并将输出重定向到日志文件
nohup poetry run python main.py --server --host 0.0.0.0 --port 8000 > zerepy.log 2>&1 &

# 打印进程 ID
echo $! > zerepy.pid
echo "Server started with PID $(cat zerepy.pid)"