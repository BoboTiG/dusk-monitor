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

        if data["rewards"]:
            data["rewards"] += utils.compute_rewards(new_blocks)
        else:
            data["rewards"] = utils.compute_rewards(data["blocks"])

        save(data)

        print(f"New blocks persisted: {', '.join(str(b) for b in sorted(new_blocks))}")


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
