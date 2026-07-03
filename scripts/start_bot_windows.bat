@echo off
chcp 65001 >nul

REM 切换到脚本所在目录的上一级(项目根目录),确保相对路径正确
pushd %~dp0\.. >nul
if errorlevel 1 (
    echo [错误] 无法定位项目根目录
    pause
    exit /b 1
)

echo ========================================
echo   智能报表机器人 - 启动 (Windows)
echo ========================================
echo.

REM 如果虚拟环境不存在，先执行安装脚本
if not exist .venv\Scripts\activate.bat (
    echo [提示] 虚拟环境不存在，先执行安装...
    call scripts\install_windows.bat
    if errorlevel 1 (
        echo [错误] 安装失败，无法启动机器人。
        pause
        exit /b 1
    )
    echo.
    echo [提示] 安装完成，继续启动机器人...
    echo.
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 检查 .env
if not exist .env (
    echo [错误] .env 文件不存在！请先运行 install_windows.bat
    pause
    exit /b 1
)

REM 检查是否有旧进程仍在运行（防止多实例冲突导致消息不稳定）
wmic process where "commandline like '%dingtalk_bot.bot%' and name='python.exe'" get processid 2>nul | findstr /r "[0-9]" >nul 2>&1
if not errorlevel 1 (
    echo [警告] 检测到已有 dingtalk_bot 进程在运行！
    echo [警告] 多实例同时运行会导致消息回复不稳定（消息随机分发给旧/新实例）。
    echo.
    echo 正在终止旧进程...
    wmic process where "commandline like '%dingtalk_bot.bot%' and name='python.exe'" call terminate 2>nul
    timeout /t 2 /nobreak >nul
    echo [提示] 旧进程已终止。
    echo.
)

REM 检查关键依赖是否已安装，缺失则自动安装
REM 同时验证 dingtalk-stream SDK 的实际 API（防止版本差异导致 bot.py 运行时失败）
python -c "import dingtalk_stream; from dingtalk_stream import DingTalkStreamClient, AckMessage; from dingtalk_stream.credential import Credential; from dingtalk_stream.chatbot import ChatbotMessage, ChatbotHandler; import apscheduler, dotenv, requests, yaml" >nul 2>&1
if errorlevel 1 (
    echo [提示] 检测到依赖缺失或 SDK API 不兼容，正在自动安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络连接或 requirements.txt。
        pause
        exit /b 1
    )
    echo [提示] 依赖安装完成。
) else (
    echo [提示] 依赖检查通过。
)

echo.

REM 设置 UTF-8 输出编码，防止中文日志在 GBK 控制台乱码
set PYTHONIOENCODING=utf-8

REM 进入 app 目录启动机器人
cd app
echo 正在启动钉钉机器人...
echo 按 Ctrl+C 停止
echo.

python -m dingtalk_bot.bot

if errorlevel 1 (
    echo.
    echo [错误] 机器人启动失败，请检查 outputs\bot.log
    pause
)
