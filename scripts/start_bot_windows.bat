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

REM ===== 清理旧进程 =====
REM 注意：batch 文件中 %% 才是字面量 %，否则 cmd.exe 会把 %...% 当环境变量！
REM 使用 Python 脚本精确查找并终止旧 dingtalk_bot 进程（避免 WMIC % 转义问题）

echo [步骤1] 检查旧进程...
REM 用 PowerShell + CIM 查找并终止所有包含 dingtalk_bot 的 python.exe 进程
REM 注意：不用 WMIC —— 用户机器上 wmic 可能已弃用（Windows 11 24H2+ 默认禁用）
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'dingtalk_bot\.bot' } | ForEach-Object { Write-Host (\"  Killing PID=\" + $_.ProcessId + \" cmd=\" + $_.CommandLine); Stop-Process -Id $_.ProcessId -Force }"
echo.

timeout /t 1 /nobreak >nul

REM 检查关键依赖是否已安装，缺失则自动安装
REM 同时验证 dingtalk-stream SDK 的实际 API（防止版本差异导致 bot.py 运行时失败）
echo [步骤2] 检查依赖...
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
echo [步骤3] 启动钉钉机器人...
echo 按 Ctrl+C 停止
echo.

python -m dingtalk_bot.bot

echo.
if errorlevel 1 (
    echo [错误] 机器人启动失败，请检查 outputs\bot.log
) else (
    echo [提示] 机器人已停止运行。
)
echo.
pause
