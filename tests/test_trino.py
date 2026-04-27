#!/usr/bin/env python3
"""
Integration tests for the ./trino command.

Requirements:
  docker compose up -d   (from ./docker/)
  pip install trino pytest

Run:
  pytest tests/ -v
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

TRINO_BIN = str(Path(__file__).parent.parent / "scripts" / "trino")
TEST_ENV  = str(Path(__file__).parent / "fixtures" / "trino-docker.env")


def run(sql, extra_args=None):
    cmd = [sys.executable, TRINO_BIN, "--env", TEST_ENV] + (extra_args or []) + [sql]
    return subprocess.run(cmd, capture_output=True, text=True)


# ── connection ────────────────────────────────────────────────────────────────

class TestConnection:
    def test_select_1(self):
        r = run("SELECT 1")
        assert r.returncode == 0, r.stderr
        assert "1" in r.stdout

    def test_show_catalogs(self):
        r = run("SHOW CATALOGS")
        assert r.returncode == 0, r.stderr
        assert "tpch"   in r.stdout
        assert "memory" in r.stdout

    def test_show_schemas(self):
        r = run("SHOW SCHEMAS FROM tpch")
        assert r.returncode == 0, r.stderr
        assert "tiny" in r.stdout


# ── queries ───────────────────────────────────────────────────────────────────

class TestQueries:
    def test_count_nation(self):
        r = run("SELECT COUNT(*) FROM tpch.tiny.nation")
        assert r.returncode == 0, r.stderr
        assert "25" in r.stdout

    def test_select_with_limit(self):
        r = run("SELECT nationkey, name FROM tpch.tiny.nation ORDER BY nationkey",
                ["--limit", "5"])
        assert r.returncode == 0, r.stderr
        rows = [l for l in r.stdout.splitlines() if "|" in l and "---" not in l]
        assert len(rows) >= 5  # header + 5 data rows (markdown)

    def test_describe_table(self):
        r = run("DESCRIBE tpch.tiny.nation")
        assert r.returncode == 0, r.stderr
        assert "nationkey" in r.stdout


# ── output formats ────────────────────────────────────────────────────────────

SQL3 = "SELECT nationkey, name FROM tpch.tiny.nation ORDER BY nationkey LIMIT 3"


class TestFormats:
    def test_markdown(self):
        r = run(SQL3, ["--format", "markdown"])
        assert r.returncode == 0, r.stderr
        assert "| nationkey" in r.stdout

    def test_csv(self):
        r = run(SQL3, ["--format", "csv"])
        assert r.returncode == 0, r.stderr
        lines = r.stdout.strip().splitlines()
        assert lines[0] == "nationkey,name"
        assert len(lines) == 4

    def test_tsv(self):
        r = run(SQL3, ["--format", "tsv"])
        assert r.returncode == 0, r.stderr
        lines = r.stdout.strip().splitlines()
        assert "\t" in lines[0]
        assert "nationkey" in lines[0]

    def test_json(self):
        r = run(SQL3, ["--format", "json"])
        assert r.returncode == 0, r.stderr
        data = json.loads(r.stdout)
        assert len(data) == 3
        assert "nationkey" in data[0]

    def test_aligned(self):
        r = run(SQL3, ["--format", "aligned"])
        assert r.returncode == 0, r.stderr
        assert "+-" in r.stdout
        assert "(3 rows)" in r.stdout

    def test_output_file(self, tmp_path):
        out = str(tmp_path / "out.csv")
        r = run(SQL3, ["--format", "csv", "--output", out])
        assert r.returncode == 0, r.stderr
        assert "nationkey,name" in Path(out).read_text()


# ── dry-run ───────────────────────────────────────────────────────────────────

class TestDryRun:
    def test_prints_sql_no_execution(self):
        r = run("DROP TABLE tpch.tiny.nation", ["--dry-run"])
        assert r.returncode == 0
        assert "DRY RUN"    in r.stdout
        assert "DROP TABLE" in r.stdout

    def test_adds_limit(self):
        r = run("SELECT * FROM tpch.tiny.nation", ["--dry-run", "--limit", "10"])
        assert "LIMIT 10" in r.stdout


# ── DDL / DML on memory catalog ───────────────────────────────────────────────

class TestDDL:
    TABLE = "memory.default.test_trino_client"

    def test_create_insert_select_drop(self):
        run(f"DROP TABLE IF EXISTS {self.TABLE}")

        r = run(f"CREATE TABLE {self.TABLE} (id INTEGER, val VARCHAR)")
        assert r.returncode == 0, r.stderr

        r = run(f"INSERT INTO {self.TABLE} VALUES (1, 'hello'), (2, 'world')")
        assert r.returncode == 0, r.stderr

        r = run(f"SELECT * FROM {self.TABLE} ORDER BY id")
        assert r.returncode == 0, r.stderr
        assert "hello" in r.stdout
        assert "world" in r.stdout

        r = run(f"DROP TABLE {self.TABLE}")
        assert r.returncode == 0, r.stderr


# ── error handling ────────────────────────────────────────────────────────────

class TestErrors:
    def test_nonexistent_table(self):
        r = run("SELECT * FROM tpch.tiny.does_not_exist_xyz")
        assert r.returncode != 0

    def test_syntax_error(self):
        r = run("SELEKT * FORM nation")
        assert r.returncode != 0

    def test_missing_host(self):
        env = {k: v for k, v in os.environ.items() if k != "TRINO_HOST"}
        r = subprocess.run(
            [sys.executable, TRINO_BIN, "SELECT 1"],
            capture_output=True, text=True, env=env,
        )
        assert r.returncode != 0
        assert "TRINO_HOST" in r.stderr + r.stdout
