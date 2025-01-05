import pathlib
import re
import subprocess

import flask

PORT = sum(ord(c) for c in "Monitoring Node Dusk")  # 1923
CMD = ["ssh", "-t", "dusk", "source .profile ; blocks"]
app = flask.Flask(__name__)


@app.route("/")
def index() -> flask.Response:
    output = subprocess.check_output(CMD, text=True)
    values = [int(value) for value in re.findall(r"m(\d+)", output)]
    html = f"""
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
            display: flex;
            flex-flow: column wrap;
            justify-content: space-around;
        }}
        button {{
            flex: 1;
            border: 1px solid #111;
            text-align: center;
            font-size: 3em;
            font-family: "Monaspace Argon";
            text-shadow: 1px 1px 0 #222;
        }}
        button::after {{ display: block; font-size: .3em; opacity: .8 }}
        #a::after {{ content: "｢Current Block｣" }}
        #b::after {{ content: "｢Latest Block｣" }}
        #c::after {{ content: "｢Generated Blocks｣" }}
        #d::after {{ content: "｢Accepted Blocks｣" }}
    </style>
</head>
<body>
    <button id="a" style="background:#635985;color:#ccc" title="{values[0]}">{sizeof_fmt(values[0])}</button>
    <button id="b" style="background:#443c68;color:#bbb" title="{values[1]}">{sizeof_fmt(values[1])}</button>
    <button id="c" style="background:#393053;color:#aaa" title="{values[2]}">{sizeof_fmt(values[2])}</button>
    <button id="d" style="background:#18122b;color:#999" title="{values[3]}">{sizeof_fmt(values[3])}<br><span style="font-size:.5em">{values[3] / (values[2] or 1):0,.02f}%</span></button>
</body>
</html>
    """
    return flask.Response(html, mimetype="text/html")


def sizeof_fmt(value: int) -> str:
    for unit in ("", "K", "m", "M"):
        if abs(value) < 1000:
            if not unit:
                return f"{value:,}"
            return f"{value:3.3f}{unit}"
        value /= 1000


app.run(port=PORT, host="0.0.0.0", debug=True)
