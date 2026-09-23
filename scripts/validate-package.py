"""Render the buyer package without starting services or reading real secrets."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
version_names = ("LYRITHM_VERSION", "LYRITHM_ENGINE_VERSION", "LYRITHM_DASHBOARD_VERSION", "LYRITHM_WORKER_VERSION")
env = {k: v for k, v in os.environ.items() if not k.startswith(("LYRITHM_", "COMPOSE_"))}
env.update(DB_PASSWORD="package-validation-only", LYRITHM_MASTER_KEY="package-validation-only", GHCR_OWNER="lyrithm-io")

with tempfile.TemporaryDirectory() as directory:
    empty_env = Path(directory) / "empty.env"
    empty_env.touch()
    for overrides, expected in [
        ({}, ("1.1.0", "1.1.0", "1.1.0")),
        ({"LYRITHM_VERSION": "legacy-test"}, ("legacy-test",) * 3),
        (dict(zip(version_names, ("fallback-test", "engine-test", "dashboard-test", "worker-test"))),
         ("engine-test", "dashboard-test", "worker-test")),
    ]:
        rendered = subprocess.check_output([
            "docker", "compose", "--env-file", str(empty_env),
            "-f", str(root / "docker-compose.personal.yml"), "config", "--format", "json",
        ], env=env | overrides, text=True)
        services = json.loads(rendered)["services"]
        assert set(services) == {"init-data", "postgres", "redis", "strategy-worker-python", "engine", "dashboard"}
        for service, version in zip(("engine", "dashboard", "strategy-worker-python"), expected):
            assert services[service]["image"].endswith(":" + version), service
        assert services["init-data"]["image"] == services["engine"]["image"]
        assert services["engine"]["environment"]["LYRITHM_VERSION"] == expected[0]
        assert services["engine"]["environment"]["LYRITHM_TRADING_INITIAL_STATE"] == "idle"
        assert "LYRITHM_BACKUP_ENCRYPTION_KEY" in services["engine"]["environment"]
        assert services["init-data"]["network_mode"] == "none"
        for service in ("engine", "strategy-worker-python"):
            assert services[service]["depends_on"]["init-data"]["condition"] == "service_completed_successfully"
        for name, service in services.items():
            if name != "dashboard":
                assert not service.get("ports"), name
        assert all(port["host_ip"] == "127.0.0.1" for port in services["dashboard"]["ports"])
        worker_sources = next(v for v in services["strategy-worker-python"]["volumes"] if v["source"] == "strategy_sources")
        engine_sources = next(v for v in services["engine"]["volumes"] if v["source"] == "strategy_sources")
        assert worker_sources["read_only"] and not engine_sources.get("read_only", False)
        redis_args = services["redis"]["command"]
        for option, value in (("--appendonly", "yes"), ("--appendfsync", "always"), ("--maxmemory-policy", "volatile-lru")):
            assert redis_args[redis_args.index(option) + 1] == value
        assert any(v["source"] == "redis_data" and v["target"] == "/data" for v in services["redis"]["volumes"])

print("Package validation passed: default, legacy and independent image pins; startup order; local ports; durable volumes.")
