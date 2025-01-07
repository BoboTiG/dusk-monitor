"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""
from os import getenv
from pathlib import Path

# Local files
ROOT = Path(__file__).parent.parent
DB_FILE = ROOT / "db.json"
PROVISIONER = (ROOT / "provisioner.txt").read_text().strip()

# Mainnet URL
NODE_URL = "https://nodes.dusk.network/02/Chain"
HEADERS = {"User-Agent": "https://github.com/BoboTiG/dusk-monitor"}
ACCEPTED_BLOCKS_GRAPHQL_QUERY = (
    # FIXME: Find a more efficient query, like passing `generatorBlsPubkey == "PROVISIONER"` as a condition directly.
    "fragment BlockInfo on "
    "Block { header { height, generatorBlsPubkey } } "
    "query() { blocks(last: 10000) {...BlockInfo} }"
)

# Local web server
HOST = "0.0.0.0"
PORT = sum(ord(c) for c in "Dusk Node Monitoring")  # Hint: one-thousand-twenty-three
DEBUG = True

# SSH commands to get data from the node
CMD_SSH = ["ssh", "-t", getenv("DUSK_SSH_HOSTNAME", "dusk")]
CMD_GET_BLOCK_HEIGHTS = [*CMD_SSH, "source .profile ; get_block_heights"]
CMD_LIST_REJECTED_BLOCKS = [*CMD_SSH, "source .profile ; list_rejected_blocks"]

# Types
Database = dict[str, list[int]]
