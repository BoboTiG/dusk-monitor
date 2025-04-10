# Dusk Node Monitoring

> [!TIP]
> Become **my boss** to help me work on this awesome software, and make the world better:
> 
> [![Patreon](https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/mschoentgen)

A dashboard for your Dusk node.

This is __safe__: it works outside the node, no need to install anything on the node.

Interesting links:

- 🇬🇧 [How to query your Dusk node?](https://www.tiger-222.fr/luma/en/blockchain/node-dusk-http-wss.html)
- 🇫🇷 [Communiquer avec votre nœud Dusk](https://www.tiger-222.fr/luma/blockchain/node-dusk-http-wss.html)
- 🇫🇷 [Comment déployer un nœud Dusk ?](https://www.tiger-222.fr/luma/blockchain/node-dusk.html)

Dusk wallet for tips:
```
VKZpBrNtEeTobMgYkkdcGiZn8fK2Ve2yez429yRXrH4nUUDTuvr7Tv74xFA2DKNVegtF6jaom2uacZMm8Z2Lg2J
```

---

## Install

```bash
python3 -m venv venv
. ./venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

1. Start the local [web server](#web-server).
   - Open the [dashboard](http://localhost:1923) for the setup (and for later updates, you can directly go to the [/setup](http://localhost:1923/setup) page).
1. Set up the [cron job](#update-data).
1. That's it!

### Environment Variables

- `DATA_DIR=path/to/folder`: the folder where node data will be stored, it's recommended using a folder outside the repository.
- `DEBUG=0`: disable most `print()` statements.

## Commands

### Update Data

The first time, it will scan the entire blockchain to find blocks generated by the node, then subsequent calls will only fetch new blocks since the last run.

Here is the cron job to update data every 5 minutes:

```bash
*/5 * * * * cd /path/to/dusk-monitor && DATA_DIR=../dusk-monitor-data/node-1 ./venv/bin/python -m app --update
```

### Web Server

Start the local web server at [http://localhost:1923](http://localhost:1923):

```bash
DATA_DIR=../dusk-monitor-data/node-1 python -m app
```

#### Endpoints

- [/](http://localhost:1923/): the dashboard.
- [/setup](http://localhost:1923/setup): where you can tweak options, and set the provisoner public key.
- [/rewards](http://localhost:1923/rewards): redirects to the daily rewards chart.
- [/rewards/hour](http://localhost:1923/rewards/hour): hourly rewards chart.
- [/rewards/day](http://localhost:1923/rewards/day): daily rewards chart.
- [/rewards/month](http://localhost:1923/rewards/month): monthly rewards chart.
- [/rewards/year](http://localhost:1923/rewards/year): yearly rewards chart.

## Preview

> [!NOTE]
> Those screenshots might be outdated, but the essence of the dashboard is still relevant from those pictures.
> Also, if you have any **design skills**, please take a look at [#5](https://github.com/BoboTiG/dusk-monitor/issues/5) 🙏

On desktop:

![Preview on a large screen](./screenshots/dusk-monitoring-large-screen.png)

On smartphone:

<img src="./screenshots/dusk-monitoring-small-screen.png" width="50%"/>
