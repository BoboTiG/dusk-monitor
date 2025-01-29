"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from os import getenv
from pathlib import Path

# Debug mode
DEBUG = getenv("DEBUG", "1") != "0"

# Local files
ROOT = Path(__file__).parent
DATA_DIR = Path(getenv("DATA_DIR", ROOT.parent))
CONFIG_FILE = DATA_DIR / "config.json"
DB_FILE = DATA_DIR / "db.json"
REWARDS_FILE = DATA_DIR / "rewards.txt"

# Database
DB_VERSION = 4
DB_BLOCKS_PER_LINE = 50
DB_KEY_BLOCKS = "blocks"
DB_KEY_CURRENT_BLOCK = "current-block"
DB_KEY_CURRENT_REWARDS = "current-rewards"
DB_KEY_HISTORY = "history"
DB_KEY_LAST_BLOCK = "last-block"
DB_KEY_SLASH_HARD = "slash-hard"
DB_KEY_SLASH_SOFT = "slash-soft"
DB_KEY_TOTAL_REWARDS = "total-rewards"
DB_KEY_VERSION = "version"

# Remote data
HEADERS = {"User-Agent": "https://github.com/BoboTiG/dusk-monitor"}
URL_RUES_GQL = "https://nodes.dusk.network/on/graphql/query"
URL_RUES_PROVISIONERS = "https://nodes.dusk.network/on/node/provisioners"
GQL_GET_BLOCKS = """
fragment TransactionInfo on SpentTransaction { tx { json } }
fragment BlockInfo on Block { header { generatorBlsPubkey, height, timestamp }, transactions {...TransactionInfo} }
query() { blocks(range: [%d, %d]) {...BlockInfo} }
"""
GQL_GET_BLOCKS_ITEMS_COUNT = 10_000
GQL_LAST_BLOCK = "query { block(height: -1) { header { height } } }"
CONTRACT_TRANSFER = "0100000000000000000000000000000000000000000000000000000000000000"
CONTRACT_STAKING = "0200000000000000000000000000000000000000000000000000000000000000"

# Shell command to get data from the rewards history file (1 hour of data)
CMD_GET_LAST_REWARDS = ["tail", "-14", str(REWARDS_FILE)]

# Play a sound on new block generated (only when config.PLAY_SOUND is True)
AUDIO_FILE = ROOT / "static" / "mixkit-melodic-gold-price-2000.wav"
PLAY_SOUND_CMD = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(AUDIO_FILE)]

# Voter fraction rewards, in percent (estimation)
VOTER_FRACTION_PERCENT = 1.13

# Provisioner public key length
PROVISIONER_KEY_LENGTH = 131
