# 1.0.1

Release date: `2025-02-10`

## Features

- Enable back the light theme.
- Rewards charts are now compatible with dark themes.
- Add the changelog.

# 1.0.0

Release date: `2025-02-05`

## Bug Fixes

- Use a locking mechanism when running `--update` in order to prevent concurrent runs.
- Keep only one light theme, and it is disabled for now.

## Features

- Display rewards, and public history, on the dashboard.
- Add rewards charts (hourly, daily, monthly, and yearly).
- Introduce the setup page to define the provisioner public key, and other parameters.

## Technical Changes

- `--update` now retreives the public history too.
- The `<DATA_DIR>/db.json` file contains more details: rewards, last block, slashes (soft, and hard), and public history.
- Keep rewards in the `<DATA_DIR>/rewards.txt` file. It is updated at each call to `--update`.
- Remove the need for SSH, making the project really safe by not touching the node at all.
- Remove the `<DATA_DIR>/provisioner.txt` file: now using a `<DATA_DIR>/config.json` file to store this information in addition to other parameters.
- Remove the `listen.py` file, no more needed.
- Remove the `websockets` module requirement.
- Replace the `niquests` module for `requests`.

# 0.1.0

Release date: `2025-01-20`

## Features

- Public version.
- First commit from `2025-01-06`.
