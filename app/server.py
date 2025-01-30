"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from __future__ import annotations

import itertools
from datetime import datetime
from subprocess import check_output
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

    data = db.load()
    history = craft_history(data)
    return render(
        "dashboard",
        data=data,
        history=history,
        longest=len(max(history, key=lambda v: len(v[1]))[1]),
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


def craft_history(data: db.DataBase) -> list[tuple[str, str]]:
    res: list[tuple[str, str, str]] = []
    rewards_history = sorted(check_output(constants.CMD_GET_LAST_REWARDS, text=True).strip().splitlines(), reverse=True)

    # Rewards
    for line1, line2 in itertools.pairwise(rewards_history):
        when, rewards1 = line1.strip().split("|", 1)
        _, rewards2 = line2.strip().split("|", 1)
        if (diff := float(rewards1) - float(rewards2)) != 0.0:
            if diff:
                res.append((when, f"+{format_float(diff / 10**9)}", "go-up up"))
            else:
                res.append((when, format_float(diff / 10**9), "go-down down"))
        else:
            res.append((when, "±0.000", "go-nowhere empty"))

    # Actions
    first_date = res[-1][0]
    for when in reversed(data.history.keys()):
        if when < first_date:
            break

        fn_name, amount, _ = data.history[when]
        css_cls = "empty"

        if amount != 0:
            value = format_float(amount / 10**9)
            if fn_name != "convert":
                if amount > 0:
                    value = f"+{value}"
                    css_cls = "up"
                else:
                    css_cls = "down"

        res.append((when, value, f"{fn_name} {css_cls}"))

    return sorted(res, reverse=True)  # type: ignore[arg-type]


def render(template: str, **kwargs: Any) -> str:
    return flask.render_template(f"{template}.html", **kwargs)
