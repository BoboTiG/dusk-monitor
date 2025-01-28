"""
This is part of the Dusk node Monitoring.
Source: https://github.com/BoboTiG/dusk-monitor
"""

from pathlib import Path


LOCK_FILE = Path("/tmp/dusk-monitor.lock")


if __name__ == "__main__":
    import sys

    if "--update" in sys.argv:
        if not LOCK_FILE.is_file():
            LOCK_FILE.write_text("Hello, there!")
            try:
                from app import update

                update.update()
            finally:
                LOCK_FILE.unlink()
    else:
        from app import config, constants, server

        server.app.run(port=config.PORT, host=config.HOST, debug=constants.DEBUG)
