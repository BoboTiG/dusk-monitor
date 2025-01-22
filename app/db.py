"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

import json
from itertools import islice
from contextlib import suppress

from app import constants, utils


def batched(iterable, n):
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        yield batch


def add(blocks: set[int], last_block: int = 0) -> None:
    data = load()
    if not (new_blocks := blocks - data["blocks"]):
        return

    data["blocks"] |= new_blocks
    utils.update_rewards(data, new_blocks)

    if last_block:
        data["last-checked-block"] = last_block

    save(data)
    print(f"New blocks persisted: {', '.join(str(b) for b in sorted(new_blocks))}")


def load() -> dict[str, set[int] | float]:
    data = {}
    with suppress(FileNotFoundError):
        data = json.loads(constants.DB_FILE.read_text())

    return {
        # Generated blocks list
        "blocks": set(data.get("blocks", [])),
        # Last checked block (used in --update)
        "last-checked-block": data.get("last-checked-block", 0),
        # Current rewards
        "rewards": data.get("rewards", 0.0),
        # Total theoric rewards
        "total-rewards": data.get("total-rewards", 0.0),
    }


def save(data: dict[str, set[int] | float]) -> None:
    blocks = ",\n        ".join(
        str(batch)[1:-1] for batch in batched(sorted(data["blocks"]), constants.DB_BLOCKS_PER_LINE)
    )
    output = f"""{{
    "blocks": [
        {blocks.rstrip(",")}
    ],
    "last-checked-block": {data["last-checked-block"]},
    "rewards": {data["rewards"]},
    "total-rewards": {data["total-rewards"]}
}}
"""
    constants.DB_FILE.write_text(output)
