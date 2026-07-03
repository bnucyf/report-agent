# 智能报表机器人 - 部署文档

## 概述

本项目是一个基于 SQL Server 的数据库分析工具，提供两种使用方式：
1. **Streamlit 网页端**：本地浏览器访问的交互式分析仪表盘
2. **钉钉机器人**：在钉钉单聊/群聊中通过对话或定时任务获取分析数据

采用 **GitHub 开源 + 用户自部署** 模式，不需要服务器，所有数据在用户本地处理。

---

## 环境要求

| 组件 | 要求 |
|------|------|
| 操作系统 | Windows 10/11（现阶段优先支持） |
| Python | 3.10+ |
| 数据库 | SQL Server（用友 T+ / U8 等 ERP 数据库均可） |
| 网络 | 能访问钉钉 API（出站 HTTPS） |
| 浏览器 | Edge 或 Chrome（PDF 报告生成用） |

---

## 部署步骤（约 15 分钟）

### 第 1 步：克隆代码

```bash
git clone https://github.com/bnucyf/report-agent.git
cd report-agent
```

### 第 2 步：钉钉后台创建应用（5 分钟）

详见 [钉钉应用配置指南](./DINGTALK_APP_SETUP.md)，简要步骤：

1. 登录 [钉钉开发者后台](https://open-dev.dingtalk.com)
2. **应用开发** → **企业内部应用** → **创建应用**
   - 应用名称：智能报表（自定义）
   - 应用描述：数据库分析机器人
3. **应用能力** → **机器人** → 开启
   - 消息接收模式：选择 **Stream 模式**
4. **权限管理** → 申请以下权限：
   - 企业内机器人发送消息（`qyapi_robot_sendmsg`）
   - 互动卡片实例读写
   - 文件上传
   - 通讯录只读（用于用户身份）
5. **基础信息** → 记下以下 4 个凭证：
   - `AppKey`（即 Client ID）
   - `AppSecret`（即 Client Secret）
   - `AgentId`
   - 企业 CorpId（在「我的企业」页面查看）
6. **应用发布** → 选择本企业发布 → 等待审批通过

### 第 3 步：数据库账号准备（2 分钟）

在 SQL Server 中创建只读账号：

```sql
-- 创建只读用户
CREATE LOGIN report_reader WITH PASSWORD = 'YourStrongPassword!2024';
USE YourDatabase;
CREATE USER report_reader FOR LOGIN report_reader;
ALTER ROLE db_datareader ADD MEMBER report_reader;
```

测试连接：
```bash
sqlcmd -S your_db_host,1433 -U report_reader -P YourStrongPassword!2024 -Q "SELECT 1"
```

> ⚠️ **强烈建议使用只读账号**，不要使用 `sa`。

### 第 4 步：安装机器人服务（5 分钟）

**Windows 用户：**

1. 双击 `scripts/install_windows.bat`
   - 自动创建虚拟环境 `.venv`
   - 自动安装所有 Python 依赖
   - 自动从 `.env.example` 复制 `.env`
2. 用记事本（或 VS Code）编辑 `.env`，填入：
   - 4 个钉钉凭证
   - 5 个数据库参数
   - （可选）管理员 UserId

**手动安装（Linux/macOS）：**

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入凭证
```

### 第 5 步：启动机器人（3 分钟）

**方式 A：前台运行（推荐首次使用）**

双击 `scripts/start_bot_windows.bat`

看到以下输出表示成功：
```
[INFO] 智能报表机器人启动中...
[INFO] access_token 获取成功，凭证有效
[INFO] 🤖 机器人已就绪，等待消息...
```

**方式 B：注册为 Windows 服务（后台常驻）**

```bash
# 需要安装 nssm（Non-Sucking Service Manager）
nssm install ReportBot "C:\path\to\.venv\Scripts\python.exe" "-m dingtalk_bot.bot"
nssm set ReportBot AppDirectory "C:\path\to\report-agent\app"
nssm set ReportBot AppStdout "C:\path\to\report-agent\outputs\bot.log"
nssm set ReportBot AppStderr "C:\path\to\report-agent\outputs\bot.log"
nssm start ReportBot
```

### 第 6 步：验证

1. 在钉钉搜索机器人名称，发起单聊
2. 发送「帮助」→ 收到使用说明
3. 发送「扫描」→ 启动数据库扫描
4. 发送「生产用料」→ 收到分析数据
5. 发送「质量」→ 收到数据质量诊断
6. 发送「字段」→ 收到字段资产盘点
7. 发送「报告」→ 收到 PDF/Excel 下载链接

---

## 可选配置

### 定时任务

编辑 `config/scheduler.yaml`，配置自动推送：

```yaml
scheduler:
  timezone: Asia/Shanghai
  jobs:
    - name: 每日生产用料推送
      cron: "0 8 * * 1-5"           # 工作日早 8 点
      target: chat_group
      chat_id: "oc_xxxxx"            # 钉钉群 ID
      action: send_production_usage
```

**获取群 chat_id**：在钉钉群设置 → 群管理 → 群信息中查看，或在群中 @机器人 发任意消息后查看 `outputs/bot.log` 中的 `conversationId`。

### Streamlit 网页端（可选）

```bash
# 激活虚拟环境后
cd app
streamlit run main.py
```

浏览器访问 `http://localhost:8501`

---

## 常见问题

### Q: 机器人启动报 "缺少钉钉凭证"
A: 检查 `.env` 文件是否正确填写了 `DINGTALK_CLIENT_ID` 和 `DINGTALK_CLIENT_SECRET`。

### Q: 收不到消息回复
A: 
1. 检查钉钉后台应用是否已发布
2. 检查机器人消息接收模式是否为 Stream
3. 查看 `outputs/bot.log` 是否有错误日志
4. 确认机器人可见范围包含当前用户

### Q: 扫描很慢
A: 在 `.env` 中调低 `DB_SAMPLE_ROWS`（默认 200，可调到 100）。480 张表 × 200 行采样约需 10-30 分钟。

### Q: PDF 生成失败
A: 确保系统安装了 Edge 或 Chrome 浏览器，或在 `.env` 中设置 `EDGE_PATH` / `CHROME_PATH` 指向浏览器可执行文件。

### Q: 数据库连接超时
A: 
1. 确认 SQL Server 1433 端口可访问
2. 在 `.env` 中调高 `DB_QUERY_TIMEOUT`（默认 10 秒）
3. 检查防火墙规则

---

## 目录结构

```
report-agent/
├── app/                          # 主代码
│   ├── db.py                     # 数据库连接
│   ├── scan.py                   # 扫描引擎
│   ├── data_loader.py            # 快照加载
│   ├── business_analysis.py      # 业务分析
│   ├── profiling.py              # 数据质量诊断
│   ├── field_inventory_report.py # 字段资产报告
│   ├── reports.py                # 报告生成
│   ├── main.py                   # Streamlit 入口
│   ├── views/                    # Streamlit 页面
│   ├── analysis/                 # 分析函数
│   └── dingtalk_bot/             # 钉钉机器人模块
│       ├── bot.py                # Stream 入口
│       ├── credential.py         # 凭证管理
│       ├── router.py             # 意图路由
│       ├── card_builder.py       # 卡片构建
│       ├── interactive_card.py   # 互动卡片
│       ├── report_pusher.py      # 报告推送
│       ├── scheduler.py          # 定时任务
│       └── handlers/             # 各主题处理器
├── config/                       # 配置文件
│   └── scheduler.yaml            # 定时任务配置
├── scripts/                      # 脚本
│   ├── install_windows.bat       # 一键安装
│   └── start_bot_windows.bat     # 启动机器人
├── outputs/                      # 输出目录（自动创建）
│   ├── snapshots/                # CSV/JSON 快照
│   ├── reports/                  # HTML/PDF/Excel 报告
│   └── bot.log                   # 机器人日志
├── docs/                         # 文档
├── .env.example                  # 环境变量模板
├── requirements.txt              # Python 依赖
├── LICENSE                       # MIT 协议
└── README.md
```

---

## 技术支持

- 查看 `outputs/bot.log` 获取详细错误日志
- 查看 `outputs/scan.log` 获取扫描日志
- GitHub Issues: https://github.com/bnucyf/report-agent/issues
