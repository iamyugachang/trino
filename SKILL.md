---
name: trino
description: >
  Natural language interface to Trino — query, explore schemas, and manage
  data using the bundled Python client. No MCP required.
triggers:
  - "trino"
  - "query trino"
  - "show tables / schemas / catalogs"
  - "describe table"
  - "trino DDL"
---

# Trino Skill

## Overview

Execute SQL against Trino using the bundled `scripts/trino` client.
Translate natural language → SQL → run → return results.

The skill directory is the repo itself:
```
~/.hermes/skills/data-science/trino/
├── SKILL.md             ← this file
├── scripts/
│   ├── trino            ← executable entry point
│   └── trino_client.py  ← core client logic
├── templates/
│   └── trino.env        ← connection config template
├── docker/              ← local Trino test environment
└── tests/               ← integration test suite
```

---

## 1. Install

```bash
git clone https://github.com/iamyugachang/trino.git \
    ~/.hermes/skills/data-science/trino

pip install trino
```

---

## 2. Connection Setup (first time)

```bash
# Copy the template
cp ~/.hermes/skills/data-science/trino/templates/trino.env ~/.trino.env

# Fill in your settings
nano ~/.trino.env
```

**Fields:**
```bash
TRINO_HOST=trino.your-company.com   # coordinator hostname
TRINO_PORT=8080                      # 443=HTTPS, 8080=HTTP
TRINO_USER=your_username             # LDAP / SSO account
TRINO_PASSWORD=                      # leave blank if no auth
TRINO_HTTPS=false                    # true | false
TRINO_VERIFY_SSL=false               # false for self-signed certs
TRINO_CATALOG=hive                   # default catalog
TRINO_SCHEMA=default                 # default schema
```

Lookup order: `--env FILE` > `./.trino.env` > `~/.trino.env`

---

## 3. Running Queries

The client to call is: `~/.hermes/skills/data-science/trino/scripts/trino`

```bash
TRINO=~/.hermes/skills/data-science/trino/scripts/trino

# Basic
python3 $TRINO "SHOW CATALOGS"
python3 $TRINO "SHOW SCHEMAS FROM hive"
python3 $TRINO "SHOW TABLES FROM hive.analytics"
python3 $TRINO "DESCRIBE hive.analytics.events"

# Query
python3 $TRINO "SELECT * FROM hive.analytics.events" --limit 100
python3 $TRINO --format csv --output out.csv "SELECT * FROM hive.analytics.events"
python3 $TRINO --format json "SELECT user_id, COUNT(*) FROM t GROUP BY 1"
python3 $TRINO --file my_query.sql

# Safety — always dry-run before destructive operations
python3 $TRINO --dry-run "DROP TABLE hive.myschema.old_data"

# Override catalog/schema inline
python3 $TRINO --catalog iceberg --schema analytics "SHOW TABLES"

# Use a custom env (e.g. staging)
python3 $TRINO --env ~/.trino-staging.env "SELECT 1"
```

**Output formats:**
| `--format` | Description |
|---|---|
| `markdown` | Markdown table *(default)* |
| `aligned` | Aligned ASCII table (like psql) |
| `csv` | CSV with header |
| `tsv` | TSV with header |
| `json` | JSON array of objects |

---

## 4. Natural Language → SQL Reference

| User says | SQL |
|---|---|
| "show all catalogs" | `SHOW CATALOGS` |
| "list schemas in X" | `SHOW SCHEMAS FROM X` |
| "list tables in X.Y" | `SHOW TABLES FROM X.Y` |
| "describe table X.Y.Z" | `DESCRIBE X.Y.Z` |
| "sample table X" | `SELECT * FROM X LIMIT 20` |
| "count rows in X" | `SELECT COUNT(*) FROM X` |
| "find tables with column X" | `SELECT table_schema, table_name FROM information_schema.columns WHERE column_name = 'X'` |
| "table stats / size" | `SHOW STATS FOR X` |
| "show partitions of X" | `SHOW PARTITIONS FROM X` |

---

## 5. Workflow

1. **Check connection** — load `~/.trino.env`, verify `TRINO_HOST` is set
2. **Show SQL** — always display the SQL before executing
3. **Confirm write ops** — require user confirmation for INSERT / CREATE / DROP / ALTER
4. **Execute** — call `scripts/trino`
5. **Return result** — format as markdown table or summarize

---

## 6. Common Patterns

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

## 7. Error Reference

| Error | Cause | Fix |
|---|---|---|
| `TRINO_HOST not set` | Missing `.trino.env` | Copy template → fill in |
| `Authentication failed` | Wrong credentials | Check `TRINO_USER` / `TRINO_PASSWORD` |
| `SSL handshake failed` | Cert issue | Set `TRINO_VERIFY_SSL=false` |
| `Catalog does not exist` | Wrong catalog | Run `SHOW CATALOGS` first |
| `Query exceeded memory limit` | Large scan | Add `--limit` or push down filters |
| `SYNTAX_ERROR` | Non-ANSI SQL | Trino uses ANSI SQL — avoid MySQL/Hive-specific syntax |

---

## 8. Verify with Docker (optional)

Test the client against a local Trino before using in production:

```bash
cd ~/.hermes/skills/data-science/trino/docker
docker compose up -d
cd ..
pytest tests/ -v   # 18 tests, ~10s
```
