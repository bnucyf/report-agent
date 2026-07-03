# 智能报表机器人 (Report Agent)

基于 SQL Server 元数据扫描的智能数据分析与钉钉机器人推送系统。

## 功能概览

- **数据库只读扫描**：扫描 SQL Server 全库表结构、字段、索引，识别业务候选表
- **业务分析**：生产加工用料明细、库存收发存、采购到货、财务往来等专题
- **数据质量诊断**：空值、空字符串、异常日期、负数值抽样检测
- **字段资产盘点**：全库字段语义分类、模块归属、时间/金额/数量字段识别
- **多端呈现**：
  - Streamlit 网页应用（本地 8501 端口）
  - 钉钉机器人（单聊 + 群聊，Stream 模式）
  - HTML / PDF / Excel 报告导出
- **定时推送**：APScheduler 内嵌，支持 cron 配置，推群或推单聊

## 快速开始

### 环境要求

- Python 3.10+
- SQL Server（已开放只读账号）
- 钉钉企业内部应用（机器人 + Stream 模式）

### 安装

```bash
git clone https://github.com/bnucyf/report-agent.git
cd report-agent
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入数据库和钉钉凭证
```

### 运行网页端

```bash
cd app
streamlit run main.py
```

### 运行钉钉机器人

```bash
cd app
python -m dingtalk_bot.bot
```

## 文档

- [部署指南](docs/DEPLOY.md)
- [钉钉应用配置](docs/DINGTALK_APP_SETUP.md)
- [使用手册](docs/USER_GUIDE.md)

## 技术栈

| 层 | 技术 |
|---|---|
| 数据库 | SQL Server (pymssql) |
| 网页 | Streamlit |
| 钉钉 | dingtalk-stream-sdk-python (Stream 模式) |
| 定时任务 | APScheduler |
| 报告 | HTML / PDF / Excel (openpyxl) |

## License

MIT
