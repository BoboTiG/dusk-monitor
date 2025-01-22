"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from dataclasses import dataclass
import json
from itertools import islice
from contextlib import suppress

from app import constants, utils


@dataclass(slots=True)
class DataBase:
    # Generated blocks
    blocks: set[int]
    # Last checked block (used in --update)
    last_checked_block: int
    # Current rewards
    rewards: float
    # Total theoric rewards
    total_rewards: float


def batched(iterable, n):
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        yield batch


def add(blocks: set[int], last_block: int = 0) -> None:
    data = load()
    need_persistence = False

    if new_blocks := blocks - data.blocks:
        data.blocks |= new_blocks
        utils.update_rewards(data, new_blocks)
        need_persistence = True
        print(f"New blocks persisted: {', '.join(str(b) for b in sorted(new_blocks))}")

    if last_block:
        data.last_checked_block = last_block
        need_persistence = True

    if need_persistence:
        save(data)


def load() -> DataBase:
    data = {}
    with suppress(FileNotFoundError):
        data = json.loads(constants.DB_FILE.read_text())

    return DataBase(
        set(data.get(constants.DB_KEY_BLOCKS, [])),
        int(data.get(constants.DB_KEY_LAST_CHECKED_BLOCK, 0)),
        float(data.get(constants.DB_KEY_REWARDS, 0.0)),
        float(data.get(constants.DB_KEY_TOTAL_REWARDS, 0.0)),
    )


def save(data: DataBase) -> None:
    blocks = ",\n        ".join(
        str(batch)[1:-1] for batch in batched(sorted(data.blocks), constants.DB_BLOCKS_PER_LINE)
    )
    output = f"""{{
    "{constants.DB_KEY_BLOCKS}": [
        {blocks.rstrip(",")}
    ],
    "{constants.DB_KEY_LAST_CHECKED_BLOCK}": {data.last_checked_block},
    "{constants.DB_KEY_REWARDS}": {data.rewards},
    "{constants.DB_KEY_TOTAL_REWARDS}": {data.total_rewards}
}}
"""
    constants.DB_FILE.write_text(output)
