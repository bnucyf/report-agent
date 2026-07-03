# 智能报表原型运行说明

## 1. 配置数据库连接

复制 `.env.example` 为 `.env`，填写数据库连接信息：

```text
DB_HOST=113.45.41.170
DB_PORT=1433
DB_NAME=UFTData662308_000088
# Previous account can be retained as comments in local .env when switching accounts.
# DB_USER_OLD=sa
# DB_PASSWORD_OLD=change_me
DB_USER=test
DB_PASSWORD=change_me
DB_QUERY_TIMEOUT=10
DB_SAMPLE_ROWS=200
```

正式环境建议使用专用只读账号，不建议使用 `sa`。

## 2. 安装依赖

使用隔离 Python 环境安装：

```bash
C:/Users/22411/.workbuddy/binaries/python/envs/default/Scripts/python.exe -m pip install -r requirements.txt
```

## 3. 执行只读扫描

### 3.1 概览页三种扫描模式

- **开始/继续扫描**：在“概览”页点击按钮。`app/scan.py` 会对**所有非噪声业务候选表（约 1308 张）** 逐表做字段、索引和质量 profiling。
- **暂停扫描**：扫描进行中（`state.current_table` 非空）时可点击。会在**当前表扫描完成后**停止，不会中断正在 profiling 的表。
- **全部重新扫描**：清空 `outputs/scan_state.json` 和 `outputs/scan_progress.json`，从第 1 张表开始。点击后立即启动新扫描任务。

### 3.2 命令行直接执行

```bash
C:/Users/22411/.workbuddy/binaries/python/envs/default/Scripts/python.exe app/scan.py
```

支持参数：
- `--reset` 启动前清空所有扫描进度（等价于页面上的“全部重新扫描”）
- `--pause` 写暂停信号（等价于页面上的“暂停扫描”）

### 3.3 扫描输出

- `outputs/snapshots/tables_*.csv`
- `outputs/snapshots/columns_*.csv`
- `outputs/snapshots/indexes_*.csv`
- `outputs/snapshots/business_candidates_*.csv`
- `outputs/snapshots/quality_issues_*.csv`（按逐表进度汇总）
- `outputs/scan_state.json` — 整体状态
- `outputs/scan_progress.json` — **逐表进度**（每张表 status、开始/结束时间、问题数）
- `outputs/scan_control.json` — 暂停/重置控制信号
- `outputs/scan.log` — 后台进程输出日志

### 3.4 断点续扫原理

`scan.py` 启动时读取 `scan_progress.json`，跳过 `status == "done"` 的表，只处理 `pending / failed` 的表。任意时刻点击暂停，下一次再点“继续扫描”会从最后完成的下一张表开始。

## 4. 启动 Demo 页面

```bash
C:/Users/22411/.workbuddy/binaries/python/envs/default/Scripts/streamlit.exe run app/main.py
```

页面采用一级菜单 + 二级子菜单结构：

- `概览`：展示数据资产规模、业务模块分布、数据库大表概览，以及“开始分析”按钮。
- `业务分析`：包含管理层经营总览、生产加工用料、库存收发存、采购到货分析、财务往来分析、主数据资产分析。
- `数据质量`：包含质量总览、字段完整性、异常值检测、单据关联风险、业务一致性、主数据质量。
- `报告导出`：集中下载最新 HTML 报告和 CSV 快照。

> 注意：`app/views/` 是页面渲染模块，不是 Streamlit 的多页面目录，因此不会生成额外的英文导航页。

## 5. 验证检查

修改页面或分析模块后，先执行语法检查：

```bash
C:/Users/22411/.workbuddy/binaries/python/versions/3.13.12/python.exe -m py_compile app/main.py app/data_loader.py app/menus.py app/views/*.py app/ui/*.py app/analysis/*.py
```

再使用项目虚拟环境检查关键模块导入：

```bash
PYTHONPATH=app C:/Users/22411/.workbuddy/binaries/python/envs/default/Scripts/python.exe -c "from views import overview, business, quality, reports; from data_loader import load_snapshot_bundle; print(sorted(load_snapshot_bundle().keys()))"
```

如需端到端模拟断点续扫 + 暂停逻辑（不需要数据库），可运行：

```bash
PYTHONPATH=app C:/Users/22411/.workbuddy/binaries/python/envs/default/Scripts/python.exe scripts/test_scan_state.py
```

## 6. 数据字典字段补充

项目中包含 `TPlus160 数据字典.chm`。当前环境已用 7z 解压到 `outputs/chm_decompile/`。
要生成字段补充报告，运行：

```bash
PYTHONPATH=app C:/Users/22411/.workbuddy/binaries/python/envs/default/Scripts/python.exe app/chm_parser.py
```

输出：

- `outputs/chm_decompile/chm_descriptions.json` — 字典中所有表和字段说明
- `outputs/reports/chm_field_supplement.csv` — 与 field_inventory 合并后的补充报告

页面“报告导出”中也提供该 CSV 的下载入口。

## 7. 当前原则

1. 数据字典仅供参考，以真实数据库扫描为准。
2. 第一阶段只读，不写入生产库。
3. 抽样分析默认每表 200 行，避免影响生产库。
4. 页面分为“概览、业务分析、数据质量、报告导出”，业务分析与数据质量同等重要。
5. 业务分析和数据质量都按模块拆分，页面层只负责展示，具体计算逻辑放在 `app/analysis/`。
6. 报告中的质量问题是规则命中结果，最终是否为业务问题需要客户确认口径。
