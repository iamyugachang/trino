# trino

Command-line SQL client for [Trino](https://trino.io/).  
Configure via `.trino.env`, then run queries in any format.

## Install

```bash
git clone https://github.com/iamyugachang/trino.git
cd trino
pip install trino
chmod +x trino
```

Optionally add to PATH:
```bash
ln -s $(pwd)/trino ~/.local/bin/trino-cli
```

## Setup

```bash
cp .env.example .trino.env
# edit .trino.env
```

`.trino.env` lookup order:
1. `--env /custom/path.env`
2. `./.trino.env` (project-local)
3. `~/.trino.env` (user-global)

## Usage

```bash
# basic
./trino "SHOW CATALOGS"
./trino "SHOW TABLES FROM hive.analytics"
./trino "SELECT * FROM tpch.tiny.nation LIMIT 5"

# output formats
./trino --format csv     "SELECT * FROM tpch.tiny.orders" --output orders.csv
./trino --format json    "SELECT nationkey, name FROM tpch.tiny.nation LIMIT 3"
./trino --format aligned "DESCRIBE tpch.tiny.nation"

# safety
./trino --dry-run     "DROP TABLE hive.myschema.old_data"
./trino --limit 100   "SELECT * FROM hive.myschema.huge_table"

# sql file
./trino --file my_query.sql

# switch environment
./trino --env ~/.trino-staging.env "SHOW SCHEMAS FROM hive"
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
cd docker
docker compose up -d

cd ..
pip install pytest
pytest tests/ -v
```

The test suite covers connection, TPC-H queries, all output formats,  
file output, dry-run, DDL/DML on `memory` catalog, and error handling.

## `.trino.env` reference

```bash
TRINO_HOST=trino.your-company.com
TRINO_PORT=443           # 443=HTTPS, 8080=HTTP
TRINO_USER=your_username
TRINO_PASSWORD=          # leave blank if no auth
TRINO_HTTPS=true
TRINO_VERIFY_SSL=false   # false for self-signed certs
TRINO_CATALOG=hive
TRINO_SCHEMA=default
```

## License

MIT
