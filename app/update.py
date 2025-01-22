"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from contextlib import suppress
import subprocess
import niquests

from app import constants, db


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


def get_generated_blocks(last_block: int) -> set[int]:
    data = db.load()
    blocks: set[int] = set()
    url = f"https://{constants.NODE_HOSTNAME}/02/Chain"

    if constants.DEBUG:
        print(f"DB last-block = {data.last_block:,}")
        print(f"last-block    = {last_block:,}")

    for from_block in range(data.last_block, last_block, constants.GQL_GENERATED_BLOCKS_ITEMS_COUNT):
        to_block = from_block + constants.GQL_GENERATED_BLOCKS_ITEMS_COUNT

        if constants.DEBUG:
            print(f"POST {url!r} [{from_block:,}, {to_block:,}]")

        query = {"topic": "gql", "data": constants.GQL_GENERATED_BLOCKS % (from_block, to_block)}
        with niquests.post(url, headers=constants.HEADERS, json=query) as req:
            if new_blocks := {
                block["header"]["height"]
                for block in req.json()["blocks"]
                if block["header"]["generatorBlsPubkey"] == constants.PROVISIONER
            }:
                blocks.update(new_blocks)

    return blocks


def get_last_block() -> int:
    query = {"topic": "gql", "data": constants.GQL_LAST_BLOCK}
    with niquests.post(f"https://{constants.NODE_HOSTNAME}/02/Chain", headers=constants.HEADERS, json=query) as req:
        return req.json()["block"]["header"]["height"]


def get_provisioner_data() -> dict:
    with niquests.post(f"https://{constants.NODE_HOSTNAME}/on/node/provisioners", headers=constants.HEADERS) as req:
        return next((prov for prov in req.json() if prov["key"] == constants.PROVISIONER), {})


def play_sound_of_the_riches() -> None:
    if constants.PLAY_SOUND:
        with suppress(Exception):
            subprocess.call(constants.PLAY_SOUND_CMD)
            if constants.DEBUG:
                print("🔔")


def update() -> None:
    try:
        last_block = get_last_block()
        blocks = get_generated_blocks(last_block)
    except niquests.exceptions.JSONDecodeError as exc:
        print(f"Error in update(): {exc}")
        return

    data = db.load()

    with suppress(Exception):
        provisioner_data = get_provisioner_data()
        data.rewards = provisioner_data["reward"] / 10**9
        data.slash_hard = provisioner_data["hard_faults"]
        data.slash_soft = provisioner_data["faults"]

    if new_blocks := blocks - data.blocks:
        data.blocks |= new_blocks
        if data.total_rewards:
            data.total_rewards += compute_rewards(new_blocks)
        else:
            data.total_rewards = compute_rewards(data.blocks)
        print(f"New blocks persisted: {', '.join(str(b) for b in sorted(new_blocks))}")
        play_sound_of_the_riches()

    data.last_block = last_block

    db.save(data)
