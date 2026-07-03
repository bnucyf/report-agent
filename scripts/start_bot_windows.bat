@echo off
chcp 65001 >nul
echo ========================================
echo   智能报表机器人 - 启动 (Windows)
echo ========================================
echo.

REM 激活虚拟环境
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo [警告] 虚拟环境不存在，使用系统 Python。
)

REM 检查 .env
if not exist .env (
    echo [错误] .env 文件不存在！请先运行 install_windows.bat
    pause
    exit /b 1
)

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
