"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

import json
from contextlib import suppress

from app import constants, utils


def add(blocks: set[int]) -> None:
    data = load()
    if new_blocks := blocks - data["blocks"]:
        data["blocks"] |= new_blocks
        data["rewards"] = utils.compute_rewards(data["blocks"])
        save(data)
        print(f"Saved accepted blocks: {', '.join(sorted(new_blocks))}")


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
