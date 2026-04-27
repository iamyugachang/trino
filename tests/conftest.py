"""pytest: wait for Trino Docker before running tests."""
import time
import json
import pytest
import urllib.request


def wait_for_trino(host="localhost", port=8080, timeout=120):
    url = f"http://{host}:{port}/v1/info"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                info = json.loads(resp.read())
                if info.get("starting") is False:
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


def pytest_configure(config):
    print("\n[conftest] waiting for Trino on localhost:8080 ...", flush=True)
    if not wait_for_trino():
        pytest.exit(
            "Trino not reachable after 120s.\n"
            "Start it with:  cd docker && docker compose up -d",
            returncode=1,
        )
    print("[conftest] Trino ready ✅", flush=True)
