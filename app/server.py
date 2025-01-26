"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from datetime import UTC, datetime
from random import choice

import flask

from app import constants, db

app = flask.Flask(__name__)


@app.route("/")
def index() -> str:
    data = db.load()
    history = craft_history(data)
    return render(
        "dashboard",
        data=data,
        estimated_rewards=data.total_rewards * constants.VOTER_FRACTION_PERCENT,
        history=history,
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


def craft_history(data: db.DataBase) -> list[tuple[str, str]]:
    def to_date(value: str) -> datetime:
        return datetime.fromtimestamp(float(value), tz=UTC)

    actions_history = data.history
    rewards_history = constants.REWARDS_FILE.read_text().splitlines()[-20:]  # Last 20 records

    res: list[tuple[datetime, str, str]] = [
        (to_date(when), details[0], details[0]) for when, details in actions_history.items()
    ]

    for line1, line2 in zip(rewards_history, rewards_history[1:], strict=False):
        when, rewards1 = line1.strip().split("|", 1)
        _, rewards2 = line2.strip().split("|", 1)
        if diff := float(rewards2) - float(rewards1):
            res.append((to_date(when), format_float(diff), "go-up" if diff > 0.0 else "go-down"))

    res = sorted(res)[-12:]  # Last 12 items (1 hour of data)
    return sorted(res, reverse=True)  # type: ignore[arg-type]


def get_random_style() -> str:
    return choice(constants.CSS_FILES).name


def render(template: str, **kwargs) -> str:
    return flask.render_template(f"{template}.html", css=get_random_style(), **kwargs)
