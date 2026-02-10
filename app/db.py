"""
This is part of the Dusk Node Monitoring project.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from __future__ import annotations

import fcntl
import functools
import json
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import islice
from pathlib import Path
from typing import TYPE_CHECKING, Any

from app import constants

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

# "timestamp": ("fn_name", amount, block)
History = dict[str, tuple[str, int, int]]


@dataclass(slots=True, kw_only=True)
class DataBase:
    rewards: int
    last_block: int
    slash_hard: int
    slash_soft: int
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
        rewards=int(data.get(constants.DB_KEY_REWARDS, 0)),
        last_block=int(data.get(constants.DB_KEY_LAST_BLOCK, 0)),
        slash_soft=int(data.get(constants.DB_KEY_SLASH_SOFT, 0)),
        slash_hard=int(data.get(constants.DB_KEY_SLASH_HARD, 0)),
        history=data.get(constants.DB_KEY_HISTORY, {}),
        blocks=set(data.get(constants.DB_KEY_BLOCKS, [])),
        version=int(data.get(constants.DB_KEY_VERSION, 1)),
    )


def locker(kind: str) -> Callable:
    """File locking mechanism to protect against concurrent read/write mess."""

    def decorator(function: Callable) -> Callable:
        @functools.wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Callable:
            lock_file = Path(f"/tmp/{kind}.lock")
            with lock_file.open(mode="w") as fh:
                fcntl.flock(fh, fcntl.LOCK_EX)
                try:
                    return function(*args, **kwargs)
                finally:
                    fcntl.flock(fh, fcntl.LOCK_UN)
        return wrapper

    return decorator


@locker(constants.DB_FILE.name)
def save(data: DataBase) -> None:
    glue = ",\n        "
    history = glue.join(
        f'"{timestamp}": ["{fn_name}", {amount}, {block}]'
        for timestamp, (fn_name, amount, block) in sorted(data.history.items(), reverse=True)
    )
    blocks = glue.join(batched(sorted(data.blocks), constants.DB_BLOCKS_PER_LINE))

    constants.DB_FILE.write_text(f"""{{
    "{constants.DB_KEY_REWARDS}": {data.rewards},
    "{constants.DB_KEY_LAST_BLOCK}": {data.last_block},
    "{constants.DB_KEY_SLASH_SOFT}": {data.slash_soft},
    "{constants.DB_KEY_SLASH_HARD}": {data.slash_hard},
    "{constants.DB_KEY_HISTORY}": {{
        {history}
    }},
    "{constants.DB_KEY_BLOCKS}": [
        {blocks}
    ],
    "{constants.DB_KEY_VERSION}": {data.version}
}}
""")

    now = datetime.now(tz=UTC).replace(second=0, microsecond=0)
    with constants.REWARDS_FILE.open(mode="+at") as fh:
        fh.write(f"{int(now.timestamp())}|{data.rewards / 10**9}\n")
