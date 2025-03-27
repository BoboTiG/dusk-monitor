# 1.1.2

Release date: `2025-03-25`

## Features

- Set a usefull title to history entries on the dashboard (when hovering with the cursor).

# 1.1.1

Release date: `2025-02-20`

## Bug Fixes

- History actions being skipped.

## Technical Changes

- Higher hourly diff threshold (`1.0` → `5.0`).

# 1.1.0

Release date: `2025-02-13`

## Bug Fixes

- Redirect `/rewards/` to `/rewards` instead of ending on a HTTP 404 error.
- Skip negative rewards amount in chart data: they are useful to track node efficiency, not to show the full history.

## Features

- Display an average line on charts, and use a two-colors scheme.
- Print soft/hard slashes when they occur.

## Technical Changes

- More efficient HTTP requests by using connections pooling. 

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
- First commit from `2025-01-05`.
