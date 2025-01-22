"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from __future__ import annotations

from contextlib import suppress
import subprocess
import niquests
from typing import TYPE_CHECKING

from app import constants

if TYPE_CHECKING:
    from app.db import DataBase


def compute_rewards(blocks: set[int]) -> float:
    """
    Block generators get 70% + voting fractions (not computed here).
    Source: https://github.com/dusk-network/rusk/blob/rusk-1.0.0/rusk/src/lib/node.rs#L132-L157
    Source: https://github.com/dusk-network/audits/blob/main/core-audits/2024-09_economic-protocol-design_pol-finance.pdf
    """
    amount = 0.0
    for block in blocks:
        if block == 113_529_597:  # Last mint
            dusk = 0.05428
        elif block >= 100_915_201:  # Period 9
            dusk = 0.07757
        elif block >= 88_300_801:  # Period 8
            dusk = 0.15514
        elif block >= 75_686_401:  # Period 7
            dusk = 0.31027
        elif block >= 63_072_001:  # Period 6
            dusk = 0.62054
        elif block >= 50_457_601:  # Period 5
            dusk = 1.24109
        elif block >= 37_843_201:  # Period 4
            dusk = 2.48218
        elif block >= 25_228_801:  # Period 3
            dusk = 4.96435
        elif block >= 12_614_401:  # Period 2
            dusk = 9.9287
        elif block >= 1:  # Period 1
            dusk = 19.8574
        else:  # Genesis
            dusk = 0.0
        amount += dusk * 0.7
    return amount


def get_current_rewards() -> float:
    with niquests.post(f"https://{constants.NODE_HOSTNAME}/on/node/provisioners", headers=constants.HEADERS) as req:
        return next((prov["reward"] / 10**9 for prov in req.json() if prov["key"] == constants.PROVISIONER), 0.0)


def play_sound_of_the_riches() -> None:
    if not constants.PLAY_SOUND:
        return

    with suppress(Exception):
        subprocess.call(constants.PLAY_SOUND_CMD)
        print("🔔")


def update_rewards(data: "DataBase", new_blocks: set[int]) -> None:
    with suppress(Exception):
        data.rewards = get_current_rewards()

    if data.total_rewards:
        data.total_rewards += compute_rewards(new_blocks)
    else:
        data.total_rewards = compute_rewards(data.blocks)

    play_sound_of_the_riches()
