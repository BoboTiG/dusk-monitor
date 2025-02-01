"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from app import constants


@dataclass(slots=True, frozen=True)
class Defaults:
    # Local web server
    host = "0.0.0.0"
    port = sum(ord(c) for c in "Dusk Node Monitoring")  # Hint: one-thousand-twenty-three
    # Hours of rewards history data to display (min: 0 [disabled], max: 24)
    rewards_history_hours = 3
    # Play a sound on new block generated
    play_sound = True


HOST = Defaults.host
PORT = Defaults.port
PLAY_SOUND = Defaults.play_sound
REWARDS_HISTORY_HOURS = Defaults.rewards_history_hours
PROVISIONER = ""  # Provisioner public key


def load(*, verbose: bool = True) -> dict[str, bool | int | str]:
    data = {}
    try:
        data = json.loads(constants.CONFIG_FILE.read_text())
    except FileNotFoundError:
        print(">>> Config file not found, go to the dashboard /setup page.")
        return data
    except Exception as exc:
        print(f">>> Config file error, go to the dashboard /setup page, or fix it: {exc}")
        return data

    global HOST, PORT, PLAY_SOUND, PROVISIONER, REWARDS_HISTORY_HOURS

    HOST = data.get("host", Defaults.host)
    PORT = int(data.get("port", Defaults.port))
    PLAY_SOUND = bool(data.get("play-sound", Defaults.play_sound))
    PROVISIONER = data.get("provisioner", "")
    REWARDS_HISTORY_HOURS = min(max(0, int(data.get("rewards-history-hours", Defaults.rewards_history_hours))), 24)

    if verbose and constants.DEBUG:
        if PROVISIONER:
            print(f">>> Using config provisioner (truncated): {PROVISIONER[:16]!r}")
        if Defaults.host != HOST:
            print(f">>> Using config host: {HOST!r}")
        if Defaults.port != PORT:
            print(f">>> Using config port: {PORT!r}")
        if PLAY_SOUND is not Defaults.play_sound:
            print(f">>> Using config play-sound: {PLAY_SOUND!r}")
        if Defaults.rewards_history_hours != REWARDS_HISTORY_HOURS:
            print(f">>> Using config rewards-history-hours: {REWARDS_HISTORY_HOURS!r}")

    return {
        "host": HOST,
        "port": PORT,
        "play-sound": PLAY_SOUND,
        "provisioner": PROVISIONER,
        "rewards-history-hours": REWARDS_HISTORY_HOURS,
    }


def save(form: dict) -> None:
    if len(provisioner := form["provisioner"].strip()) != constants.PROVISIONER_KEY_LENGTH:
        msg = "the provisioner key length is incorrect."
        raise ValueError(msg)

    new_data = {
        "host": form["host"],
        "port": int(form["port"]),
        "play-sound": "play-sound" in form,
        "provisioner": provisioner,
        "rewards-history-hours": min(max(0, int(form["rewards-history-hours"])), 24),
    }

    if new_data != load(verbose=False):
        constants.CONFIG_FILE.write_text(json.dumps(new_data, indent=4, sort_keys=True))
        load()


load()
