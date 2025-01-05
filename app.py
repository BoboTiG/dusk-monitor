import pathlib
import re
import subprocess

import flask

PORT = sum(ord(c) for c in "Dusk Node Monitoring")  # 1923
CMD = ["ssh", "-t", "dusk", "source .profile ; blocks"]
app = flask.Flask(__name__)


@app.route("/")
def index() -> flask.Response:
    output = subprocess.check_output(CMD, text=True)
    values = [int(value) for value in re.findall(r"m(\d+)", output)]
    reward = block_reward(values[3])
    html = f"""\
<html>
<head>
    <meta content="width=device-width,initial-scale=1.0" name="viewport">
    <link rel="shortcut icon" href="/static/favicon.svg">
    <title>Dusk Node Monitoring</title>
    <style>
        @font-face {{
            /* https://github.com/githubnext/monaspace/blob/v1.000/fonts/webfonts/MonaspaceArgonVarVF%5Bwght%2Cwdth%2Cslnt%5D.woff2 */
            font-family: "Monaspace Argon";
            src:
                local("Monaspace Argon Regular"),
                url("/static/monaspace-argon.woff2") format("woff2");
        }}
        body {{
            height: 100%;
            padding: 0;
            margin: 0;
            background-color: #000;
            display: flex;
            flex-flow: column wrap;
            justify-content: space-around;
        }}
        button {{
            flex: 1;
            border: 1px solid #111;
            border-radius: .1em / 1em;
            text-align: center;
            font-size: 3em;
            font-family: "Monaspace Argon";
            color: #ddd;
            text-shadow: 1px 1px 0 #222;
        }}
        button::after {{
            display: block;
            font-size: .3em;
            color: moccasin;
        }}
        #a::after {{ content: "｢Current Block｣" }}
        #b::after {{ content: "｢Latest Block｣" }}
        #c::after {{ content: "｢Generated Blocks｣" }}
        #d::after {{ content: "｢Accepted Blocks｣" }}
    </style>
</head>
<body>
    <button id="a" style="background:#635985" title="{values[0]:,}">{sizeof_fmt(values[0])}</button>
    <button id="b" style="background:#443c68" title="{values[1]:,}">{sizeof_fmt(values[1])}</button>
    <button id="c" style="background:#393053" title="{values[2]:,}">{sizeof_fmt(values[2])}</button>
    <button id="d" style="background:#18122b" title="{values[3]:,}">
        {sizeof_fmt(values[3])}
        <br>
        <span style="font-size:.5em" title="Ratio blocks accepted / blocks generated">{values[3] * 100 / (values[2] or 1):0,.02f}%</span>
        <span style="font-size:.5em">|</span>
        <span style="font-size:.5em" title="{reward:0,.02f}">{sizeof_fmt(reward)}$</span>
    </button>
    <!-- 2025-01-06 -->
</body>
</html>"""
    return flask.Response(html, mimetype="text/html")


def block_reward(count: int, *, reward: float = 19.8574) -> int:
    """
    As of 2025-01-06:
        - There is a 19.8574 block reward.
        - Deducting 10% for the team rewards.
        - Block generator gets 80% + voting fractions (not computed here).
    Source: https://github.com/dusk-network/audits/blob/main/core-audits/2024-09_economic-protocol-design_pol-finance.pdf
    """
    return count * (reward * 0.9 * 0.8)


def sizeof_fmt(value: int) -> str:
    if value < 1000:
        if isinstance(value, float):
            return f"{value:0.02f}"
        return f"{value:,}"

    for unit in ("", "K", "m"):
        if value < 1000:
            return f"{value:3.3f}{unit}"
        value /= 1000

    return f"{value:3,.3f}M"


app.run(port=PORT, host="0.0.0.0", debug=True)
