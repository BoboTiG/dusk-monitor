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
        "rejected": data.get("rejected", []),
        "accepted": data.get("accepted", []),
    }


def save(data: constants.Database) -> None:
    constants.DB_FILE.write_text(json.dumps(data, sort_keys=True))
