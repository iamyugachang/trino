Execute a SQL query or natural language request against Trino.

The user's input is: $ARGUMENTS

Follow these steps:

1. **Resolve the query**
   - If the input looks like SQL (starts with SELECT/SHOW/DESCRIBE/EXPLAIN/CREATE/INSERT/DROP/ALTER etc.), use it directly.
   - If it's natural language, translate to SQL first and show it to the user before executing.

2. **Execute** by running:
   ```bash
   python3 ~/.local/share/trino/scripts/trino "$ARGUMENTS"
   ```
   If the input was translated from natural language, run the SQL instead:
   ```bash
   python3 ~/.local/share/trino/scripts/trino "TRANSLATED SQL HERE"
   ```

3. **Output options** — append flags as needed:
   - `--format csv --output FILE`  →  export to CSV
   - `--format json`               →  JSON output
   - `--format aligned`            →  psql-style table
   - `--limit N`                   →  cap results
   - `--dry-run`                   →  print SQL without executing (use before any destructive query)
   - `--catalog NAME`              →  override catalog
   - `--schema NAME`               →  override schema
   - `--env FILE`                  →  use a custom .env file (e.g. staging)
   - `--file FILE`                 →  execute SQL from a .sql file

4. **Safety rules**
   - Always show the SQL before running it.
   - For write operations (INSERT / CREATE / DROP / ALTER), run `--dry-run` first and ask the user to confirm before executing for real.

5. **If connection fails** — check that `~/.trino.env` exists and `TRINO_HOST` is set:
   ```bash
   cat ~/.trino.env
   ```
   Template is at: `~/.local/share/trino/templates/trino.env`

## Natural language → SQL reference

| User says | SQL |
|---|---|
| "show all catalogs" | `SHOW CATALOGS` |
| "list schemas in X" | `SHOW SCHEMAS FROM X` |
| "list tables in X.Y" | `SHOW TABLES FROM X.Y` |
| "describe table X.Y.Z" | `DESCRIBE X.Y.Z` |
| "sample table X" | `SELECT * FROM X LIMIT 20` |
| "count rows in X" | `SELECT COUNT(*) FROM X` |
| "find tables with column X" | `SELECT table_schema, table_name FROM information_schema.columns WHERE column_name = 'X'` |
| "table size / stats" | `SHOW STATS FOR X` |
| "show partitions of X" | `SHOW PARTITIONS FROM X` |
| "query plan for ..." | `EXPLAIN (TYPE DISTRIBUTED) <sql>` |

## Common errors

| Error | Fix |
|---|---|
| `TRINO_HOST not set` | Edit `~/.trino.env` |
| `Authentication failed` | Check `TRINO_USER` / `TRINO_PASSWORD` |
| `SSL handshake failed` | Set `TRINO_VERIFY_SSL=false` |
| `Catalog does not exist` | Run `/trino SHOW CATALOGS` to list available |
| `Query exceeded memory limit` | Add `--limit N` or push down filters |
