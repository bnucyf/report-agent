from __future__ import annotations

import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

from db import ROOT_DIR  # noqa: E402

# ---------- 子进程异常兜底：把所有未捕获异常写进 scan.log ----------
SCAN_LOG_PATH = ROOT_DIR / "outputs" / "scan.log"


def _scan_log(msg: str) -> None:
    try:
        SCAN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with SCAN_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(msg + "\n")
            fh.flush()
    except Exception:
        pass


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    _scan_log(f"[FATAL] uncaught exception:\n{msg}")
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _excepthook

from business_analysis import fetch_production_material_usage  # noqa: E402
from db import load_config  # noqa: E402
from metadata import build_column_map, scan_columns, scan_indexes, scan_tables  # noqa: E402
from profiling import profile_table  # noqa: E402
from reports import (  # noqa: E402
    SNAPSHOT_DIR,
    build_summary,
    json_default,
    render_data_map,
    render_html,
    write_csv,
)
from scan_state import (  # noqa: E402
    CONTROL_PATH,
    PROGRESS_PATH,
    STATE_PATH,
    TableProgress,
    clear_control,
    init_run,
    load_control,
    load_progress,
    load_state,
    save_progress,
    save_state,
    update_state,
    write_control,
)
from table_classifier import classify_tables  # noqa: E402


# ---------- 工具 ----------

def _now() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _is_pause_requested() -> bool:
    if not CONTROL_PATH.exists():
        return False
    try:
        data = json.loads(CONTROL_PATH.read_text(encoding="utf-8"))
        return str(data.get("action", "")) == "pause"
    except Exception:
        return False


def _progress_path_safe() -> None:
    """逐表进度文件已存在时确保不是空文件。"""
    if not PROGRESS_PATH.exists():
        save_progress({})


# ---------- 核心：逐表扫描 ----------

def collect_all_candidate_tables(tables: list[dict[str, Any]], column_map: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """基于表清单+字段信息识别非噪声业务候选表。"""
    candidates = classify_tables(tables, column_map)
    # 只取 row_count > 0 的非空业务候选
    return [c for c in candidates if int(c.get("row_count") or 0) > 0]


def profile_one_table(candidate: dict[str, Any], column_map: dict[str, list[dict[str, Any]]], sample_rows: int) -> list[dict[str, Any]]:
    schema = candidate["schema_name"]
    table = candidate["table_name"]
    key = f"{schema}.{table}"
    cols = column_map.get(key, [])[:80]
    if not cols:
        return []
    return profile_table(schema, table, cols, sample_rows)


def scan_all_candidate_tables(
    *,
    sample_rows: int,
    profile_limit: int,
    save_snapshots_every: int = 5,
) -> dict[str, Any]:
    """主循环：扫描所有非噪声业务候选表（断点续扫，可暂停）。"""
    cfg = load_config()
    print(f"[scan] database={cfg.database} host={cfg.host}:{cfg.port}", flush=True)
    print("[scan] Step 1: scanning tables list", flush=True)
    tables = scan_tables()
    print(f"[scan] total tables in catalog: {len(tables)}", flush=True)

    print("[scan] Step 2: scanning columns for all non-empty tables", flush=True)
    active_tables = [row for row in tables if int(row.get("row_count") or 0) > 0]
    active_table_names = [row["table_name"] for row in active_tables]
    columns = scan_columns(active_table_names)
    column_map = build_column_map(columns)

    print("[scan] Step 3: scanning indexes for all non-empty tables", flush=True)
    indexes = scan_indexes(active_table_names)

    print("[scan] Step 4: classifying business candidate tables", flush=True)
    candidates = collect_all_candidate_tables(tables, column_map)
    print(f"[scan] non-noise business candidates: {len(candidates)}", flush=True)

    # 初始化/恢复逐表进度
    state = load_state()
    if not state.candidate_tables or state.candidate_tables != len(candidates) or state.database_name != cfg.database:
        # 数据库不匹配 或 候选表数不一致 → 重新初始化（不重置历史 done，保持断点）
        state = init_run(
            database_name=cfg.database,
            database_host=cfg.host,
            database_port=cfg.port,
            total_tables=len(tables),
            candidate_tables=len(candidates),
        )
        print("[scan] state initialized", flush=True)
    else:
        state.is_paused = False
        state.note = "扫描进行中"
        save_state(state)
        print("[scan] resumed from previous progress", flush=True)

    progress = load_progress()
    # 给新出现的候选表补登记
    for cand in candidates:
        name = cand["full_name"]
        if name not in progress:
            progress[name] = TableProgress(table=name, status="pending")
    save_progress(progress)

    # 主循环：按顺序逐表扫描；status=done 的跳过
    done_now = 0
    for cand in candidates:
        name = cand["full_name"]
        item = progress.get(name) or TableProgress(table=name, status="pending")
        if item.status == "done":
            continue
        if _is_pause_requested():
            print(f"[scan] pause requested, stopping after {done_now} tables in this run", flush=True)
            state.is_paused = True
            state.current_table = ""
            state.note = f"已暂停：完成 {state.done_count}/{state.candidate_tables}。下次点击“开始分析”会从当前断点继续。"
            save_state(state)
            clear_control()
            return {
                "stopped": "paused",
                "done_now": done_now,
                "tables_count": len(tables),
                "columns_count": len(columns),
                "indexes_count": len(indexes),
                "candidates_count": len(candidates),
            }

        item.status = "scanning"
        item.started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state.current_table = name
        state.is_paused = False
        save_state(state)
        save_progress(progress)
        print(f"[scan] ({state.done_count + 1}/{len(candidates)}) profiling {name} ...", flush=True)

        t0 = time.time()
        try:
            issues = profile_one_table(cand, column_map, sample_rows)
            elapsed = time.time() - t0
            # 限制单表保留问题数
            trimmed = issues[:profile_limit]
            item.status = "done"
            item.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item.issue_count = len(trimmed)
            item.column_count = len(column_map.get(name, []))
            item.error = ""
            state.done_count += 1
            # 累积 issues
            accumulated = state.note if False else ""  # 不在 note 中累积
            print(f"[scan]   -> done in {elapsed:.1f}s, issues={len(trimmed)}", flush=True)
        except Exception as exc:
            item.status = "failed"
            item.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item.error = f"{type(exc).__name__}: {exc}"[:300]
            state.failed_count += 1
            print(f"[scan]   -> FAILED: {item.error}", flush=True)

        # 每张表都更新一次进度
        state.pending_count = max(state.candidate_tables - state.done_count - state.failed_count, 0)
        state.note = f"扫描中：{state.done_count + state.failed_count}/{state.candidate_tables}"
        save_state(state)
        save_progress(progress)
        done_now += 1

        # 周期性生成中间快照
        if done_now % max(1, save_snapshots_every) == 0:
            _persist_snapshots(tables, columns, indexes, candidates, progress, partial=True)
            print(f"[scan] intermediate snapshot saved after {done_now} tables", flush=True)

    state.is_complete = (state.done_count + state.failed_count) >= state.candidate_tables and state.candidate_tables > 0
    state.current_table = ""
    state.note = (
        f"已完成：成功 {state.done_count} 张，失败 {state.failed_count} 张，共 {state.candidate_tables} 张。"
        if state.is_complete else
        f"扫描停止：完成 {state.done_count + state.failed_count}/{state.candidate_tables}。"
    )
    save_state(state)
    clear_control()
    print(f"[scan] run finished. is_complete={state.is_complete}", flush=True)
    return {
        "stopped": "complete" if state.is_complete else "stopped",
        "done_now": done_now,
        "tables_count": len(tables),
        "columns_count": len(columns),
        "indexes_count": len(indexes),
        "candidates_count": len(candidates),
    }


# ---------- 快照持久化 ----------

def _accumulate_issues_from_progress(progress: dict[str, TableProgress]) -> list[dict[str, Any]]:
    """从逐表进度中汇总已扫描表的质量问题(仅用于 partial 中间快照,数据粒度较粗)。"""
    rows: list[dict[str, Any]] = []
    for item in progress.values():
        if item.status == "done" and item.issue_count > 0:
            # 仅保留数量，不复刻每条问题原文（避免进度文件过大）
            rows.append({
                "schema_name": item.table.split(".")[0] if "." in item.table else "",
                "table_name": item.table.split(".")[-1],
                "column_name": "*",
                "issue_type": "scanned_summary",
                "issue_count": item.issue_count,
                "sampled_rows": 0,
                "issue_rate": 0.0,
                "detail": f"该表扫描完成，累计问题 {item.issue_count} 条；如需明细可在数据字典或明细报告中查看。",
            })
    return rows


def _regenerate_detailed_issues(
    candidates: list[dict[str, Any]],
    column_map: dict[str, list[dict[str, Any]]],
    sample_rows: int,
    profile_limit_per_table: int = 8,
) -> list[dict[str, Any]]:
    """正式快照用：对所有已 done 的业务候选重新拉一次 profile_table 拿明细 issues。

    数据粒度：每条 schema/table/column/issue_type 一行，
    issue_type ∈ {空值, 空字符串, 异常日期, 负数值}，
    与页面 quality.py 的过滤口径一致。
    """
    from profiling import profile_table

    issues: list[dict[str, Any]] = []
    for cand in candidates:
        if int(cand.get("row_count") or 0) <= 0:
            continue
        key = cand.get("full_name") or f"{cand['schema_name']}.{cand['table_name']}"
        cols = column_map.get(key, [])[:80]
        if not cols:
            continue
        try:
            rows = profile_table(cand["schema_name"], cand["table_name"], cols, sample_rows)
        except Exception as exc:
            issues.append({
                "schema_name": cand["schema_name"],
                "table_name": cand["table_name"],
                "column_name": "*",
                "issue_type": "profile_failed",
                "issue_count": 1,
                "sampled_rows": 0,
                "issue_rate": 1.0,
                "detail": f"{type(exc).__name__}: {str(exc)[:200]}",
            })
            continue
        # 限单表保留问题数,按 issue_rate 倒序裁剪
        for item in rows[:profile_limit_per_table]:
            issues.append(item)
    # 全局再按 issue_rate 倒序,方便页面拿 Top N
    issues.sort(key=lambda r: (r.get("issue_rate", 0.0), r.get("issue_count", 0)), reverse=True)
    return issues


def _regenerate_field_inventory(stamp: str) -> dict[str, Path]:
    """正式快照用：调 field_inventory_report 的内部函数，产出 4 类资产盘点文件。

    输出：
        field_inventory_<stamp>.csv
        field_inventory_summary_<stamp>.json
        docs/database-field-analysis-report.md
        reports/database-field-analysis-report_<stamp>.html
    """
    from field_inventory_report import (
        enrich_columns,
        fetch_columns,
        fetch_tables,
        render_html,
        render_markdown,
        summarize,
        write_json,
    )

    tables = fetch_tables()
    columns = fetch_columns()
    enriched = enrich_columns(tables, columns)
    summary = summarize(tables, enriched)

    field_csv = SNAPSHOT_DIR / f"field_inventory_{stamp}.csv"
    summary_json = SNAPSHOT_DIR / f"field_inventory_summary_{stamp}.json"
    from reports import REPORT_DIR, DOCS_DIR  # noqa: WPS433
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    md_path = DOCS_DIR / "database-field-analysis-report.md"
    html_path = REPORT_DIR / f"database-field-analysis-report_{stamp}.html"

    write_csv(field_csv, enriched)
    write_json(summary_json, summary)
    md_path.write_text(render_markdown(summary, enriched), encoding="utf-8")
    html_path.write_text(render_html(summary, enriched), encoding="utf-8")

    return {
        "field_csv": field_csv,
        "field_summary_json": summary_json,
        "field_md": md_path,
        "field_html": html_path,
    }


def _regenerate_production_usage(stamp: str, limit: int = 5000) -> Path:
    """正式快照用：拉一次生产加工用料明细 → production_material_usage_<stamp>.csv。"""
    rows = fetch_production_material_usage(limit=limit)
    path = SNAPSHOT_DIR / f"production_material_usage_{stamp}.csv"
    write_csv(path, rows)
    return path


def _persist_snapshots(
    tables: list[dict[str, Any]],
    columns: list[dict[str, Any]],
    indexes: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    progress: dict[str, TableProgress],
    *,
    partial: bool,
) -> dict[str, Path]:
    """生成 CSV/JSON/HTML 快照。partial=True 时使用 _partial 后缀。"""
    stamp = _now() + ("_partial" if partial else "")
    paths = {
        "tables_csv": SNAPSHOT_DIR / f"tables_{stamp}.csv",
        "columns_csv": SNAPSHOT_DIR / f"columns_{stamp}.csv",
        "indexes_csv": SNAPSHOT_DIR / f"indexes_{stamp}.csv",
        "candidates_csv": SNAPSHOT_DIR / f"business_candidates_{stamp}.csv",
        "issues_csv": SNAPSHOT_DIR / f"quality_issues_{stamp}.csv",
        "summary_json": SNAPSHOT_DIR / f"summary_{stamp}.json",
    }
    write_csv(paths["tables_csv"], tables)
    write_csv(paths["columns_csv"], columns)
    write_csv(paths["indexes_csv"], indexes)
    write_csv(paths["candidates_csv"], candidates)
    issues_summary = _accumulate_issues_from_progress(progress)
    write_csv(paths["issues_csv"], issues_summary)
    summary = build_summary(tables, columns, candidates, issues_summary, [])
    summary["scan_mode"] = "partial" if partial else "complete"
    summary["done_count"] = sum(1 for p in progress.values() if p.status == "done")
    summary["failed_count"] = sum(1 for p in progress.values() if p.status == "failed")
    paths["summary_json"].write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=json_default),
        encoding="utf-8",
    )
    return paths


# ---------- 入口 ----------

def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        return _main_impl(argv)
    except Exception as exc:
        _scan_log(f"[FATAL] main() crashed: {type(exc).__name__}: {exc}")
        _scan_log(traceback.format_exc())
        # 把崩溃信息同时写到 scan_state.note（如果文件可写）
        try:
            state = load_state()
            state.note = f"扫描子进程崩溃: {type(exc).__name__}: {str(exc)[:200]}"
            state.is_paused = True
            save_state(state)
        except Exception:
            pass
        return 1


def _main_impl(argv: list[str]) -> int:
    cfg = load_config()

    if "--reset" in argv:
        from scan_state import reset_progress
        reset_progress()
        print("[scan] progress reset (full rescan requested)", flush=True)

    if "--pause" in argv:
        write_control("pause")
        print("[scan] pause signal written", flush=True)
        return 0

    # 单次 scan（默认）：断点续扫所有非噪声业务表
    # sample_rows 用 .env 中的 DB_SAMPLE_ROWS（默认 1000）
    sample_rows = cfg.sample_rows
    profile_limit = 8
    result = scan_all_candidate_tables(sample_rows=sample_rows, profile_limit=profile_limit)

    # 结束后生成正式快照（覆盖 partial）
    if result.get("stopped") in ("complete", "stopped", "paused"):
        # 重新拉一次最新表/字段/索引/分类（已包含在 result 内，但要重新序列化）
        tables = scan_tables()
        active_tables = [row for row in tables if int(row.get("row_count") or 0) > 0]
        columns = scan_columns([row["table_name"] for row in active_tables])
        indexes = scan_indexes([row["table_name"] for row in active_tables])
        column_map = build_column_map(columns)
        candidates = collect_all_candidate_tables(tables, column_map)
        progress = load_progress()

        # ----- 1) 基础 6 个快照 -----
        paths = _persist_snapshots(tables, columns, indexes, candidates, progress, partial=False)

        # ----- 2) 详细 issues（按 profile_table 重新拉明细，页面用得到） -----
        # 即便扫描未全部完成，对当前所有非空候选都补一份明细；既能让页面有数据，
        # 又能保证 issues 是"最近一次采样"的统计。
        detailed_issues = _regenerate_detailed_issues(
            candidates, column_map, sample_rows, profile_limit_per_table=profile_limit
        )
        # 覆盖 _persist_snapshots 写的 summary 版 issues（page 真正想看的是 detailed）
        detailed_issues_path = paths["issues_csv"]  # 复用同一文件名
        write_csv(detailed_issues_path, detailed_issues)
        print(f"[scan] detailed issues: {detailed_issues_path} (rows={len(detailed_issues)})", flush=True)

        # ----- 3) 生产加工用料明细 -----
        try:
            production_usage_path = _regenerate_production_usage(_now(), limit=5000)
            print(f"[scan] production_material_usage: {production_usage_path}", flush=True)
        except Exception as exc:
            _scan_log(f"[WARN] production_material_usage 重建失败: {type(exc).__name__}: {exc}")
            production_usage_path = None
            detailed_issues = detailed_issues  # 保持引用

        # ----- 4) 字段资产盘点（field inventory + html 报告） -----
        try:
            field_paths = _regenerate_field_inventory(_now())
            for name, p in field_paths.items():
                print(f"[scan] field_inventory.{name}: {p}", flush=True)
        except Exception as exc:
            _scan_log(f"[WARN] field_inventory 重建失败: {type(exc).__name__}: {exc}")
            field_paths = {}

        # ----- 5) 数据地图 & HTML 总报告 -----
        from reports import REPORT_DIR, DOCS_DIR
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        # 重新读一次 production_usage 列表（避免上面变量未定义时引用）
        production_usage: list[dict[str, Any]] = []
        if production_usage_path is not None and production_usage_path.exists():
            # 简单读回 CSV -> list[dict] 给 render_html 用
            import csv as _csv
            with production_usage_path.open("r", encoding="utf-8-sig", newline="") as fh:
                production_usage = list(_csv.DictReader(fh))

        summary = build_summary(tables, columns, candidates, detailed_issues, production_usage)
        summary["scan_mode"] = result.get("stopped", "complete")
        summary["done_count"] = sum(1 for p in progress.values() if p.status == "done")
        summary["failed_count"] = sum(1 for p in progress.values() if p.status == "failed")
        # 重新落盘 summary_*.json （用最新 detailed_issues + production_usage）
        from reports import json_default
        (SNAPSHOT_DIR / paths["summary_json"].name).write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, default=json_default),
            encoding="utf-8",
        )

        (DOCS_DIR / "data-map.md").write_text(
            render_data_map(summary, candidates, detailed_issues), encoding="utf-8"
        )
        report_path = REPORT_DIR / f"smart-report-demo_{_now()}.html"
        report_path.write_text(
            render_html(summary, candidates, detailed_issues, production_usage),
            encoding="utf-8",
        )
        print(f"[scan] final report: {report_path}", flush=True)
        for name, p in paths.items():
            print(f"[scan] {name}: {p}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
