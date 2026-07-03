from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pymssql


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


ROOT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    timeout: int = 30
    sample_rows: int = 1000


def load_config(env_path: Path | None = None) -> DbConfig:
    load_dotenv(env_path or ROOT_DIR / ".env")
    return DbConfig(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "1433")),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        timeout=int(os.environ.get("DB_QUERY_TIMEOUT", "30")),
        sample_rows=int(os.environ.get("DB_SAMPLE_ROWS", "1000")),
    )


def connect(config: DbConfig | None = None):
    cfg = config or load_config()
    try:
        return pymssql.connect(
            server=cfg.host,
            port=cfg.port,
            user=cfg.user,
            password=cfg.password,
            database=cfg.database,
            login_timeout=cfg.timeout,
            timeout=cfg.timeout,
            charset="UTF-8",
            as_dict=True,
        )
    except Exception as exc:
        # 在子进程/终端中给出更明确的诊断信息，帮助定位网络/账号/白名单问题
        import socket
        import sys

        sys.stderr.write(
            f"[db.connect] 连接失败: host={cfg.host}, port={cfg.port}, database={cfg.database}, user={cfg.user}\n"
        )
        try:
            sock = socket.create_connection((cfg.host, cfg.port), timeout=5)
            sock.close()
            sys.stderr.write(f"[db.connect] TCP {cfg.host}:{cfg.port} 端口可连通，问题可能在认证或 SQL Server 服务。\n")
        except Exception as net_exc:
            sys.stderr.write(f"[db.connect] TCP {cfg.host}:{cfg.port} 端口不通: {net_exc}\n")
        sys.stderr.write(f"[db.connect] 原始异常: {type(exc).__name__}: {exc}\n")
        raise


def fetch_all(sql: str, params: Iterable[Any] | None = None, config: DbConfig | None = None) -> list[dict[str, Any]]:
    with connect(config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(params or ()))
            return list(cursor.fetchall())


def quote_name(name: str) -> str:
    return "[" + name.replace("]", "]] ").replace("]] ", "]]") + "]"


def qualified_name(schema_name: str, table_name: str) -> str:
    return f"{quote_name(schema_name)}.{quote_name(table_name)}"
