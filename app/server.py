"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from random import choice

import flask

from app import constants, db

app = flask.Flask(__name__)


@app.route("/")
def index() -> str:
    data = db.load()
    return flask.render_template(
        "dashboard.html",
        css=get_random_style(),
        data=data,
        estimated_rewards=data.total_rewards * constants.VOTER_FRACTION_PERCENT,
    )


@app.template_filter()
def format_float(value: float) -> str:
    for unit in ("", "k"):
        if abs(value) < 1000.0:
            return f"{value:,.03f}{unit}"
        value /= 1000.0
    return f"{value:,.03f}M"


@app.template_filter()
def format_int(value: int | float) -> str:
    return f"{int(value):,}"


def get_random_style() -> str:
    return choice(constants.CSS_FILES).name
