"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import islice
from contextlib import suppress
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app import constants

if TYPE_CHECKING:
    from typing import Iterator


@dataclass(slots=True, kw_only=True)
class DataBase:
    blocks: set[int]
    current_block: int
    history: dict[str, tuple[int, str]]
    last_block: int
    rewards: float
    slash_hard: int
    slash_soft: int
    total_rewards: float
    version: int


def batched(iterable: list[int], n: int) -> Iterator[str]:
    iterator = iter(iterable)
    while batch := list(islice(iterator, n)):
        yield str(batch)[1:-1]


def load() -> DataBase:
    data = {}
    with suppress(FileNotFoundError):
        data = json.loads(constants.DB_FILE.read_text())

    return DataBase(
        blocks=set(data.get(constants.DB_KEY_BLOCKS, [])),
        current_block=int(data.get(constants.DB_KEY_CURRENT_BLOCK, 0)),
        history=data.get(constants.DB_KEY_HISTORY, {}),
        last_block=int(data.get(constants.DB_KEY_LAST_BLOCK, 0)),
        rewards=float(data.get(constants.DB_KEY_REWARDS, 0.0)),
        slash_hard=int(data.get(constants.DB_KEY_SLASH_HARD, 0)),
        slash_soft=int(data.get(constants.DB_KEY_SLASH_SOFT, 0)),
        total_rewards=float(data.get(constants.DB_KEY_TOTAL_REWARDS, 0.0)),
        version=int(data.get(constants.DB_KEY_VERSION, 1)),
    )


def save(data: DataBase) -> None:
    glue = ",\n        "

    constants.DB_FILE.write_text(f"""{{
    "{constants.DB_KEY_BLOCKS}": [
        {glue.join(batched(sorted(data.blocks), constants.DB_BLOCKS_PER_LINE))}
    ],
    "{constants.DB_KEY_CURRENT_BLOCK}": {data.current_block},
    "{constants.DB_KEY_HISTORY}": {{
        {glue.join(f'"{k}": ["{v[0]}", {v[1]}]' for k, v in sorted(data.history.items()))}
    }},
    "{constants.DB_KEY_LAST_BLOCK}": {data.last_block},
    "{constants.DB_KEY_REWARDS}": {data.rewards},
    "{constants.DB_KEY_SLASH_HARD}": {data.slash_hard},
    "{constants.DB_KEY_SLASH_SOFT}": {data.slash_soft},
    "{constants.DB_KEY_TOTAL_REWARDS}": {data.total_rewards},
    "{constants.DB_KEY_VERSION}": {data.version}
}}
""")

    now = datetime.now(tz=UTC).replace(second=0, microsecond=0)
    with constants.REWARDS_FILE.open(mode="+at") as fh:
        fh.write(f"{int(now.timestamp())}|{data.rewards}\n")
