# Dusk Node Monitoring

Dumb & simple tool to sync & display Dusk node metrics.
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
cp db.json.sample db.json
```

Add the provisioner public key in `db.json`.

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

> If you test you're a coward.
