"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from os import getenv
from pathlib import Path

# Local files
ROOT = Path(__file__).parent
STATIC = ROOT / "static"
DATA_DIR = Path(getenv("DATA_DIR", ROOT.parent))
DB_FILE = DATA_DIR / "db.json"
PROVISIONER = (DATA_DIR / "provisioner.txt").read_text().strip()

# Database
DB_BLOCKS_PER_LINE = 50
DB_KEY_BLOCKS = "blocks"
DB_KEY_CURRENT_BLOCK = "current-block"
DB_KEY_LAST_BLOCK = "last-block"
DB_KEY_REWARDS = "rewards"
DB_KEY_SLASH_HARD = "slash-hard"
DB_KEY_SLASH_SOFT = "slash-soft"
DB_KEY_TOTAL_REWARDS = "total-rewards"

# Mainnet URL
NODE_HOSTNAME = "nodes.dusk.network"
HEADERS = {"User-Agent": "https://github.com/BoboTiG/dusk-monitor"}
GQL_GENERATED_BLOCKS = "fragment BlockInfo on Block { header { height, generatorBlsPubkey } } query() { blocks(range: [%d, %d]) {...BlockInfo} }"
GQL_GENERATED_BLOCKS_ITEMS_COUNT = 10_000
GQL_LAST_BLOCK = "query { block(height: -1) { header { height } } }"

# Local web server
HOST = getenv("HOST", "0.0.0.0")
PORT = int(getenv("PORT", sum(ord(c) for c in "Dusk Node Monitoring")))  # Hint: one-thousand-twenty-three
DEBUG = getenv("DEBUG", "1") != "0"
CSS_FILES = list(STATIC.glob("light-*.css"))

# SSH command to get data from the node
CMD_GET_NODE_SYNCED_BLOCK = ["ssh", getenv("DUSK_SSH_HOSTNAME", "dusk"), "ruskquery block-height"]

# Bonus: play a sound on new block generated (only when PLAY_SOUND is True)
PLAY_SOUND = getenv("PLAY_SOUND", "1") != "0"
AUDIO_FILE = STATIC / "mixkit-melodic-gold-price-2000.wav"
PLAY_SOUND_CMD = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(AUDIO_FILE)]

# Voter fraction rewards, in percent (estimation)
VOTER_FRACTION_PERCENT = 1.13
