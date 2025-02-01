"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from __future__ import annotations

import itertools
from datetime import datetime
from subprocess import check_output
from time import monotonic
from typing import TYPE_CHECKING, Any

import flask

from app import config, constants, db

if TYPE_CHECKING:
    from werkzeug.wrappers.response import Response

app = flask.Flask(__name__)


@app.route("/")
def index() -> str | Response:
    if not config.PROVISIONER:
        return flask.redirect("/setup")

    start = monotonic()
    data = db.load()
    history = craft_history(data)
    longest = len(max(history, key=lambda v: len(v[1]))[1]) if history else 0
    total_rewards = data.rewards + sum(amount for fn_name, amount, _ in data.history.values() if fn_name == "withdraw")
    served_time = monotonic() - start

    # Note: as of 2025-01-31, served_time = 0.001 sec (rounded in the template).

    return render(
        "dashboard",
        data=data,
        history=history,
        longest=longest,
        served_time=served_time,
        total_rewards=total_rewards,
    )


@app.route("/setup", methods=["GET", "POST"])
def setup() -> str | Response:
    if flask.request.method == "GET":
        return render("setup", config=config, constants=constants)

    try:
        config.save(dict(flask.request.form))
    except Exception as exc:
        print(f"Error while handling form data: {exc}")
        return flask.redirect("/setup")

    return flask.redirect("/")


@app.template_filter()
def format_float(value: float) -> str:
    for unit in ("", "k"):
        if abs(value) < 1000.0:
            return f"{value:,.03f}{unit}"
        value /= 1000.0
    return f"{value:,.03f}M"


@app.template_filter()
def format_int(value: float) -> str:
    return f"{int(value):,}"


@app.template_filter()
def pad(value: str, width: int) -> str:
    return value.rjust(width, "\u00a0")


@app.template_filter()
def to_hour(value: str) -> str:
    return datetime.fromtimestamp(float(value)).strftime("%H:%M")


def craft_history(data: db.DataBase) -> list[tuple[str, str, str, str]]:
    if not config.REWARDS_HISTORY_HOURS:
        return []

    cmd = ["tail", f"-{config.REWARDS_HISTORY_HOURS * 12 + 2}", str(constants.REWARDS_FILE)]
    res: list[tuple[str, str, str, str]] = []

    # Rewards
    try:
        rewards_history = sorted(check_output(cmd, text=True).strip().splitlines(), reverse=True)
    except Exception:
        return []
    else:
        for line1, line2 in itertools.pairwise(rewards_history):
            when, rewards1 = line1.strip().split("|", 1)
            _, rewards2 = line2.strip().split("|", 1)
            if (diff := float(rewards1) - float(rewards2)) != 0.0:
                if diff:
                    res.append((when, f"+{format_float(diff)}", "go-up up", ""))
                else:
                    res.append((when, format_float(diff), "go-down down", ""))
            else:
                res.append((when, "±0.000", "go-nowhere empty", ""))

    # Actions
    first_date = res[-1][0] if res else "0"
    for when in data.history:
        if when < first_date:
            break

        fn_name, amount, _ = data.history[when]
        css_cls = "empty"

        if amount != 0:
            value = format_float(amount / 10**9)
            css_cls = "up" if amount > 0 else "down"
            if fn_name == "withdraw":
                value = f"+{value}"

        res.append((when, value, f"{fn_name} {css_cls}", fn_name.title()))

    return sorted(res, reverse=True)


def render(template: str, **kwargs: Any) -> str:
    return flask.render_template(f"{template}.html", **kwargs)
