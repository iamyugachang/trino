---
name: trino
description: >
  Natural language interface to Trino — query catalogs/schemas/tables with SQL
  or English/Chinese. Works in Claude Code (as the /trino slash command) and
  in Hermes (as a skill). Bundled standalone Python client; no MCP required.
triggers:
  - "trino"
  - "query trino"
  - "show catalogs"
  - "show schemas"
  - "show tables"
  - "describe table"
  - "trino DDL"
required_environment_variables:
  - TRINO_HOST
---

# Trino Skill

Run SQL against Trino with a single CLI. The client reads connection info from
`~/.trino.env`, executes the query, prints an aligned table to the terminal,
and **auto-saves a markdown copy** to `./trino-output/<timestamp>.md`.

Source repo: https://github.com/iamyugachang/trino

---

## Installation

```bash
git clone https://github.com/iamyugachang/trino.git
cd trino

./install.sh                    # install both Claude Code and Hermes
./install.sh --target claude-code
./install.sh --target hermes
```

`uv` is preferred for installing the Python `trino` package; otherwise falls
back to `python3 -m pip install trino`.

---

## Connection setup

```bash
cp templates/trino.env ~/.trino.env   # if not auto-created by install.sh
$EDITOR ~/.trino.env
```

```bash
TRINO_HOST=trino.your-company.com
TRINO_PORT=8080
TRINO_USER=your_username
TRINO_PASSWORD=
TRINO_HTTPS=false
TRINO_VERIFY_SSL=false        # false for self-signed certs
TRINO_CATALOG=hive
TRINO_SCHEMA=default
```

For local Docker testing use `templates/trino.env.docker` instead
(host=localhost:8080, no auth, catalog=tpch).

Lookup order: `--env FILE` > `./.trino.env` > `~/.trino.env`.

---

## Usage

### Claude Code

```
/trino SHOW CATALOGS
/trino hive 有幾個 schema
/trino list tables in hive.analytics
/trino describe table hive.analytics.events
/trino SELECT * FROM tpch.tiny.nation LIMIT 5
/trino --dry-run DROP TABLE hive.myschema.old_data
```

### Hermes (or any shell)

```bash
TRINO=~/.hermes/skills/data-science/trino/scripts/trino_client.py
# or, after install.sh --target claude-code:
TRINO=~/.local/share/trino/scripts/trino_client.py

python3 $TRINO "SHOW CATALOGS"
python3 $TRINO "SELECT * FROM tpch.tiny.nation LIMIT 5"
python3 $TRINO --no-save "SELECT 1"
python3 $TRINO --save report.md "SHOW SCHEMAS FROM hive"
```

### Flags

| Flag | Description |
|---|---|
| `--format` | `aligned` *(default)*, `markdown`, `csv`, `tsv`, `json` |
| `--save FILE` | Override auto-save path |
| `--no-save` | Disable the auto markdown copy |
| `--output FILE` | Write `--format` output to FILE (skips auto-save) |
| `--limit N` | Append `LIMIT N` |
| `--dry-run` | Print SQL, don't execute |
| `--env FILE` | Custom `.env` file |
| `--catalog` / `--schema` | Override catalog / schema |
| `--file FILE` | Read SQL from file |

Env vars: `TRINO_AUTO_SAVE=0` disables auto-save globally; `TRINO_OUTPUT_DIR`
overrides the default `./trino-output`.

---

## Natural language → SQL reference

| User says | SQL |
|---|---|
| "show all catalogs" | `SHOW CATALOGS` |
| "list schemas in X" | `SHOW SCHEMAS FROM X` |
| "list tables in X.Y" | `SHOW TABLES FROM X.Y` |
| "X catalog 有幾個 schema" | `SELECT COUNT(*) FROM X.information_schema.schemata` |
| "X.Y schema 有幾張表" | `SELECT COUNT(*) FROM X.information_schema.tables WHERE table_schema='Y'` |
| "describe table X.Y.Z" | `DESCRIBE X.Y.Z` |
| "sample table X" | `SELECT * FROM X LIMIT 20` |
| "count rows in X" | `SELECT COUNT(*) FROM X` |
| "find tables with column X" | `SELECT table_schema, table_name FROM information_schema.columns WHERE column_name = 'X'` |
| "table stats / size" | `SHOW STATS FOR X` |
| "show partitions of X" | `SHOW PARTITIONS FROM X` |
| "query plan for ..." | `EXPLAIN (TYPE DISTRIBUTED) <sql>` |

---

## Workflow rules (for the agent)

1. **Always print the SQL** before executing.
2. For write ops (`INSERT`/`UPDATE`/`DELETE`/`DROP`/`CREATE`/`ALTER`), run
   `--dry-run` first and ask the user to confirm.
3. Use `--limit N` proactively for `SELECT *` on unfamiliar tables.
4. Mention the auto-saved markdown path so the user knows where the result lives.

---

## Common patterns

```sql
-- Query plan
EXPLAIN (TYPE DISTRIBUTED) SELECT ...;
EXPLAIN ANALYZE SELECT ...;

-- Metadata
SHOW CREATE TABLE catalog.schema.table;
SHOW SESSION;

-- Iceberg time travel
SELECT * FROM hive.myschema."mytable$snapshots" ORDER BY committed_at DESC;
SELECT * FROM hive.myschema."mytable$history";
```

---

## Error reference

| Error | Cause | Fix |
|---|---|---|
| `TRINO_HOST not set` | Missing `.trino.env` | `cp templates/trino.env ~/.trino.env` |
| `Authentication failed` | Wrong credentials | Check `TRINO_USER` / `TRINO_PASSWORD` |
| `SSL handshake failed` | Cert issue | Set `TRINO_VERIFY_SSL=false` |
| `Catalog does not exist` | Wrong catalog | Run `/trino SHOW CATALOGS` first |
| `Query exceeded memory limit` | Large scan | Add `--limit` or push down filters |
| `SYNTAX_ERROR` | Non-ANSI SQL | Trino uses ANSI SQL — avoid MySQL/Hive-specific syntax |
| `No module named trino` | Package missing | `uv pip install trino` or `python3 -m pip install trino` |

---

## Verification (Docker)

```bash
cd docker && docker compose up -d && cd ..
python3 -m pip install pytest
pytest tests/ -v   # ~20 tests, ~10s
```

See `TESTING.md` for the full three-environment checklist
(Hermes + Docker / Claude Code + Docker / Claude Code + company Trino).
