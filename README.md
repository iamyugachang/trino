# trino skill

Python SQL client for [Trino](https://trino.io/).  
Install as a skill — the repo root is the skill directory.

## Install

```bash
git clone https://github.com/iamyugachang/trino.git \
    ~/.hermes/skills/data-science/trino

pip install trino
```

## Setup

```bash
cp ~/.hermes/skills/data-science/trino/templates/trino.env ~/.trino.env
nano ~/.trino.env   # fill in TRINO_HOST, TRINO_USER, etc.
```

## Usage

```bash
TRINO=~/.hermes/skills/data-science/trino/scripts/trino

python3 $TRINO "SHOW CATALOGS"
python3 $TRINO "SELECT * FROM tpch.tiny.nation LIMIT 5"
python3 $TRINO --format csv --output out.csv "SELECT * FROM tpch.tiny.orders"
python3 $TRINO --dry-run "DROP TABLE hive.myschema.old"
python3 $TRINO --limit 100 "SELECT * FROM hive.myschema.huge_table"
```

| Flag | Description |
|---|---|
| `--format` | `markdown` *(default)*, `aligned`, `csv`, `tsv`, `json` |
| `--output FILE` | Write result to file |
| `--limit N` | Append `LIMIT N` |
| `--dry-run` | Print SQL, don't execute |
| `--env FILE` | Custom `.env` file |
| `--catalog` / `--schema` | Override catalog / schema |
| `--file FILE` | Read SQL from file |

## Test with Docker

```bash
cd ~/.hermes/skills/data-science/trino/docker
docker compose up -d
cd ..
pip install pytest
pytest tests/ -v   # 18 tests
```

## `.trino.env` reference

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

## License

MIT
