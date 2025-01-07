# Dusk Node Monitoring

Dumb'n simple tool to sync & display Dusk node metrics (see the [preview](#preview)).
It is all about blocks, nothing more.

## Install

```bash
python3 -m venv venv
. ./venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

## Setup

```bash
echo 'PROVISIONER_PUBLIC_KEY' > provisioner.txt
```

### Node

On the node, execute this script to append shell functions into the user profile file:

```bash
cat << 'EOF' >> ~/.profile

# Dusk Monitoring (https://github.com/BoboTiG/dusk-monitor)

function get_block_heights() {
    local current_block="$(ruskquery block-height)"
    local latest_block="$(API_ENDPOINT=https://nodes.dusk.network ruskquery block-height)"
    echo "${current_block} ${latest_block}"
}

function list_rejected_blocks() {
    zgrep 'Block generated' /var/log/rusk.log* \
        | awk '{print $3 $4}' \
        | sed 's/[[:cntrl:]]\[[[:digit:]][a-z]//g' \
        | grep -E 'iter=[^0]' | \
            while read -r line ; do \
                printf '%s ' "$(echo "${line}" | grep -Eo 'round=[[:digit:]]+' | cut -d= -f2)"
            done
    echo ""
}
EOF
```

There are also two assumptions:
- The SSH connection to the node is made via key (and not a password).
- There is a defined custom SSH `HostName` to connect to the node (`dusk` by default, and it can be tweaked by setting the `DUSK_SSH_HOSTNAME` environment variable).

Here is a sample `~/.ssh/config` file to see what I mean:

```bash
Host dusk
    User USER
    HostName IP
    PreferredAuthentications publickey
```

The app will issue commands like `ssh -t DUSK_SSH_HOSTNAME "source .profile ; COMMAND"` (where `COMMAND` will be one of the two functions defined above, nothing more ; and you can inspect the source code to double-check).

## Run

Update data on a regular basis (to be done via a daily cron job):

```bash
python -m app --update
```

Start the local web server at [http://localhost:1923](http://localhost:1923):

```bash
python -m app
```

## Test

> If you test, you're a coward.

> Si tu testes, t’es un lâche.

## Preview

On desktop:

![Preview on a large screen](./screenshots/dusk-monitoring-large-screen.png)

On smartphone:

![Preview on a small screen](./screenshots/dusk-monitoring-small-screen.png)
