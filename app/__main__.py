"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

if __name__ == "__main__":
    import sys

    if "--update" in sys.argv:
        from app import update

        update.update()
    else:
        from app import constants, server

        server.app.run(port=constants.PORT, host=constants.HOST, debug=constants.DEBUG)
