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
def index() -> flask.Response:
    data = get_node_info()
    slashes = data.slash_soft + data.slash_hard

    div = []

    if data.current_block < (data.last_block - 1):
        div.append(
            f'<div id="block-height" tooltip data-tooltip="Latest: {data.last_block:,}" class="error">{data.current_block:,}<span>｢⚠️ current block｣</span></div>'
        )  # noqa: E501
    else:
        div.append(f'<div id="block-height">{data.current_block:,}<span>｢current block｣</span></div>')

    if slashes:
        div.append(
            f'<div id="slashes" tooltip data-tooltip="Soft: {data.slash_soft} | Hard: {data.slash_hard}" class="error">{slashes}<span>｢⚠️ slashes｣</span></div>'
        )  # noqa: E501
    else:
        div.append(f'<div id="slashes">{slashes}<span>｢slashes｣</span></div>')

    div.append(
        f'<div id="blocks-generated" tooltip data-tooltip="Latest: {max(data.blocks):,}">{len(data.blocks):,}<span>｢blocks generated｣</span></div>'
    )  # noqa: E501
    div.append(
        f'<div id="rewards" tooltip data-tooltip="Current: {math.ceil(data.rewards):,} | Total: {math.ceil(data.total_rewards * constants.VOTER_FRACTION_PERCENT):,}">{format_num(data.rewards)}<span>｢rewards｣</span></div>'
    )  # noqa: E501

    html = """<!DOCTYPE html>
<html>
<head>
    <link rel="icon" href="/static/favicon.svg">
    <link rel="stylesheet" href="/static/style.css"/>
    <link rel="stylesheet" href="/static/%s"/>
    <meta content="width=device-width,initial-scale=1.0" name="viewport">
    <title>Dusk Node Monitoring</title>
</head>
<body>
    %s
    <!-- First version: 2025-01-06 -->
    <!-- Source: https://github.com/BoboTiG/dusk-monitor -->
    <!-- Dusk wallet for tips: VKZpBrNtEeTobMgYkkdcGiZn8fK2Ve2yez429yRXrH4nUUDTuvr7Tv74xFA2DKNVegtF6jaom2uacZMm8Z2Lg2J -->
</body>
</html>""" % (get_random_style(), "\n    ".join(div))
    return flask.Response(html, mimetype="text/html")


def format_num(value: float) -> str:
    for unit in ("", "k"):
        if value < 1000.0:
            return f"{value:.03f}{unit}"
        value /= 1000.0
    return f"{value:,.03f}M"


def get_node_info() -> db.DataBase:
    data = db.load()
    try:
        data.current_block = int(check_output(constants.CMD_GET_NODE_SYNCED_BLOCK, text=True).strip())
    except Exception as exc:
        print(f"Error in get_node_info(): {exc}")
    return data


def get_random_style() -> str:
    return choice(constants.CSS_FILES).name
