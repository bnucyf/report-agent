"""一次性裸跑探针：复现 scan.py 卡在 Step 2 的真实堆栈。"""
from __future__ import annotations

import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

# 全局未捕获异常写日志
def _excepthook(exc_type, exc_value, exc_tb):
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    sys.stderr.write(f"[FATAL] {msg}\n")
    sys.stderr.flush()
    try:
        (ROOT / "outputs" / "scan_diag.log").write_text(msg, encoding="utf-8")
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _excepthook

DIAG = ROOT / "outputs" / "scan_diag.log"
DIAG.parent.mkdir(parents=True, exist_ok=True)
DIAG.write_text("", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{time.time():.1f}] {msg}\n"
    sys.stderr.write(line)
    sys.stderr.flush()
    try:
        with DIAG.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        pass


log(f"diag start, python={sys.version.split()[0]} cwd={os.getcwd()}")
log(f"DB_HOST={os.environ.get('DB_HOST')} DB_NAME={os.environ.get('DB_NAME')}")

# Step 1: scan_tables
t0 = time.time()
try:
    from metadata import scan_tables
    tables = scan_tables()
    log(f"OK scan_tables: {len(tables)} rows in {time.time()-t0:.2f}s")
except Exception:
    log(f"FAIL scan_tables after {time.time()-t0:.2f}s:\n{traceback.format_exc()}")

# Step 2: scan_columns (None) —— 这就是子进程卡死的位置
t0 = time.time()
try:
    from metadata import scan_columns
    cols = scan_columns(None)
    log(f"OK scan_columns(None): {len(cols)} rows in {time.time()-t0:.2f}s")
except Exception:
    log(f"FAIL scan_columns(None) after {time.time()-t0:.2f}s:\n{traceback.format_exc()}")

# Step 3: scan_indexes
t0 = time.time()
try:
    from metadata import scan_indexes
    idx = scan_indexes(None)
    log(f"OK scan_indexes(None): {len(idx)} rows in {time.time()-t0:.2f}s")
except Exception:
    log(f"FAIL scan_indexes(None) after {time.time()-t0:.2f}s:\n{traceback.format_exc()}")

# Step 4: classify_tables
t0 = time.time()
try:
    from table_classifier import classify_tables
    from metadata import build_column_map
    columns = scan_columns(None) if "cols" in dir() else []
    cmap = build_column_map(columns)
    cands = classify_tables(tables, cmap)
    log(f"OK classify_tables: {len(cands)} candidates in {time.time()-t0:.2f}s")
except Exception:
    log(f"FAIL classify_tables after {time.time()-t0:.2f}s:\n{traceback.format_exc()}")

# Step 5: profile_one_table（最关键的一步）
t0 = time.time()
try:
    from profiling import profile_table
    active = [r for r in tables if int(r.get("row_count") or 0) > 0]
    # 取行数最多的一张
    active.sort(key=lambda r: -int(r.get("row_count") or 0))
    target = active[0]
    log(f"profile target: {target['schema_name']}.{target['table_name']} rows={target['row_count']}")
    cols = cmap.get(f"{target['schema_name']}.{target['table_name']}", [])[:80]
    log(f"  cols: {len(cols)}")
    issues = profile_table(target["schema_name"], target["table_name"], cols, 200)
    log(f"OK profile_table: {len(issues)} issues in {time.time()-t0:.2f}s")
except Exception:
    log(f"FAIL profile_table after {time.time()-t0:.2f}s:\n{traceback.format_exc()}")

log("diag end")
