"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from subprocess import check_output

import flask

from app import constants, db

app = flask.Flask(__name__)


@app.route("/")
def index() -> flask.Response:
    data = db.load()
    rewards = data["rewards"]
    current_block, latest_block = get_block_heights()
    html = f"""<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="/static/favicon.svg">
    <link rel="stylesheet" href="/static/style.css"/>
    <meta content="width=device-width,initial-scale=1.0" name="viewport">
    <title>Dusk Node Monitoring</title>
</head>
<body>
    <button id="block-current">{current_block:,}</button>
    <button id="block-latest">{latest_block:,}</button>
    <button id="blocks-generated">{len(data['blocks']):,}</button>
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


def get_block_heights() -> tuple[int, int]:
    try:
        output = check_output(constants.CMD_GET_BLOCK_HEIGHTS, text=True)
        current_block, latest_block = [int(value) for value in output.strip().split()]
    except Exception as exc:
        print(f"Error in get_block_heights(): {exc}")
        current_block = latest_block = 0
    return current_block, latest_block
