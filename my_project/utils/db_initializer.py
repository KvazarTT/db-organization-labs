from pathlib import Path
from typing import List
import pymysql


def parse_sql_script(sql_text: str) -> List[str]:
    """Splits a MySQL script supporting DELIMITER directives, comments, and quoted strings."""
    statements: List[str] = []
    delimiter = ';'
    buffer: List[str] = []
    in_single_quote = False
    in_double_quote = False
    i = 0
    n = len(sql_text)

    while i < n:
        ch = sql_text[i]

        # Handle DELIMITER directive at line start when not inside quotes
        if not in_single_quote and not in_double_quote and (i == 0 or sql_text[i - 1] == '\n'):
            line_end = sql_text.find('\n', i)
            if line_end == -1:
                line_end = n
            line = sql_text[i:line_end].strip()

            if line.upper().startswith('DELIMITER '):
                new_delim = line.split(None, 1)[1].strip()
                leftover = ''.join(buffer).strip()
                if leftover:
                    statements.append(leftover)
                    buffer.clear()
                delimiter = new_delim
                i = line_end + 1
                continue

            if line.startswith('--') or not line:
                i = line_end + 1
                continue

        # Track string literals
        if ch == "'" and not in_double_quote:
            # Handle escaped quote '' or \'
            if in_single_quote and i + 1 < n and sql_text[i + 1] == "'":
                buffer.append("''")
                i += 2
                continue
            if i > 0 and sql_text[i - 1] != '\\':
                in_single_quote = not in_single_quote
            buffer.append(ch)
            i += 1
            continue

        if ch == '"' and not in_single_quote:
            if i > 0 and sql_text[i - 1] != '\\':
                in_double_quote = not in_double_quote
            buffer.append(ch)
            i += 1
            continue

        # Check for current delimiter outside quotes
        if not in_single_quote and not in_double_quote:
            if sql_text.startswith(delimiter, i):
                stmt = ''.join(buffer).strip()
                if stmt:
                    statements.append(stmt)
                buffer.clear()
                i += len(delimiter)
                continue

        buffer.append(ch)
        i += 1

    trailing = ''.join(buffer).strip()
    if trailing:
        statements.append(trailing)

    return statements


def execute_sql_file(cfg: dict, sql_path: Path = None) -> None:
    """Executes data.sql against MySQL to ensure tables, triggers, functions, and procedures exist."""
    if sql_path is None:
        sql_path = Path(__file__).resolve().parent.parent.parent / 'data.sql'

    sql_text = sql_path.read_text(encoding='utf-8')
    statements = parse_sql_script(sql_text)

    conn = pymysql.connect(
        host=cfg['DB_HOST'],
        port=cfg['DB_PORT'],
        user=cfg['DB_USER'],
        password=cfg['DB_PASSWORD'],
        charset='utf8mb4',
        autocommit=True
    )
    try:
        with conn.cursor() as cur:
            # Drop any leftover cursor-generated dynamic tables from previous runs
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = %s AND table_name LIKE 'clients_copy_%%'",
                (cfg['DB_NAME'],)
            )
            for (tbl_name,) in cur.fetchall():
                cur.execute(f"DROP TABLE IF EXISTS `{cfg['DB_NAME']}`.`{tbl_name}`")

            for stmt in statements:
                cur.execute(stmt)
    finally:
        conn.close()
