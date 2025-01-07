"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""
from pathlib import Path

PROVISIONER = ""
NODE_URL = "https://nodes.dusk.network/02/Chain"
HEADERS = {"User-Agent": "https://github.com/BoboTiG/dusk-monitor"}
DB_FILE = Path(__file__).parent.parent / "db.json"
PORT = sum(ord(c) for c in "Dusk Node Monitoring")  # Hint: one-thousand-twenty-three
CMD_SSH = ["ssh", "-t", "dusk"]
CMD_GET_BLOCK_HEIGHTS = [*CMD_SSH, "source .profile ; get_block_heights"]
CMD_LIST_REJECTED_BLOCKS = [*CMD_SSH, "source .profile ; list_rejected_blocks"]

Database = dict[str, set[int]]
