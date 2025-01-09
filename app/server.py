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
    blk_cur: int
    blk_lat: int
    slash_soft: int
    slash_hard: int


@app.route("/")
def index() -> flask.Response:
    data = db.load()
    rewards = data["rewards"]
    node = get_node_info()
    slashes = node.slash_soft + node.slash_hard
    sync_class = "error" if node.blk_cur < (node.blk_lat - 1) else ""
    slash_class = "error" if slashes else ""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <link rel="icon" href="/static/favicon.svg">
    <link rel="stylesheet" href="/static/style.css"/>
    <meta content="width=device-width,initial-scale=1.0" name="viewport">
    <title>Dusk Node Monitoring</title>
</head>
<body>
    <button id="block-height" class="{sync_class}" title="Current: {node.blk_cur:,} | Latest: {node.blk_lat:,}">{node.blk_cur:,}</button>
    <button id="slashes" class="{slash_class}" title="Soft: {node.slash_soft} | Hard: {node.slash_hard}">{slashes}</button>
    <button id="blocks-generated" title="Latest: {max(data['blocks']):,}">{len(data['blocks']):,}</button>
    <button id="rewards" title="{rewards:0,.02f}">{format_num(rewards)}</button>
    <!-- First version: 2025-01-06! -->
    <!-- Source: https://github.com/BoboTiG/dusk-monitor -->
</body>
</html>"""
    return flask.Response(html, mimetype="text/html")


def format_num(value: float) -> str:
    for unit in ("", "k"):
        if value < 1000.0:
            return f"{value:.03f}{unit}"
        value /= 1000.0
    return f"{value:,.03f}M"


def get_node_info() -> NodeInfo:
    current_block = latest_block = soft_slashes = hard_slashes = 0
    try:
        output = check_output(constants.CMD_GET_NODE_INFO, text=True)
        current_block, latest_block, soft_slashes, hard_slashes = [int(value) for value in output.strip().split()]
    except Exception as exc:
        print(f"Error in get_node_info(): {exc}")
    return NodeInfo(current_block, latest_block, soft_slashes, hard_slashes)
