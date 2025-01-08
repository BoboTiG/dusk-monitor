"""
This is part of the DnS Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

import asyncio


if __name__ == "__main__":
    import sys

    if "--listen" in sys.argv:
        from app import listen

        asyncio.run(listen.to_accepted_blocks())
    elif "--update" in sys.argv:
        from app import update

        update.update()
    else:
        from app import constants, server

        server.app.run(port=constants.PORT, host=constants.HOST, debug=constants.DEBUG)
