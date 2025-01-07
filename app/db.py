"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""
from contextlib import suppress
import json

from app import constants


def load() -> constants.Database:
    data = {}
    with suppress(FileNotFoundError):
        data = json.loads(constants.DB_FILE.read_text())

    return {
        "accepted": set(data.get("accepted", [])),
        "rejected": set(data.get("rejected", [])),
        "rewards": data.get("rewards", 0.0),
    }


def save(data: constants.Database) -> None:
    data["accepted"] = sorted(data["accepted"])
    data["rejected"] = sorted(data["rejected"])
    constants.DB_FILE.write_text(json.dumps(data, sort_keys=True))
