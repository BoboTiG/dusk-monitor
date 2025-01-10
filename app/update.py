"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

import niquests

from app import constants, db


def get_generated_blocks() -> set[int]:
    query = {"topic": "gql", "data": constants.GENERATED_BLOCKS_GRAPHQL_QUERY}
    with niquests.post(f"https://{constants.NODE_HOSTNAME}/02/Chain", headers=constants.HEADERS, json=query) as req:
        return {block["header"]["height"] for block in req.json()["blocks"] if block["header"]["generatorBlsPubkey"] == constants.PROVISIONER}


def update() -> None:
    try:
        blocks = get_generated_blocks()
    except niquests.exceptions.JSONDecodeError as exc:
        print(f"Error in get_generated_blocks(): {exc}")
    else:
        if blocks:
            db.add(blocks)
