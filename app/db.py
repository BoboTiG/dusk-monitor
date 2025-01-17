"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

import json
from contextlib import suppress

from app import constants, utils


def add(blocks: set[int]) -> None:
    data = load()
    if not (new_blocks := blocks - data["blocks"]):
        return

    data["blocks"] |= new_blocks
    utils.update_rewards(data, new_blocks)
    save(data)
    print(f"New blocks persisted: {', '.join(str(b) for b in sorted(new_blocks))}")


def load() -> dict[str, set[int] | float]:
    data = {}
    with suppress(FileNotFoundError):
        data = json.loads(constants.DB_FILE.read_text())

    return {
        # Generated blocks list
        "blocks": set(data.get("blocks", [])),
        # Current rewards
        "rewards": data.get("rewards", 0.0),
        # Total theoric rewards
        "total-rewards": data.get("total-rewards", 0.0),
    }


def save(data: dict[str, set[int] | float]) -> None:
    data["blocks"] = sorted(data["blocks"])
    constants.DB_FILE.write_text(json.dumps(data, sort_keys=True))
