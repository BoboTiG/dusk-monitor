"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from os import getenv
from pathlib import Path

# Local files
ROOT = Path(__file__).parent
STATIC = ROOT / "static"
DB_FILE = ROOT.parent / "db.json"
PROVISIONER = (ROOT.parent / "provisioner.txt").read_text().strip()

# Mainnet URL
NODE_HOSTNAME = "nodes.dusk.network"
HEADERS = {"User-Agent": "https://github.com/BoboTiG/dusk-monitor"}
LAST_BLOCKS_COUNT = getenv("LAST_BLOCKS_COUNT", 10000)
GENERATED_BLOCKS_GRAPHQL_QUERY = "fragment BlockInfo on Block { header { height, generatorBlsPubkey } } query() { blocks(last: %s) {...BlockInfo} }" % LAST_BLOCKS_COUNT

# Local web server
HOST = "0.0.0.0"
PORT = sum(ord(c) for c in "Dusk Node Monitoring")  # Hint: one-thousand-twenty-three
DEBUG = True
CSS_FILES = list(STATIC.glob("light-*.css"))

# SSH command to get data from the node
CMD_GET_NODE_INFO = ["ssh", getenv("DUSK_SSH_HOSTNAME", "dusk"), "source .profile ; get_node_info"]

# Bonus: play a sound on new block generated (only when PLAY_SOUND is True)
PLAY_SOUND = getenv("PLAY_SOUND", "1") != "0"
AUDIO_FILE = STATIC / "mixkit-melodic-gold-price-2000.wav"
PLAY_SOUND_CMD = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", AUDIO_FILE]

# Voter fraction rewards, in percent (estimation)
VOTER_FRACTION_PERCENT = 1.125

# Used to check when the connection is back again in `--listen` (https://www.fdn.fr/actions/dns/)
NET_CHECK_IP = "80.67.169.12"
NET_CHECK_PORT = 53
NET_CHECK_INTVL = 5
