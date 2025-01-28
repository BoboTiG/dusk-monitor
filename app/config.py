"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app import constants


def sanitize(value: str, *, pattern: re.Pattern[str] = re.compile(r"[^a-zAZ0-9\.\-_]+")) -> str:
    """Regexp used to clean-up the SSH hostname."""
    return pattern.sub("", value)


@dataclass(slots=True, frozen=True)
class Defaults:
    # Local web server
    host = "0.0.0.0"
    port = sum(ord(c) for c in "Dusk Node Monitoring")  # Hint: one-thousand-twenty-three
    # Play a sound on new block generated
    play_sound = True
    # SSH hostname to contact the node
    ssh_hostname = "dusk"


HOST = Defaults.host
PORT = Defaults.port
PLAY_SOUND = Defaults.play_sound
SSH_HOSTNAME = Defaults.ssh_hostname
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

    global HOST, PORT, PLAY_SOUND, PROVISIONER, SSH_HOSTNAME

    HOST = data.get("host", Defaults.host)
    PORT = int(data.get("port", Defaults.port))
    PLAY_SOUND = bool(data.get("play-sound", Defaults.play_sound))
    PROVISIONER = data.get("provisioner", "")
    SSH_HOSTNAME = sanitize(data.get("ssh-hostname", Defaults.ssh_hostname))

    if verbose:
        if PROVISIONER:
            print(f">>> Using config provisioner (truncated): {PROVISIONER[:16]!r}")
        if HOST != Defaults.host:
            print(f">>> Using config host: {HOST!r}")
        if PORT != Defaults.port:
            print(f">>> Using config port: {PORT!r}")
        if PLAY_SOUND is not Defaults.play_sound:
            print(f">>> Using config play-sound: {PLAY_SOUND!r}")
        if SSH_HOSTNAME != Defaults.ssh_hostname:
            print(f">>> Using config ssh-hostname: {SSH_HOSTNAME!r}")

    return {
        "host": HOST,
        "port": PORT,
        "play-sound": PLAY_SOUND,
        "provisioner": PROVISIONER,
        "ssh-hostname": SSH_HOSTNAME,
    }


def save(form: dict) -> None:
    if len((provisioner := form["provisioner"].strip())) != constants.PROVISIONER_KEY_LENGTH:
        raise ValueError("the provisioner key length is incorrect.")

    new_data = {
        "host": form["host"],
        "port": int(form["port"]),
        "play-sound": "play-sound" in form,
        "provisioner": provisioner,
        "ssh-hostname": sanitize(form["ssh-hostname"]),
    }

    if new_data != load(verbose=False):
        constants.CONFIG_FILE.write_text(json.dumps(new_data, indent=4, sort_keys=True))
        load()


load()
