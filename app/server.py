"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""
from subprocess import check_output

import flask

import app.constants as constants
import app.db as db
import app.utils as utils

app = flask.Flask(__name__)


@app.route("/")
def index() -> flask.Response:
    data = db.load()
    blocks_accepted = len(data["accepted"])
    blocks_generated = blocks_accepted + len(data["rejected"])
    output = check_output(constants.CMD_GET_BLOCK_HEIGHTS, text=True)
    current_block, latest_block = [int(value) for value in output.strip().split()]
    reward = utils.compute_rewards(data["accepted"])
    ratio = blocks_accepted * 100 / (blocks_generated or 1)
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
        <span title="Ratio blocks accepted / blocks generated is {ratio:0.02f}">{int(ratio)}%</span>
        <span>|</span>
        <span title="{reward:0,.02f}">{utils.format_num(reward)} DUSK</span>
    </button>
    <!-- First version: 2025-01-06! -->
</body>
</html>"""
    return flask.Response(html, mimetype="text/html")
