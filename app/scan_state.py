from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from db import ROOT_DIR


STATE_PATH = ROOT_DIR / "outputs" / "scan_state.json"
CONTROL_PATH = ROOT_DIR / "outputs" / "scan_control.json"  # 暂停/继续控制信号
# 每个表的扫描明细落盘
PROGRESS_PATH = ROOT_DIR / "outputs" / "scan_progress.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class TableProgress:
    table: str
    status: str = "pending"  # pending / scanning / done / failed / skipped
    started_at: str = ""
    finished_at: str = ""
    issue_count: int = 0
    column_count: int = 0
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "table": self.table,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "issue_count": self.issue_count,
            "column_count": self.column_count,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TableProgress":
        return cls(
            table=str(data.get("table", "")),
            status=str(data.get("status", "pending")),
            started_at=str(data.get("started_at", "")),
            finished_at=str(data.get("finished_at", "")),
            issue_count=int(data.get("issue_count", 0) or 0),
            column_count=int(data.get("column_count", 0) or 0),
            error=str(data.get("error", "")),
        )


@dataclass
class ScanState:
    database_name: str = ""
    database_host: str = ""
    database_port: int = 1433
    total_tables: int = 0
    candidate_tables: int = 0          # 非噪声业务候选表总数
    done_count: int = 0                # 已完成（含历史 done）
    failed_count: int = 0              # 失败数量
    pending_count: int = 0             # 待扫描数量
    current_table: str = ""            # 正在扫描的表
    is_complete: bool = False
    is_paused: bool = False            # 用户触发的暂停
    analyzed_at: str = ""              # 最近一次状态变更时间
    started_at: str = ""               # 最近一轮扫描开始时间
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "database_name": self.database_name,
            "database_host": self.database_host,
            "database_port": self.database_port,
            "total_tables": self.total_tables,
            "candidate_tables": self.candidate_tables,
            "done_count": self.done_count,
            "failed_count": self.failed_count,
            "pending_count": self.pending_count,
            "current_table": self.current_table,
            "is_complete": self.is_complete,
            "is_paused": self.is_paused,
            "analyzed_at": self.analyzed_at,
            "started_at": self.started_at,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScanState":
        return cls(
            database_name=data.get("database_name", ""),
            database_host=data.get("database_host", ""),
            database_port=int(data.get("database_port", 1433)),
            total_tables=int(data.get("total_tables", 0)),
            candidate_tables=int(data.get("candidate_tables", 0)),
            done_count=int(data.get("done_count", 0)),
            failed_count=int(data.get("failed_count", 0)),
            pending_count=int(data.get("pending_count", 0)),
            current_table=str(data.get("current_table", "")),
            is_complete=bool(data.get("is_complete", False)),
            is_paused=bool(data.get("is_paused", False)),
            analyzed_at=str(data.get("analyzed_at", "")),
            started_at=str(data.get("started_at", "")),
            note=str(data.get("note", "")),
        )


@dataclass
class ScanControl:
    action: str = "idle"  # idle / pause / resume / reset
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"action": self.action, "updated_at": self.updated_at}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScanControl":
        return cls(
            action=str(data.get("action", "idle")),
            updated_at=str(data.get("updated_at", "")),
        )


# ---------- 顶层状态读写 ----------

def load_state() -> ScanState:
    if not STATE_PATH.exists():
        return ScanState()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return ScanState.from_dict(data)
    except Exception:
        return ScanState()


def _safe_write_json(path: Path, payload: str) -> None:
    """直接写目标文件：先尝试 os.replace（保留原子性），WinError 5 / PermissionError 时回退为直接覆盖。

    之所以放弃 .tmp 中转：Streamlit 主进程每 3 秒 st.rerun() 时会短暂持有 scan_state.json
    句柄，子进程的 .tmp.replace() 会撞上 WinError 5 拒绝访问；直接覆盖即使丢 1 个状态点，
    也比子进程 PermissionError 整个崩掉要好。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    # 1) 优先尝试写到 .tmp 再原子替换
    for attempt in range(3):
        try:
            tmp.write_text(payload, encoding="utf-8")
            os.replace(tmp, path)
            return
        except (PermissionError, OSError) as exc:
            if attempt < 2:
                time.sleep(0.2 * (attempt + 1))
                continue
            # 2) .tmp 被占 → 回退为直接写目标文件（容忍短时不一致）
            try:
                if tmp.exists():
                    try:
                        tmp.unlink()
                    except Exception:
                        pass
                path.write_text(payload, encoding="utf-8")
                return
            except Exception:
                # 3) 仍失败 → 最后尝试一次删除后重建
                try:
                    if path.exists():
                        path.unlink()
                except Exception:
                    pass
                path.write_text(payload, encoding="utf-8")
                return


def save_state(state: ScanState) -> None:
    _safe_write_json(STATE_PATH, json.dumps(state.to_dict(), ensure_ascii=False, indent=2))


# ---------- 逐表进度读写 ----------

def load_progress() -> dict[str, TableProgress]:
    if not PROGRESS_PATH.exists():
        return {}
    try:
        data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {name: TableProgress.from_dict(item) for name, item in data.items()}


def save_progress(progress: dict[str, TableProgress]) -> None:
    payload = {name: item.to_dict() for name, item in progress.items()}
    _safe_write_json(PROGRESS_PATH, json.dumps(payload, ensure_ascii=False, indent=2))


# ---------- 控制信号（暂停/继续/重置） ----------

def load_control() -> ScanControl:
    if not CONTROL_PATH.exists():
        return ScanControl()
    try:
        return ScanControl.from_dict(json.loads(CONTROL_PATH.read_text(encoding="utf-8")))
    except Exception:
        return ScanControl()


def write_control(action: str) -> None:
    CONTROL_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = ScanControl(action=action, updated_at=_now()).to_dict()
    tmp = CONTROL_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CONTROL_PATH)


def clear_control() -> None:
    if CONTROL_PATH.exists():
        try:
            CONTROL_PATH.unlink()
        except Exception:
            pass


# ---------- 状态汇总（给页面用） ----------

def _recalc_counts(state: ScanState, progress: dict[str, TableProgress]) -> None:
    done = sum(1 for p in progress.values() if p.status == "done")
    failed = sum(1 for p in progress.values() if p.status == "failed")
    pending = max(state.candidate_tables - done - failed, 0)
    state.done_count = done
    state.failed_count = failed
    state.pending_count = pending
    state.candidate_tables = max(state.candidate_tables, done + failed + pending)
    if state.candidate_tables > 0 and done + failed >= state.candidate_tables:
        state.is_complete = True
    else:
        state.is_complete = False


def refresh_state_from_progress() -> ScanState:
    state = load_state()
    progress = load_progress()
    _recalc_counts(state, progress)
    state.analyzed_at = _now()
    save_state(state)
    return state


def update_state(**kwargs: Any) -> ScanState:
    state = load_state()
    for k, v in kwargs.items():
        if hasattr(state, k):
            setattr(state, k, v)
    state.analyzed_at = _now()
    save_state(state)
    return state


def init_run(database_name: str, database_host: str, database_port: int, total_tables: int, candidate_tables: int) -> ScanState:
    """开始新一轮扫描前调用（断点续扫或全量重扫）。"""
    state = ScanState(
        database_name=database_name,
        database_host=database_host,
        database_port=database_port,
        total_tables=total_tables,
        candidate_tables=candidate_tables,
        done_count=0,
        failed_count=0,
        pending_count=candidate_tables,
        current_table="",
        is_complete=False,
        is_paused=False,
        analyzed_at=_now(),
        started_at=_now(),
        note="扫描启动中",
    )
    progress = load_progress()
    _recalc_counts(state, progress)
    state.analyzed_at = _now()
    save_state(state)
    return state


def reset_progress() -> None:
    """全部重新扫描：清空逐表进度和状态。"""
    for path in (PROGRESS_PATH, STATE_PATH, CONTROL_PATH):
        if path.exists():
            try:
                path.unlink()
            except Exception:
                pass


def is_fully_analyzed() -> bool:
    state = load_state()
    return state.is_complete and state.candidate_tables > 0 and state.pending_count == 0


def state_summary() -> dict[str, Any]:
    state = load_state()
    pct = round(state.done_count / max(state.candidate_tables, 1) * 100, 1)
    return {
        "has_state": STATE_PATH.exists(),
        "database_name": state.database_name,
        "analyzed_at": state.analyzed_at,
        "started_at": state.started_at,
        "is_complete": state.is_complete,
        "is_paused": state.is_paused,
        "total_tables": state.total_tables,
        "candidate_tables": state.candidate_tables,
        "done_count": state.done_count,
        "failed_count": state.failed_count,
        "pending_count": state.pending_count,
        "current_table": state.current_table,
        "progress_pct": pct,
        "note": state.note,
    }


def progress_rows() -> list[dict[str, Any]]:
    """返回逐表进度列表（按状态、开始时间排序）。"""
    progress = load_progress()
    rows = [p.to_dict() for p in progress.values()]
    order = {"scanning": 0, "pending": 1, "failed": 2, "skipped": 3, "done": 4}
    rows.sort(key=lambda r: (order.get(r["status"], 9), r["table"]))
    return rows
