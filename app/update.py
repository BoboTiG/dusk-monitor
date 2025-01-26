"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from contextlib import suppress
import json
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


def scan_the_blockchain(last_db_block: int, last_block: int) -> tuple[bool, int, set[int], dict]:
    blocks: set[int] = set()
    history: dict[str, tuple[int, str]] = {}
    status = True
    provisioner = constants.PROVISIONER

    if constants.DEBUG:
        print(f"DB last-block = {last_db_block:,}")
        print(f"BC last-block = {last_block:,}")

    for from_block in range(last_db_block, last_block, constants.GQL_GET_BLOCKS_ITEMS_COUNT):
        to_block = from_block + constants.GQL_GET_BLOCKS_ITEMS_COUNT
        query = constants.GQL_GET_BLOCKS % (from_block, to_block)

        if constants.DEBUG:
            print(f"POST {constants.URL_RUES_GQL!r} [{from_block:,}, {to_block:,}]")

        try:
            with niquests.post(constants.URL_RUES_GQL, headers=constants.HEADERS, data=query) as req:
                req.raise_for_status()
                res = req.json()
        except Exception as exc:
            if constants.DEBUG:
                print(f"Error in scan_the_blockchain(): {exc}")
            last_block = from_block
            status = False
            break

        for block in res["blocks"]:
            # New generated block
            if block["header"]["generatorBlsPubkey"] == provisioner:
                blocks.add(block["header"]["height"])

            for transaction in block["transactions"]:
                tx_data = json.loads(transaction["tx"]["json"])

                # Provisioner action
                # TODO: decode TX fn_args to retrieve amounts staked/unstaked/withdrawed/transfered
                if (
                    tx_data["type"] == "moonlight"
                    and tx_data["sender"] == provisioner
                    and tx_data["call"]["contract"] == constants.CONTRACT_STAKING
                ):
                    history[str(block["header"]["timestamp"])] = tx_data["call"]["fn_name"], block["header"]["height"]

    return status, last_block, blocks, history


def get_current_block() -> int:
    return int(subprocess.check_output(constants.CMD_GET_NODE_SYNCED_BLOCK, text=True).strip())


def get_last_block() -> int:
    with niquests.post(constants.URL_RUES_GQL, headers=constants.HEADERS, data=constants.GQL_LAST_BLOCK) as req:
        req.raise_for_status()
        return req.json()["block"]["header"]["height"]


def get_provisioner_data() -> dict:
    with niquests.post(constants.URL_RUES_PROVISIONERS, headers=constants.HEADERS) as req:
        req.raise_for_status()
        return next((prov for prov in req.json() if prov["key"] == constants.PROVISIONER), {})


def play_sound_of_the_riches() -> None:
    if constants.PLAY_SOUND:
        with suppress(Exception):
            subprocess.check_call(constants.PLAY_SOUND_CMD)
            if constants.DEBUG:
                print("🔔")


def update() -> None:
    data = db.load()

    # Force a full scan
    if data.version < constants.DB_VERSION:
        data.last_block = 0

    try:
        status, last_block, blocks, history = scan_the_blockchain(data.last_block, get_last_block())
    except Exception as exc:
        if constants.DEBUG:
            print(f"Error in update(): {exc}")
        return

    with suppress(Exception):
        provisioner_data = get_provisioner_data()
        data.rewards = provisioner_data["reward"] / 10**9
        data.slash_hard = provisioner_data["hard_faults"]
        data.slash_soft = provisioner_data["faults"]

    with suppress(Exception):
        data.current_block = get_current_block()

    if history:
        data.history.update(history)

    if new_blocks := blocks - data.blocks:
        data.blocks |= new_blocks
        if data.total_rewards:
            data.total_rewards += compute_rewards(new_blocks)
        else:
            data.total_rewards = compute_rewards(data.blocks)

        if constants.DEBUG:
            print(f"New blocks persisted: {', '.join(str(b) for b in sorted(new_blocks))}")

        play_sound_of_the_riches()

    data.last_block = last_block

    if status:
        data.version = constants.DB_VERSION

    db.save(data)
