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
    total_rewards = data["total-rewards"]
    node = get_node_info()
    slashes = node.slash_soft + node.slash_hard
    sync_err = '⚠️ ' if node.blk_cur < (node.blk_lat - 1) else ""
    slash_err = '⚠️ ' if slashes else ""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <link rel="icon" href="/static/favicon.svg">
    <link rel="stylesheet" href="/static/style.css"/>
    <meta content="width=device-width,initial-scale=1.0" name="viewport">
    <title>Dusk Node Monitoring</title>
</head>
<body>
    <div id="block-height" tooltip data-tooltip="Latest: {node.blk_lat:,}"{' class="error"' if sync_err else ''}>{node.blk_cur:,}<span>｢{sync_err}current block｣</span></div>
    <div id="slashes" tooltip data-tooltip="Soft: {node.slash_soft} | Hard: {node.slash_hard}"{' class="error"' if slash_err else ''}>{slashes}<span>｢{slash_err}slashes｣</span></div>
    <div id="blocks-generated" tooltip data-tooltip="Latest: {max(data['blocks']):,}">{len(data['blocks']):,}<span>｢blocks generated｣</span></div>
    <div id="rewards" tooltip data-tooltip="Current: {rewards:0,.02f} | Total: {total_rewards:0,.02f}">{format_num(rewards)}<span>｢rewards｣</span></div>
    <!-- First version: 2025-01-06 -->
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
    blk_cur = blk_lat = slash_soft = slash_hard = 0
    try:
        output = check_output(constants.CMD_GET_NODE_INFO, text=True)
        blk_cur, blk_lat, slash_soft, slash_hard = [int(value) for value in output.strip().split()]
    except Exception as exc:
        print(f"Error in get_node_info(): {exc}")
    return NodeInfo(blk_cur, blk_lat, slash_soft, slash_hard)
