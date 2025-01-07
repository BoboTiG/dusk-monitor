"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""
from subprocess import check_output

import niquests

from app import constants, db


def get_accepted_blocks() -> set[int]:
    query = {"topic": "gql", "data": constants.ACCEPTED_BLOCKS_GRAPHQL_QUERY}
    with niquests.post(constants.NODE_URL, headers=constants.HEADERS, json=query) as req:
        return {
            block["header"]["height"]
            for block in req.json()["blocks"]
            if block["header"]["generatorBlsPubkey"] == constants.PROVISIONER
        }


def get_rejected_blocks() -> set[int]:
    output = check_output(constants.CMD_LIST_REJECTED_BLOCKS, text=True)
    return {int(block) for block in output.strip().split()}


def update() -> None:
    new_accepted = get_accepted_blocks()
    new_rejected = get_rejected_blocks()
    if not new_accepted and not new_rejected:
        return

    data = db.load()
    if new_accepted:
        data["accepted"] = sorted(set(data["accepted"]) | new_accepted)
    if new_rejected:
        data["rejected"] = sorted(set(data["rejected"]) | new_rejected)
    db.save(data)
