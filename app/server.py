"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from subprocess import check_output
from typing import NamedTuple

import flask

from app import constants, db

app = flask.Flask(__name__)


class NodeInfo(NamedTuple):
    blk_max: int
    blk_cur: int
    blk_lat: int
    blk_tot: int
    slash_soft: int
    slash_hard: int
    rewards: float
    total_rewards: float


@app.route("/")
def index() -> flask.Response:
    node = get_node_info()
    slashes = node.slash_soft + node.slash_hard

    div = []
    if node.blk_cur < (node.blk_lat - 1):
        div.append(f'<div id="block-height" tooltip data-tooltip="Latest: {node.blk_lat:,}" class="error">{node.blk_cur:,}<span>｢⚠️ current block｣</span></div>')
    else:
        div.append(f'<div id="block-height">{node.blk_cur:,}<span>｢current block｣</span></div>')
    if slashes:
        div.append(f'<div id="slashes" tooltip data-tooltip="Soft: {node.slash_soft} | Hard: {node.slash_hard}" class="error">{slashes}<span>｢⚠️ slashes｣</span></div>')
    else:
        div.append(f'<div id="slashes">{slashes}<span>｢slashes｣</span></div>')
    div.append(f'<div id="blocks-generated" tooltip data-tooltip="Latest: {node.blk_max:,}">{node.blk_tot:,}<span>｢blocks generated｣</span></div>')
    div.append(f'<div id="rewards" tooltip data-tooltip="Current: {int(node.rewards):,} | Total: {int(node.total_rewards):,}">{format_num(node.rewards)}<span>｢rewards｣</span></div>')

    html = """<!DOCTYPE html>
<html>
<head>
    <link rel="icon" href="/static/favicon.svg">
    <link rel="stylesheet" href="/static/style.css"/>
    <meta content="width=device-width,initial-scale=1.0" name="viewport">
    <title>Dusk Node Monitoring</title>
</head>
<body>
    %s
    <!-- First version: 2025-01-06 -->
    <!-- Source: https://github.com/BoboTiG/dusk-monitor -->
</body>
</html>""" % "\n    ".join(div)
    return flask.Response(html, mimetype="text/html")


def format_num(value: float) -> str:
    for unit in ("", "k"):
        if value < 1000.0:
            return f"{value:.03f}{unit}"
        value /= 1000.0
    return f"{value:,.03f}M"


def get_node_info() -> NodeInfo:
    data = db.load()
    try:
        output = check_output(constants.CMD_GET_NODE_INFO, text=True)
        blk_cur, blk_lat, slash_soft, slash_hard = [int(value) for value in output.strip().split()]
    except Exception as exc:
        print(f"Error in get_node_info(): {exc}")
        blk_cur = blk_lat = slash_soft = slash_hard = 0

    return NodeInfo(
        max(data["blocks"]),
        blk_cur,
        blk_lat,
        len(data["blocks"]),
        slash_soft,
        slash_hard,
        data["rewards"],
        data["total-rewards"],
    )
