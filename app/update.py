"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

import niquests

from app import constants, db


def get_generated_blocks() -> tuple[int, set[int]]:
    data = db.load()
    last_block = get_last_block()
    blocks: set[int] = set()
    url = f"https://{constants.NODE_HOSTNAME}/02/Chain"

    if constants.DEBUG:
        print(f"last-checked-block = {data.last_checked_block:,}")
        print(f"last-block         = {last_block:,}")

    for from_block in range(data.last_checked_block, last_block, constants.GQL_GENERATED_BLOCKS_ITEMS_COUNT):
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

    return last_block, blocks


def get_last_block() -> int:
    query = {"topic": "gql", "data": constants.GQL_LAST_BLOCK}
    with niquests.post(f"https://{constants.NODE_HOSTNAME}/02/Chain", headers=constants.HEADERS, json=query) as req:
        return req.json()["block"]["header"]["height"]


def update() -> None:
    try:
        last_block, blocks = get_generated_blocks()
    except niquests.exceptions.JSONDecodeError as exc:
        print(f"Error in get_generated_blocks(): {exc}")
    else:
        db.add(blocks, last_block=last_block)
