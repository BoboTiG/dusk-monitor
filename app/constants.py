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
NODE_HOSTNAME = "nodes.dusk.network"
HEADERS = {"User-Agent": "https://github.com/BoboTiG/dusk-monitor"}
LAST_BLOCKS_COUNT = getenv("LAST_BLOCKS_COUNT", 10000)
GENERATED_BLOCKS_GRAPHQL_QUERY = (
    "fragment BlockInfo on "
    "Block { header { height, generatorBlsPubkey } } "
    "query() { blocks(last: %s) {...BlockInfo} }" % LAST_BLOCKS_COUNT
)

# Local web server
HOST = "0.0.0.0"
PORT = sum(ord(c) for c in "Dusk Node Monitoring")  # Hint: one-thousand-twenty-three
DEBUG = True

# SSH command to get data from the node
CMD_GET_NODE_INFO = ["ssh", getenv("DUSK_SSH_HOSTNAME", "dusk"), "source .profile ; get_node_info"]
