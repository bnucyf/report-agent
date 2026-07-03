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

REM 检查关键依赖是否已安装，缺失则自动安装
python -c "import dingtalk_stream, apscheduler, dotenv, requests, yaml" >nul 2>&1
if errorlevel 1 (
    echo [提示] 检测到依赖缺失，正在自动安装...
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
