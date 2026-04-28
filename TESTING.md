# Testing checklist

Three environments to verify. A & B run on this machine; C runs on the company laptop.

## Setup (once)

```bash
git clone https://github.com/iamyugachang/trino.git
cd trino
./install.sh --target both
```

Start a local Trino for A & B:
```bash
cd docker && docker compose up -d && cd ..
# wait ~30s for Trino to be ready: curl -fs http://localhost:8080/v1/info
```

---

## A. Hermes + Docker Trino

1. Make sure Docker Trino is up.
2. Use the docker preset env:
   ```bash
   cp templates/trino.env.docker ~/.trino.env
   ```
3. Run pytest:
   ```bash
   python3 -m pytest tests/ -v
   ```
   ✅ All ~20 tests pass.
4. In Hermes, ask: *"use the trino skill to SHOW CATALOGS"*
   ✅ returns `tpch / system / memory`.
5. In Hermes, ask: *"use trino to count schemas in tpch"*
   ✅ executes `SELECT COUNT(*) FROM tpch.information_schema.schemata`.

---

## B. Claude Code Router (this machine) + Docker Trino

1. `./install.sh --target claude-code`
2. Restart Claude Code.
3. In Claude Code:
   - `/trino SHOW CATALOGS` → ✅ returns `tpch / system / memory`
   - `/trino tpch 有幾個 schema` → ✅ counts schemas
   - `/trino list tables in tpch.tiny` → ✅ returns 8 tables
   - `/trino DROP TABLE tpch.tiny.nation` → ✅ asks for confirmation, runs `--dry-run` first
4. Check `./trino-output/` exists and has one `.md` per non-error query.

---

## C. Claude Code Router (company laptop) + company Trino

1. `git clone https://github.com/iamyugachang/trino.git && cd trino`
2. `./install.sh --target claude-code`
3. Edit `~/.trino.env` with company endpoint, user, password.
   - Set `TRINO_HTTPS=true` if endpoint is HTTPS.
   - Set `TRINO_VERIFY_SSL=false` for self-signed certs.
4. Restart Claude Code.
5. In Claude Code:
   - `/trino SHOW CATALOGS` → ✅ returns company catalogs.
   - `/trino <some_catalog> 有幾個 schema` → ✅ returns count.
   - `/trino list tables in <catalog>.<schema>` → ✅ returns table list.
   - `/trino describe <catalog>.<schema>.<some_table>` → ✅ returns column info.
6. Check `./trino-output/*.md` files captured the queries.

---

## Teardown

```bash
cd docker && docker compose down -v
```
