"""
This is part of the Dusk Node Monitoring project.
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
    # Play a sound on new block generated
    play_sound = True
    # Hours of rewards history data to display (min: 0 [disabled], max: 24)
    rewards_history_hours = 3


HOST, PORT = Defaults.host, Defaults.port
PLAY_SOUND = Defaults.play_sound
PROVISIONER = ""  # Provisioner public key
REWARDS_HISTORY_HOURS = Defaults.rewards_history_hours


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

    HOST = data.get(constants.CONF_KEY_HOST, Defaults.host)
    PORT = int(data.get(constants.CONF_KEY_PORT, Defaults.port))
    PLAY_SOUND = bool(data.get(constants.CONF_KEY_PLAY_SOUND, Defaults.play_sound))
    PROVISIONER = data.get(constants.CONF_KEY_PROVISIONER, "")
    REWARDS_HISTORY_HOURS = min(
        max(0, int(data.get(constants.CONF_KEY_REWARDS_HISTORY_HOURS, Defaults.rewards_history_hours))),
        24,
    )

    if verbose and constants.DEBUG:
        if PROVISIONER:
            print(f">>> Using config {constants.CONF_KEY_PROVISIONER} (truncated): {PROVISIONER[:16]!r}")
        if Defaults.host != HOST:
            print(f">>> Using config {constants.CONF_KEY_HOST}: {HOST!r}")
        if Defaults.port != PORT:
            print(f">>> Using config {constants.CONF_KEY_PORT}: {PORT!r}")
        if Defaults.play_sound is not PLAY_SOUND:
            print(f">>> Using config {constants.CONF_KEY_PLAY_SOUND}: {PLAY_SOUND!r}")
        if Defaults.rewards_history_hours != REWARDS_HISTORY_HOURS:
            print(f">>> Using config {constants.CONF_KEY_REWARDS_HISTORY_HOURS}: {REWARDS_HISTORY_HOURS!r}")

    return {
        constants.CONF_KEY_HOST: HOST,
        constants.CONF_KEY_PORT: PORT,
        constants.CONF_KEY_PLAY_SOUND: PLAY_SOUND,
        constants.CONF_KEY_PROVISIONER: PROVISIONER,
        constants.CONF_KEY_REWARDS_HISTORY_HOURS: REWARDS_HISTORY_HOURS,
    }


def save(form: dict) -> None:
    if len(provisioner := form[constants.CONF_KEY_PROVISIONER].strip()) != constants.PROVISIONER_KEY_LENGTH:
        provisioner = ""

    new_data = {
        constants.CONF_KEY_HOST: form[constants.CONF_KEY_HOST],
        constants.CONF_KEY_PORT: int(form[constants.CONF_KEY_PORT]),
        constants.CONF_KEY_PLAY_SOUND: constants.CONF_KEY_PLAY_SOUND in form,
        constants.CONF_KEY_PROVISIONER: provisioner,
        constants.CONF_KEY_REWARDS_HISTORY_HOURS: min(max(0, int(form[constants.CONF_KEY_REWARDS_HISTORY_HOURS])), 24),
    }

    if new_data != load(verbose=False):
        constants.CONFIG_FILE.write_text(json.dumps(new_data, indent=4, sort_keys=True))
        load()

    if not provisioner:
        msg = "the provisioner key length is incorrect."
        raise ValueError(msg)


load()
