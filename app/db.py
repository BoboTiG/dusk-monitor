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
    if not (new_blocks := blocks - data[constants.DB_KEY_BLOCKS]):
        return

    data[constants.DB_KEY_BLOCKS] |= new_blocks
    utils.update_rewards(data, new_blocks)

    if last_block:
        data[constants.DB_KEY_LAST_CHECKED_BLOCK] = last_block

    save(data)
    print(f"New blocks persisted: {', '.join(str(b) for b in sorted(new_blocks))}")


def load() -> dict[str, set[int] | float]:
    data = {}
    with suppress(FileNotFoundError):
        data = json.loads(constants.DB_FILE.read_text())

    return {
        # Generated blocks list
        constants.DB_KEY_BLOCKS: set(data.get(constants.DB_KEY_BLOCKS, [])),
        # Last checked block (used in --update)
        constants.DB_KEY_LAST_CHECKED_BLOCK: data.get(constants.DB_KEY_LAST_CHECKED_BLOCK, 0),
        # Current rewards
        constants.DB_KEY_REWARDS: data.get(constants.DB_KEY_REWARDS, 0.0),
        # Total theoric rewards
        constants.DB_KEY_TOTAL_REWARDS: data.get(constants.DB_KEY_TOTAL_REWARDS, 0.0),
    }


def save(data: dict[str, set[int] | float]) -> None:
    blocks = ",\n        ".join(
        str(batch)[1:-1] for batch in batched(sorted(data[constants.DB_KEY_BLOCKS]), constants.DB_BLOCKS_PER_LINE)
    )
    output = f"""{{
    "{constants.DB_KEY_BLOCKS}": [
        {blocks.rstrip(",")}
    ],
    "{constants.DB_KEY_LAST_CHECKED_BLOCK}": {data[constants.DB_KEY_LAST_CHECKED_BLOCK]},
    "{constants.DB_KEY_REWARDS}": {data[constants.DB_KEY_REWARDS]},
    "{constants.DB_KEY_TOTAL_REWARDS}": {data[constants.DB_KEY_TOTAL_REWARDS]}
}}
"""
    constants.DB_FILE.write_text(output)
