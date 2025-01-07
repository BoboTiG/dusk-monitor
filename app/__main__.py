"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

if __name__ == "__main__":
    import sys

    if "--update" in sys.argv:
        import app.update as update

        update.update()
    else:
        import app.constants as constants
        import app.server as server

        server.app.run(port=constants.PORT, host="0.0.0.0", debug=True)
