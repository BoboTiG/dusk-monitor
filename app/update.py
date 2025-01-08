"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from subprocess import check_output

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
    blocks_accepted = get_accepted_blocks()
    if constants.DEBUG:
        print(f"{blocks_accepted = }")

    blocks_rejected = get_rejected_blocks()
    if constants.DEBUG:
        print(f"{blocks_rejected = }")

    if not blocks_accepted and not blocks_rejected:
        return

    data = db.load()
    has_changed = False

    if blocks_accepted and data["accepted"] != blocks_accepted:
        data["accepted"] = data["accepted"] | blocks_accepted
        data["rewards"] = compute_rewards(data["accepted"])
        has_changed = True
    elif data["accepted"] and not data["rewards"]:
        data["rewards"] = compute_rewards(data["accepted"])
        has_changed = True
    if blocks_rejected and data["rejected"] != blocks_rejected:
        data["rejected"] = data["rejected"] | blocks_rejected
        has_changed = True

    if has_changed:
        db.save(data)
