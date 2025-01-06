"""
Simple tool to sync & display Dusk node metrics.
It is all about blocks, nothing more.
"""
import json
import pathlib
import re
import subprocess

import flask

PROVISIONER = ""
NODE_URL = "https://"
HEADERS = {"User-Agent": "https://github.com/BoboTiG/dusk-monitor"}
DB_FILE = pathlib.Path(__file__).parent / "db.json"
PORT = sum(ord(c) for c in "Dusk Node Monitoring")  # Hint: one-thousand-twenty-three
CMD = ["ssh", "-t", "dusk", "source .profile ; blocks"]
CMD_GENERATED = ["ssh", "-t", "dusk", "source .profile ; list_rejected_blocks"]

Database = dict[str, set[int]]

app = flask.Flask(__name__)


@app.route("/")
def index() -> flask.Response:
    data = db_load()
    accepted = len(data["accepted"])
    generated = len(data["generated"]) + accepted
    output = subprocess.check_output(CMD, text=True)
    current, latest, *_ = [int(value) for value in re.findall(r"m(\d+)", output)]
    reward = compute_rewards(data["accepted"])
    ratio = accepted * 100 / (generated or 1)
    html = f"""<html>
<head>
    <meta content="width=device-width,initial-scale=1.0" name="viewport">
    <link rel="shortcut icon" href="/static/favicon.svg">
    <link rel="stylesheet" href="/static/style.css"/>
    <title>Dusk Node Monitoring</title>
</head>
<body>
    <button id="block-current" title="{current:,}">{format_num(current)}</button>
    <button id="block-latest" title="{latest:,}">{format_num(latest)}</button>
    <button id="blocks-generated" title="{generated:,}">{format_num(generated)}</button>
    <button id="blocks-accepted" title="{accepted:,}">
        <div>{format_num(accepted)}</div>
        <span title="Ratio blocks accepted / blocks generated">{ratio:0,.02f}%</span>
        <span>|</span>
        <span title="{reward:0,.02f}">{format_num(reward)}$</span>
    </button>
    <!-- First version: 2025-01-06 ! -->
</body>
</html>"""
    return flask.Response(html, mimetype="text/html")


def compute_rewards(blocks: set[int]) -> float:
    """
    Block generators get 80% + voting fractions (not computed here).
    Source: https://github.com/dusk-network/audits/blob/main/core-audits/2024-09_economic-protocol-design_pol-finance.pdf
    Source: https://github.com/dusk-network/rusk/blob/rusk-1.0.0/rusk/src/lib/node.rs#L132-L157
    
    >>> compute_rewards({0})  # Genesis
    0.0
    >>> compute_rewards({1 + 1})  # Period 1
    15.885919999999999
    >>> compute_rewards({12_614_401 + 1})  # Period 2
    7.942959999999999
    >>> compute_rewards({25_228_801 + 1})  # Period 3
    3.9714799999999997
    >>> compute_rewards({37_843_201 + 1})  # Period 4
    1.9857440000000002
    >>> compute_rewards({50_457_601 + 1})  # Period 5
    0.9928720000000001
    >>> compute_rewards({63_072_001 + 1})  # Period 6
    0.496432
    >>> compute_rewards({75_686_401 + 1})  # Period 7
    0.248216
    >>> compute_rewards({88_300_801 + 1})  # Period 8
    0.124112
    >>> compute_rewards({100_915_201 + 1})  # Period 9
    0.062056
    >>> compute_rewards({113_529_597})  # Last mint
    0.043424000000000004

    >>> compute_rewards({10, 10_000_000, 50_000_000, 100_000_000})
    33.881696
    """
    amount = 0.0
    for block in blocks:
        if block == 113_529_597:  # Last mint
            dusk = 0.05428
        elif block >= 100_915_201:  # Period 9
            dusk = 0.07757
        elif block >= 88_300_801:  # Period 8
            dusk = 0.15514
        elif block >= 75_686_401:  # Period 7
            dusk = 0.31027
        elif block >= 63_072_001:  # Period 6
            dusk = 0.62054
        elif block >= 50_457_601:  # Period 5
            dusk = 1.24109
        elif block >= 37_843_201:  # Period 4
            dusk = 2.48218
        elif block >= 25_228_801:  # Period 3
            dusk = 4.96435
        elif block >= 12_614_401:  # Period 2
            dusk = 9.9287
        elif block >= 1:  # Period 1
            dusk = 19.8574
        else:  # Genesis
            dusk = 0.0
        amount += dusk * 0.8
    return amount


def db_load() -> Database:
    global PROVISIONER

    data = json.loads(DB_FILE.read_text())
    PROVISIONER = data["provisioner"]
    return {
        "generated": set(data.get("generated", [])),
        "accepted": set(data.get("accepted", [])),
    }


def db_save(data: Database) -> None:
    DB_FILE.write_text(json.dumps(data, sort_keys=True))


def format_num(value: int) -> str:
    if value < 1000:
        if isinstance(value, float):
            return f"{value:0.02f}"
        return f"{value:,}"

    for unit in ("", "K", "m"):
        if value < 1000:
            return f"{value:3.3f}{unit}"
        value /= 1000

    return f"{value:3,.3f}M"


def get_accepted() -> set[int]:
    import niquests

    # FIXME: Find a more efficient query, like passing `generatorBlsPubkey == "PROVISIONER"` as a condition directly.
    query = {
        "topic": "gql",
        "data": "fragment BlockInfo on Block { header { height, generatorBlsPubkey } } query() { blocks(last: 10000) {...BlockInfo} }",  # noqa: E501
    }
    with niquests.post(NODE_URL, headers=HEADERS, json=query) as req:
        return {
            block["header"]["height"]
            for block in req.json()
            if block["header"]["generatorBlsPubkey"] == PROVISIONER
        }


def get_generated() -> set[int]:
    output = subprocess.check_output(CMD_GENERATED, text=True)
    return {int(block) for block in output.strip().split()}


def update() -> None:
    new_generated = get_generated()
    new_accepted = get_accepted()
    if not new_generated and not new_accepted:
        return

    data = db_load()
    data["generated"] |= new_generated
    data["accepted"] |= new_accepted
    db_save(data)


if __name__ == "__main__":
    import sys

    if "--update" in sys.argv:
        update()
    else:
        app.run(port=PORT, host="0.0.0.0", debug=True)
