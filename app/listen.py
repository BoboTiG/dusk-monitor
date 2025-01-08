"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

import json

import niquests
import websockets

from app import constants, db


async def to_accepted_blocks():
    """https://docs.dusk.network/developer/integrations/rues/"""
    url = f"wss://{constants.NODE_HOSTNAME}/on"

    async with websockets.connect(url) as wss:
        session_id = await wss.recv()

        # Subscribe to the accepted blocks topic
        headers = constants.HEADERS | {"Rusk-Session-Id": session_id}
        with niquests.get(f"http://{constants.NODE_HOSTNAME}/on/blocks/accepted", headers=headers) as req:
            req.raise_for_status()

        while "listening":
            raw_block = await wss.recv()
            raw_block = raw_block[raw_block.find(b'{"header"'):]
            block = json.loads(raw_block)
            if block["header"]["generator_bls_pubkey"] == constants.PROVISIONER:
                db.add(set([block["header"]["height"]]))
