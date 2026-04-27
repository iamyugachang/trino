#!/usr/bin/env python3
"""Trino client — .env loading, connection, execution, formatting."""

import argparse
import os
import sys
import json
from pathlib import Path


# ── .env loader ───────────────────────────────────────────────────────────────

def load_env(custom_path=None):
    candidates = []
    if custom_path:
        candidates.append(Path(custom_path))
    candidates += [Path(".trino.env"), Path.home() / ".trino.env"]

    for path in candidates:
        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, val = line.partition("=")
                        os.environ.setdefault(key.strip(), val.strip())
            print(f"[trino] config: {path}", file=sys.stderr)
            return str(path)

    print("[trino] warning: no .trino.env found — using environment variables", file=sys.stderr)
    return None


# ── connection ────────────────────────────────────────────────────────────────

def get_connection():
    try:
        import trino as _trino
    except ImportError:
        sys.exit("[trino] error: run  pip install trino")

    host = os.environ.get("TRINO_HOST")
    if not host:
        sys.exit("[trino] error: TRINO_HOST not set — check your .trino.env")

    port       = int(os.environ.get("TRINO_PORT", 8080))
    user       = os.environ.get("TRINO_USER", os.environ.get("USER", "trino"))
    password   = os.environ.get("TRINO_PASSWORD", "")
    catalog    = os.environ.get("TRINO_CATALOG", "tpch")
    schema     = os.environ.get("TRINO_SCHEMA", "tiny")
    use_https  = os.environ.get("TRINO_HTTPS", "false").lower() == "true"
    verify_ssl = os.environ.get("TRINO_VERIFY_SSL", "true").lower() == "true"

    auth = _trino.auth.BasicAuthentication(user, password) if password else None

    return _trino.dbapi.connect(
        host=host,
        port=port,
        user=user,
        auth=auth,
        catalog=catalog,
        schema=schema,
        http_scheme="https" if use_https else "http",
        verify=verify_ssl,
    )


# ── formatters ────────────────────────────────────────────────────────────────

def fmt_aligned(rows, cols):
    if not rows:
        return "(no rows)"
    widths = [max(len(str(c)), max((len(str(r[i])) for r in rows), default=0))
              for i, c in enumerate(cols)]
    sep    = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header = "| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cols)) + " |"
    lines  = [sep, header, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)) + " |")
    lines.append(sep)
    lines.append(f"({len(rows)} row{'s' if len(rows) != 1 else ''})")
    return "\n".join(lines)


def fmt_markdown(rows, cols):
    if not rows:
        return "*(no rows)*"
    widths = [max(len(str(c)), max((len(str(r[i])) for r in rows), default=0))
              for i, c in enumerate(cols)]
    header = "| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cols)) + " |"
    sep    = "| " + " | ".join("-" * widths[i] for i in range(len(cols))) + " |"
    lines  = [header, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)) + " |")
    lines.append(f"\n*{len(rows)} row{'s' if len(rows) != 1 else ''}*")
    return "\n".join(lines)


def fmt_csv(rows, cols):
    import csv, io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    w.writerows(rows)
    return buf.getvalue()


def fmt_tsv(rows, cols):
    lines = ["\t".join(str(c) for c in cols)]
    lines += ["\t".join(str(v) for v in row) for row in rows]
    return "\n".join(lines)


def fmt_json(rows, cols):
    return json.dumps([dict(zip(cols, row)) for row in rows],
                      default=str, ensure_ascii=False, indent=2)


FORMATTERS = {
    "markdown": fmt_markdown,
    "aligned":  fmt_aligned,
    "csv":      fmt_csv,
    "tsv":      fmt_tsv,
    "json":     fmt_json,
}


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="trino",
        description="SQL client for Trino",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  ./trino "SHOW CATALOGS"
  ./trino "SELECT * FROM tpch.tiny.nation LIMIT 5"
  ./trino --format csv "SELECT * FROM tpch.tiny.orders" --output orders.csv
  ./trino --format json "SELECT nationkey, name FROM tpch.tiny.nation LIMIT 3"
  ./trino --dry-run "DROP TABLE hive.myschema.old_data"
  ./trino --env ~/.trino-staging.env "SHOW SCHEMAS FROM hive"
        """,
    )
    parser.add_argument("sql",       nargs="?", help="SQL statement to execute")
    parser.add_argument("--file",    help="Execute SQL from a .sql file")
    parser.add_argument("--format",  choices=list(FORMATTERS), default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--output",  help="Write results to file instead of stdout")
    parser.add_argument("--env",     help="Path to custom .env file")
    parser.add_argument("--catalog", help="Override TRINO_CATALOG")
    parser.add_argument("--schema",  help="Override TRINO_SCHEMA")
    parser.add_argument("--limit",   type=int, help="Append LIMIT N to query")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print SQL without executing")
    args = parser.parse_args()

    load_env(args.env)

    if args.catalog:
        os.environ["TRINO_CATALOG"] = args.catalog
    if args.schema:
        os.environ["TRINO_SCHEMA"] = args.schema

    if args.file:
        sql = Path(args.file).read_text().strip()
    elif args.sql:
        sql = args.sql.strip()
    else:
        parser.print_help()
        sys.exit(0)

    if args.limit and "LIMIT" not in sql.upper():
        sql = f"{sql}\nLIMIT {args.limit}"

    if args.dry_run:
        print("-- DRY RUN --")
        print(sql)
        return

    conn = get_connection()
    cur  = conn.cursor()

    try:
        cur.execute(sql)
    except Exception as e:
        sys.exit(f"[trino] error: {e}")

    if cur.description is None:
        print("[trino] ok: statement executed (no result set)")
        return

    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    result = FORMATTERS[args.format](rows, cols)

    if args.output:
        Path(args.output).write_text(result)
        print(f"[trino] ok: {len(rows)} rows written to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
