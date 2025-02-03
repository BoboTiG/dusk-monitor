"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

import json
import subprocess

import niquests

from app import config, constants, db


def scan_the_blockchain(last_block_db: int, last_block_bc: int) -> tuple[bool, int, set[int], dict]:
    blocks: set[int] = set()
    history: db.History = {}
    status = True
    provisioner = config.PROVISIONER

    if constants.DEBUG:
        print(f"DB last-block = {last_block_db:,}")
        print(f"BC last-block = {last_block_bc:,}")

    for from_block in range(last_block_db, last_block_bc, constants.GQL_GET_BLOCKS_ITEMS_COUNT):
        to_block = from_block + constants.GQL_GET_BLOCKS_ITEMS_COUNT
        query = constants.GQL_GET_BLOCKS % (from_block, to_block)

        if constants.DEBUG:
            print(f"POST {constants.URL_RUES_GQL!r} [{from_block:,}, {to_block:,}]")

        try:
            with niquests.post(constants.URL_RUES_GQL, headers=constants.HEADERS, data=query) as req:
                req.raise_for_status()
                res = req.json()
        except Exception as exc:
            print(f"Error in scan_the_blockchain(): {exc}")
            last_block_bc = from_block
            status = False
            break

        for block in res["blocks"]:
            # New generated block
            if block["header"]["generatorBlsPubkey"] == provisioner:
                blocks.add(block["header"]["height"])

            # Provisioner action
            for transaction in block["transactions"]:
                tx_data = json.loads(transaction["tx"]["json"])

                if tx_data["type"] != "moonlight" or (
                    tx_data["sender"] != provisioner and tx_data["receiver"] != provisioner
                ):
                    continue

                if tx_data["call"]:
                    # stake/unstake, convert (from public to shielded), withdraw
                    fn_name = str(tx_data["call"]["fn_name"])
                    amount = int(tx_data["deposit"])
                else:
                    fn_name = "transfer"
                    amount = int(tx_data["value"])
                    if tx_data["sender"] == provisioner:
                        amount *= -1

                history[str(block["header"]["timestamp"])] = fn_name, amount, int(block["header"]["height"])

    return status, last_block_bc, blocks, history


def fill_empty_amounts(history: db.History) -> None:
    """This function is useful to get unstake/withdraw amounts."""
    if all(amount != 0 for _, amount, _ in history.values()):
        return

    query = constants.GQL_FULL_HISTORY % config.PROVISIONER
    with niquests.post(constants.URL_RUES_GQL, headers=constants.HEADERS, data=query) as req:
        req.raise_for_status()
        full_history = req.json()["fullMoonlightHistory"]["json"]

    for timestamp, (fn_name, amount, block) in history.copy().items():
        if amount != 0:
            continue

        for item in full_history:
            if item["block_height"] != block:
                continue

            correct_amount = item["events"][0]["data"]["value"]
            history[timestamp] = (fn_name, correct_amount, block)
            break


def get_last_block() -> int:
    with niquests.post(constants.URL_RUES_GQL, headers=constants.HEADERS, data=constants.GQL_LAST_BLOCK) as req:
        req.raise_for_status()
        return req.json()["block"]["header"]["height"]


def get_provisioner_data() -> dict:
    with niquests.post(constants.URL_RUES_PROVISIONERS, headers=constants.HEADERS) as req:
        req.raise_for_status()
        return next((prov for prov in req.json() if prov["key"] == config.PROVISIONER), {})


def play_sound_of_the_riches() -> None:
    if not config.PLAY_SOUND:
        return

    subprocess.check_call(constants.PLAY_SOUND_CMD, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if constants.DEBUG:
        print("🔔")


def update() -> None:
    if not config.PROVISIONER:
        print("Config file not found, go to the dashboard /setup page.")
        return

    data = db.load()

    # Force a full scan
    if data.version < constants.DB_VERSION:
        data.blocks = set()
        data.history = {}
        data.last_block = 0

    try:
        status, last_block, blocks, history = scan_the_blockchain(data.last_block, get_last_block())
    except Exception as exc:
        print(f"Error in update(): {exc}")
        return

    try:
        provisioner_data = get_provisioner_data()
        data.rewards = provisioner_data["reward"]
        data.slash_hard = provisioner_data["hard_faults"]
        data.slash_soft = provisioner_data["faults"]
    except Exception as exc:
        print(f"Error in get_provisioner_data(): {exc}")

    if history:
        data.history.update(history)

    try:
        fill_empty_amounts(data.history)
    except Exception as exc:
        print(f"Error in fill_empty_amounts(): {exc}")

    if new_blocks := blocks - data.blocks:
        data.blocks |= new_blocks
        if constants.DEBUG:
            print(f"New blocks persisted: {', '.join(str(b) for b in sorted(new_blocks))}")

        try:
            play_sound_of_the_riches()
        except Exception as exc:
            print(f"Error in play_sound_of_the_riches(): {exc}")

    data.last_block = last_block

    if status:
        data.version = constants.DB_VERSION

    db.save(data)
