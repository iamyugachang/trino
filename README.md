# trino skill

Natural language + SQL interface to [Trino](https://trino.io/), packaged as both
a **Claude Code `/trino` slash command** and a **Hermes skill**.

Source: https://github.com/iamyugachang/trino

## Quick start

```bash
git clone https://github.com/iamyugachang/trino.git
cd trino
./install.sh                    # installs to both Claude Code & Hermes
$EDITOR ~/.trino.env            # fill in TRINO_HOST / USER / PASSWORD
```

Then in Claude Code:
```
/trino SHOW CATALOGS
/trino hive 有幾個 schema
```

Or in Hermes: *"use the trino skill to list schemas in hive"*

## Features

- **Slash command + skill trigger** — call `/trino` explicitly or let Claude Code
  pick the skill from natural-language triggers.
- **Auto-save** — every query writes a markdown copy to `./trino-output/<ts>.md`.
- **uv-aware install** — uses `uv pip` when available, falls back to `pip`.
- **Dual environment** — same client works in Claude Code and Hermes.

## Install targets

```bash
./install.sh --target claude-code   # /trino slash command + Claude Code skill
./install.sh --target hermes        # ~/.hermes/skills/data-science/trino
./install.sh --target both          # default
```

## Connection

Copy a template and edit:
```bash
cp templates/trino.env ~/.trino.env          # production / company
cp templates/trino.env.docker ~/.trino.env   # local Docker preset
```

| Variable | Default |
|---|---|
| `TRINO_HOST` | (required) |
| `TRINO_PORT` | 8080 |
| `TRINO_USER` | `$USER` |
| `TRINO_PASSWORD` | (none) |
| `TRINO_HTTPS` | false |
| `TRINO_VERIFY_SSL` | true |
| `TRINO_CATALOG` | tpch |
| `TRINO_SCHEMA` | tiny |

## Flags

| Flag | Description |
|---|---|
| `--format` | `aligned` *(default)*, `markdown`, `csv`, `tsv`, `json` |
| `--save FILE` | Override auto-save markdown path |
| `--no-save` | Skip auto-save |
| `--output FILE` | Write `--format` to FILE (and skip auto-save) |
| `--limit N` | Append `LIMIT N` |
| `--dry-run` | Print SQL only |
| `--env FILE` | Use a different `.env` |
| `--catalog` / `--schema` | Override |
| `--file FILE` | Read SQL from a file |

## Test

See [`TESTING.md`](TESTING.md) for the three-environment checklist.

```bash
cd docker && docker compose up -d && cd ..
python3 -m pip install pytest
python3 -m pytest tests/ -v
```

## License

MIT
