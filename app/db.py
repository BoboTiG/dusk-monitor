"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from contextlib import suppress
import json

from app import constants


def load() -> dict[str, set[int] | float]:
    data = {}
    with suppress(FileNotFoundError):
        data = json.loads(constants.DB_FILE.read_text())

    return {
        "blocks": set(data.get("blocks", [])),
        "rewards": data.get("rewards", 0.0),
    }


def save(data: dict[str, set[int] | float]) -> None:
    data["blocks"] = sorted(data["blocks"])
    constants.DB_FILE.write_text(json.dumps(data, sort_keys=True))
