"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""
from subprocess import check_output

import flask

from app import constants, db, utils

app = flask.Flask(__name__)


@app.route("/")
def index() -> flask.Response:
    data = db.load()
    blocks_accepted = len(data["accepted"])
    blocks_generated = blocks_accepted + len(data["rejected"])
    reward = utils.compute_rewards(data["accepted"])
    ratio = blocks_accepted * 100 / (blocks_generated or 1)
    current_block, latest_block = get_block_heights()
    html = f"""<html>
<head>
    <link rel="shortcut icon" href="/static/favicon.svg">
    <link rel="stylesheet" href="/static/style.css"/>
    <meta content="width=device-width,initial-scale=1.0" name="viewport">
    <title>Dusk Node Monitoring</title>
</head>
<body>
    <button id="block-current">{current_block:,}</button>
    <button id="block-latest">{latest_block:,}</button>
    <button id="blocks-generated">{blocks_generated:,}</button>
    <button id="blocks-accepted">
        <div>{blocks_accepted:,}</div>
        <span title="Ratio blocks accepted / blocks generated is {ratio:0.02f}%">{int(ratio)}%</span>
        <span>|</span>
        <span title="{reward:0,.02f}">{utils.format_num(reward)} DUSK</span>
    </button>
    <!-- First version: 2025-01-06! -->
    <!-- Source: https://github.com/BoboTiG/dusk-monitor -->
</body>
</html>"""
    return flask.Response(html, mimetype="text/html")


def get_block_heights() -> tuple[int, int]:
    try:
        output = check_output(constants.CMD_GET_BLOCK_HEIGHTS, text=True)
        current_block, latest_block = [int(value) for value in output.strip().split()]
    except Exception as exc:
        print(f"Error in get_block_heights(): {exc}")
        current_block, latest_block = 0, 0
    return current_block, latest_block
