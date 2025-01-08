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
# Number of last blocks to fetch for the query below
# Note 1: 360 blocks are expected each hour, so using 400 as a safe value.
# Note 2: 400 is useful only for hourly cron jobs, else a higher value is required.
# Note 3: When the query below will be optimized, those numbers might be obsolete though.
LAST_BLOCKS_COUNT = getenv("LAST_BLOCKS_COUNT", 400)
GENERATED_BLOCKS_GRAPHQL_QUERY = (
    # FIXME: Find a more efficient query, like passing `generatorBlsPubkey == "PROVISIONER"` as a condition directly.
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
