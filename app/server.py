"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

import math
from random import choice
from subprocess import check_output

import flask

from app import constants, db

app = flask.Flask(__name__)


@app.route("/")
def index() -> str:
    data = get_node_info()
    return flask.render_template(
        "dashboard.html",
        css=get_random_style(),
        data=data,
        estimated_rewards=data.total_rewards * constants.VOTER_FRACTION_PERCENT,
    )


@app.template_filter()
def format_float(value: float) -> str:
    for unit in ("", "k"):
        if value < 1000.0:
            return f"{value:.03f}{unit}"
        value /= 1000.0
    return f"{value:,.03f}M"


@app.template_filter()
def format_int(value: int | float) -> str:
    return f"{int(value):,}"


def get_node_info() -> db.DataBase:
    data = db.load()
    try:
        data.current_block = int(check_output(constants.CMD_GET_NODE_SYNCED_BLOCK, text=True).strip())
    except Exception as exc:
        if constants.DEBUG:
            print(f"Error in get_node_info(): {exc}")
    return data


def get_random_style() -> str:
    return choice(constants.CSS_FILES).name
