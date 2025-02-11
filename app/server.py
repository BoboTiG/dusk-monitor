"""
This is part of the Dusk Node Monitoring project.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from __future__ import annotations

import itertools
from datetime import UTC, datetime
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


@app.route("/rewards")
@app.route("/rewards/")
def rewards() -> Response:
    return flask.redirect("/rewards/day")


@app.route("/rewards/<interval>")
def rewards_interval(interval: str) -> str | Response:
    if interval not in {"hour", "day", "month", "year"}:
        print(f"Unknown {interval=}. Choices are: hour, day, month, or year.")
        return flask.redirect("/rewards")

    start = monotonic()
    data, average = generate_history_chart_data(interval)
    served_time = monotonic() - start

    return render(
        "rewards",
        average=average,
        data=data,
        interval=interval,
        served_time=served_time,
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
                if diff > 0.0:
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
            # Wallet actions, we do not really care about them
            if fn_name in {"convert", "transfer"}:
                css_cls = "up" if amount > 0 else "down"
            # Staking actions, we do care about them
            elif fn_name in {"stake", "withdraw"}:
                css_cls = "up"
            elif fn_name in {"unstake"}:
                css_cls = "down"
                value = f"-{value}"

        res.append((when, value, f"action {fn_name} {css_cls}", fn_name.title()))

    return sorted(res, reverse=True)


def generate_history_chart_data(interval: str) -> tuple[list[tuple[str, float]], float]:
    def to_chart_date(date: datetime) -> str:
        match interval:
            case "hour":
                return date.strftime("[%d/%m] %-Hh")
            case "day":
                return date.strftime("%Y-%m-%d")
            case "month":
                return date.strftime("%Y-%m")
        return date.strftime("%Y")

    rewards_history = constants.REWARDS_FILE.read_text().splitlines()
    data: list[tuple[str, float]] = []
    current_date = None
    current_rewards = 0.0

    for line1, line2 in itertools.pairwise(rewards_history):
        when, rewards1 = line1.strip().split("|", 1)
        _, rewards2 = line2.strip().split("|", 1)

        diff = float(rewards2) - float(rewards1)
        if interval == "hour" and diff > 1.0:
            continue

        if current_date is None:
            current_date = datetime.fromtimestamp(float(when), tz=UTC)
            current_rewards = diff
            continue

        this_date = datetime.fromtimestamp(float(when), tz=UTC)
        if getattr(this_date, interval) == getattr(current_date, interval):
            current_rewards += diff
            continue

        data.append((to_chart_date(current_date), current_rewards))
        current_date = this_date
        current_rewards = 0.0

    if current_rewards and current_date:
        data.append((to_chart_date(current_date), current_rewards))

    average = (
        # Skip first, and last, as they are likely incomplete
        sum(amount for _, amount in data[1:-1]) / (len(data) - 2)
        if interval in {"hour", "day"}
        else sum(amount for _, amount in data) / len(data)
    )

    return data, average


def render(template: str, **kwargs: Any) -> str:
    return flask.render_template(f"{template}.html", **kwargs)
