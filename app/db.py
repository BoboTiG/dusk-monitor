"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""
import json

import app.constants as constants


def load() -> constants.Database:
    data = json.loads(constants.DB_FILE.read_text())
    constants.PROVISIONER = data["provisioner"]
    return {
        "rejected": set(data.get("rejected", [])),
        "accepted": set(data.get("accepted", [])),
    }


def save(data: constants.Database) -> None:
    constants.DB_FILE.write_text(json.dumps(data, sort_keys=True))
