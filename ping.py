#!/usr/bin/env python3
"""Ping a Minecraft server and append the result to a CSV log.

Config (environment variables):
  MC_HOST      Server address, e.g. "mc.example.com" or "mc.example.com:25565" (required)
  MC_EDITION   "java" (default) or "bedrock"
  MC_TIMEOUT   Seconds to wait for a response (default 10)
  MC_LOG_FILE  Output CSV path (default logs/player_log.csv)
"""
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from mcstatus import BedrockServer, JavaServer

FIELDS = [
    "timestamp_utc",
    "online",
    "players_online",
    "players_max",
    "latency_ms",
    "version",
    "motd",
    "player_sample",
    "error",
]


def clean(text) -> str:
    """Flatten text so it stays on one CSV line."""
    return " ".join(str(text).split())


def query(host: str, edition: str, timeout: float) -> dict:
    row = {f: "" for f in FIELDS}
    row["timestamp_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row["online"] = 0

    try:
        if edition == "bedrock":
            status = BedrockServer.lookup(host, timeout=timeout).status()
            row["players_online"] = status.players.online
            row["players_max"] = status.players.max
            row["latency_ms"] = round(status.latency, 1)
            row["version"] = status.version.name
            row["motd"] = clean(status.motd.to_plain())
        else:
            status = JavaServer.lookup(host, timeout=timeout).status()
            row["players_online"] = status.players.online
            row["players_max"] = status.players.max
            row["latency_ms"] = round(status.latency, 1)
            row["version"] = status.version.name
            row["motd"] = clean(status.motd.to_plain())
            # Many servers hide or truncate this list, so it's only a sample.
            sample = status.players.sample or []
            row["player_sample"] = ";".join(p.name for p in sample)
        row["online"] = 1
    except Exception as exc:  # server down, timeout, DNS failure, etc.
        row["players_online"] = 0
        row["error"] = clean(f"{type(exc).__name__}: {exc}")[:200]

    return row


def append_row(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def main() -> int:
    host = os.environ.get("MC_HOST", "mc.oomfsmp.com").strip()
    if not host:
        print("MC_HOST is not set", file=sys.stderr)
        return 1

    edition = os.environ.get("MC_EDITION", "java").strip().lower()
    timeout = float(os.environ.get("MC_TIMEOUT", "10"))
    log_file = Path(os.environ.get("MC_LOG_FILE", "logs/player_log.csv"))

    row = query(host, edition, timeout)
    append_row(log_file, row)
    print({k: v for k, v in row.items() if v != ""})
    return 0  # an offline server is a valid data point, not a job failure


if __name__ == "__main__":
    sys.exit(main())