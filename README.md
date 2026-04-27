# trino

`/trino` slash command for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) —
execute SQL or natural language queries against [Trino](https://trino.io/).

## Install

```bash
git clone https://github.com/iamyugachang/trino.git
cd trino
./install.sh
```

What `install.sh` does:
1. Copies `scripts/` to `~/.local/share/trino/`
2. Copies `claude/commands/trino.md` to `~/.claude/commands/trino.md`
3. Creates `~/.trino.env` from the template (if missing)
4. Installs the `trino` Python package

## Setup

Edit your connection settings:
```bash
nano ~/.trino.env
```

```bash
TRINO_HOST=trino.your-company.com
TRINO_PORT=8080
TRINO_USER=your_username
TRINO_PASSWORD=
TRINO_HTTPS=false
TRINO_VERIFY_SSL=false
TRINO_CATALOG=hive
TRINO_SCHEMA=default
```

## Usage

Restart Claude Code after install, then:

```
/trino SHOW CATALOGS
/trino list tables in hive.analytics
/trino describe table hive.analytics.events
/trino SELECT * FROM tpch.tiny.nation LIMIT 5
/trino find tables with a user_id column
/trino --format csv --output out.csv SELECT * FROM hive.analytics.events
/trino --dry-run DROP TABLE hive.myschema.old_data
/trino --limit 100 SELECT * FROM hive.myschema.huge_table
```

## Test with Docker

Verify the client works before pointing at production:

```bash
cd docker && docker compose up -d && cd ..
pip install pytest
pytest tests/ -v   # 18 tests, ~10s
```

## Files

```
~/.claude/commands/trino.md     ← slash command definition (Claude Code reads this)
~/.local/share/trino/scripts/   ← Python client (called by the command)
~/.trino.env                    ← your connection settings
```

## License

MIT
