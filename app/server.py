"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from datetime import datetime
from random import choice
from subprocess import check_output

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


@app.template_filter()
def to_hour(value: str) -> str:
    return datetime.fromtimestamp(float(value)).strftime("%H:%M")


def craft_history(data: db.DataBase) -> list[tuple[str, str]]:
    res: list[tuple[str, str, str]] = []
    rewards_history = check_output(constants.CMD_GET_LAST_REWARDS, text=True).strip().splitlines()

    # Rewards
    for line1, line2 in zip(rewards_history, rewards_history[1:], strict=False):
        when, rewards1 = line1.strip().split("|", 1)
        _, rewards2 = line2.strip().split("|", 1)
        if (diff := float(rewards2) - float(rewards1)) != 0.0:
            if diff:
                res.append((when, f"+{format_float(diff)}", "go-up"))
            else:
                res.append((when, format_float(diff), "go-down"))
        else:
            res.append((when, "∓0.000", "go-nowhere"))

    # Actions (stake/unstake/withdraw)
    first_date = res[0][0]
    for when, details in data.history.items():
        if when >= first_date:
            res.append((when, details[0].title(), details[0]))

    res = sorted(res)[-12:]  # Last 12 items (1 hour of data)
    return sorted(res, reverse=True)  # type: ignore[arg-type]


def get_random_style() -> str:
    return choice(constants.CSS_FILES).name


def render(template: str, **kwargs) -> str:
    return flask.render_template(f"{template}.html", css=get_random_style(), **kwargs)
