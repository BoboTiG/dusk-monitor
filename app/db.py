"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from __future__ import annotations

import json
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import islice
from typing import TYPE_CHECKING

from app import constants

if TYPE_CHECKING:
    from collections.abc import Iterator

# "timestamp": ("fn_name", amount, block)
History = dict[str, tuple[str, int, int]]


@dataclass(slots=True, kw_only=True)
class DataBase:
    current_block: int
    last_block: int
    slash_hard: int
    slash_soft: int
    current_rewards: int
    version: int
    history: History
    blocks: set[int]


def batched(iterable: list[int], n: int) -> Iterator[str]:
    iterator = iter(iterable)
    while batch := list(islice(iterator, n)):
        yield str(batch)[1:-1]


def load() -> DataBase:
    data = {}
    with suppress(FileNotFoundError):
        data = json.loads(constants.DB_FILE.read_text())

    return DataBase(
        current_block=int(data.get(constants.DB_KEY_CURRENT_BLOCK, 0)),
        last_block=int(data.get(constants.DB_KEY_LAST_BLOCK, 0)),
        slash_hard=int(data.get(constants.DB_KEY_SLASH_HARD, 0)),
        slash_soft=int(data.get(constants.DB_KEY_SLASH_SOFT, 0)),
        current_rewards=int(data.get(constants.DB_KEY_CURRENT_REWARDS, 0)),
        version=int(data.get(constants.DB_KEY_VERSION, 1)),
        history=data.get(constants.DB_KEY_HISTORY, {}),
        blocks=set(data.get(constants.DB_KEY_BLOCKS, [])),
    )


def save(data: DataBase) -> None:
    glue = ",\n        "
    history = glue.join(
        f'"{timestamp}": ["{fn_name}", {amount}, {block}]'
        for timestamp, (fn_name, amount, block) in sorted(data.history.items())
    )

    constants.DB_FILE.write_text(f"""{{
    "{constants.DB_KEY_CURRENT_BLOCK}": {data.current_block},
    "{constants.DB_KEY_LAST_BLOCK}": {data.last_block},
    "{constants.DB_KEY_SLASH_SOFT}": {data.slash_soft},
    "{constants.DB_KEY_SLASH_HARD}": {data.slash_hard},
    "{constants.DB_KEY_CURRENT_REWARDS}": {data.current_rewards},
    "{constants.DB_KEY_VERSION}": {data.version},
    "{constants.DB_KEY_HISTORY}": {{
        {history}
    }},
    "{constants.DB_KEY_BLOCKS}": [
        {glue.join(batched(sorted(data.blocks), constants.DB_BLOCKS_PER_LINE))}
    ]
}}
""")

    now = datetime.now(tz=UTC).replace(second=0, microsecond=0)
    with constants.REWARDS_FILE.open(mode="+at") as fh:
        fh.write(f"{int(now.timestamp())}|{data.current_rewards / 10**9}\n")
