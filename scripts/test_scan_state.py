"""端到端模拟：测试断点续扫 + 暂停信号 + 全量重置。"""
from scan_state import (
    TableProgress,
    init_run,
    load_state,
    save_state,
    load_progress,
    save_progress,
    refresh_state_from_progress,
    write_control,
    clear_control,
    load_control,
    reset_progress,
    state_summary,
    STATE_PATH,
    PROGRESS_PATH,
    CONTROL_PATH,
)

# 1) 清空
for p in (STATE_PATH, PROGRESS_PATH, CONTROL_PATH):
    if p.exists():
        p.unlink()
print("[1] cleared state files")

# 2) 模拟 1308 张候选表
state = init_run(
    database_name="UFTData662308_000088",
    database_host="113.45.41.170",
    database_port=1433,
    total_tables=13751,
    candidate_tables=1308,
)
print(f"[2] init_run: candidate_tables={state.candidate_tables}, pending={state.pending_count}")

# 3) 模拟完成前 50 张
progress = load_progress()
for i in range(50):
    name = f"dbo.Table_{i:04d}"
    progress[name] = TableProgress(
        table=name,
        status="done",
        started_at="2026-07-03 10:00:00",
        finished_at="2026-07-03 10:00:01",
        issue_count=2,
        column_count=12,
    )
save_progress(progress)
state = refresh_state_from_progress()
print(f"[3] after 50 done: done={state.done_count}, pending={state.pending_count}, is_complete={state.is_complete}")

# 4) 写暂停信号
write_control("pause")
control = load_control()
print(f"[4] pause signal: action={control.action}, updated_at={control.updated_at}")

# 5) 模拟扫描线程检测到暂停
ctrl = load_control()
if ctrl.action == "pause":
    state.is_paused = True
    state.note = f"已暂停: 完成 {state.done_count}/1308"
    save_state(state)
    clear_control()
    state = load_state()
    print(f"[5] pause applied: is_paused={state.is_paused}, done={state.done_count}/{state.candidate_tables}")

# 6) 模拟部分失败
progress = load_progress()
progress["dbo.Table_Bad"] = TableProgress(
    table="dbo.Table_Bad", status="failed", error="timeout", finished_at="2026-07-03 10:00:02"
)
save_progress(progress)
state = refresh_state_from_progress()
print(f"[6] after 1 failed: done={state.done_count}, failed={state.failed_count}, pending={state.pending_count}")

# 7) 全部重置
reset_progress()
print(f"[7] reset: STATE exists={STATE_PATH.exists()}, PROGRESS exists={PROGRESS_PATH.exists()}")
print(f"    summary after reset: {state_summary()}")
print("ALL OK")
