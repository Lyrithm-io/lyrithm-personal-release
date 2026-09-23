# Lyrithm Personal Edition

Self-hosted Lyrithm trading bot for licensed Personal Edition buyers.

> This working tree prepares the **next release**. The public image pins below
> remain `1.1.0`; activation status and the buyer-flow fixes require new engine
> and dashboard images. They have not been published yet. Use a complete,
> published release set rather than mixing these files with older images.

This repository contains the public release files needed to run Lyrithm Personal on your own machine or VPS. The Docker images are published on GitHub Container Registry; your `license.json` unlocks the edition and tier you purchased.

## Quick Start

```bash
mkdir -p ~/lyrithm-personal
cd ~/lyrithm-personal

curl -fsSLO https://raw.githubusercontent.com/Lyrithm-io/lyrithm-personal-release/v1.1.0/docker-compose.personal.yml
curl -fsSLO https://raw.githubusercontent.com/Lyrithm-io/lyrithm-personal-release/v1.1.0/.env.personal.example
cp .env.personal.example .env
```

Then:

1. Put your emailed `license.json` in the same directory.
2. Edit `.env` and set `DB_PASSWORD` plus `LYRITHM_MASTER_KEY`.
3. Start the stack:

```bash
docker compose -f docker-compose.personal.yml pull
docker compose -f docker-compose.personal.yml up -d
```

Open <http://localhost:3000/dashboard>.

Full walkthrough: [SETUP.personal.md](SETUP.personal.md)

## Images

| Image | Tag | Visibility |
| --- | --- | --- |
| `ghcr.io/lyrithm-io/lyrithm-personal` | `1.1.0` | Public |
| `ghcr.io/lyrithm-io/lyrithm-dashboard-personal` | `1.1.0` | Public |
| `ghcr.io/lyrithm-io/lyrithm-strategy-worker-python` | `1.1.0` | Public |

Verified pull digests are added here after each release tag's GHCR build completes. v1.0.4 and v1.0.3 remain pullable for older buyers that have not upgraded; see [CHANGELOG.md](CHANGELOG.md) for the upgrade story.

```text
# v1.0.4 (superseded by v1.1.0 for new installs)
ghcr.io/lyrithm-io/lyrithm-personal:1.0.4
ghcr.io/lyrithm-io/lyrithm-dashboard-personal:1.0.4
ghcr.io/lyrithm-io/lyrithm-strategy-worker-python:1.0.4

# v1.0.3 (older)
ghcr.io/lyrithm-io/lyrithm-personal:1.0.3
sha256:4b1f953d8dacefd93718149810c47912ad23dd57472864c683af927b52af3fd4

ghcr.io/lyrithm-io/lyrithm-dashboard-personal:1.0.3
sha256:8e83697d07632b7a14ff47d24e39e008d4309c1827c68f8a2c1f80447c2f7eb3
```

## What Is Included

The next-release stack runs five local services plus a one-shot `init-data`
job that prepares persistent-volume permissions and the bundled open-source
example before the non-root engine starts:

- `lyrithm-personal-engine` - the trading engine
- `lyrithm-personal-dashboard` - the local dashboard
- `lyrithm-personal-strategy-worker-python` - the local gRPC Python strategy worker for Sandbox-uploaded strategies
- `lyrithm-personal-postgres` - your local state database
- `lyrithm-personal-redis` - persistent Binance cooldowns and request budgets

Settings shows activation success, a fixed initial offline-grace deadline, and
connection retry status. Keep the same Compose project and volumes on upgrade;
see the [setup and recovery guide](SETUP.personal.md). The published `v1.1.0`
quick-start downloads above retain their historical four-service package.

No Clerk, Stripe, or SaaS account is required for the local stack. Your signed `license.json` is the credential.

Starting in v1.1.0 the engine also opens an **outbound-only** HTTPS stream to `api.lyrithm.io` so Telegram inline buttons (`[Close]`, `[Reload]`, `[Info]`, `[Retry]`) and the Lyrithm Mini App can act on your data without anyone reaching back into your VPS. Your exchange keys and trade state stay local. The relay is mutually authenticated by your `license.json`; air-gapped buyers can disable it with `LYRITHM_PULSE_RELAY_ENABLED=false` and keep using the legacy direct-bot path. See [SETUP.personal.md](SETUP.personal.md).

## Support

- Setup help: [SUPPORT.md](SUPPORT.md)
- Security reporting: [SECURITY.md](SECURITY.md)
- Bugs: open a GitHub issue with logs and your image tag
- Billing / lost license / re-issue: `support@lyrithm.io`

Do not paste your `license.json`, exchange API keys, `.env`, or Telegram token into GitHub issues.

## Release Notes

See [CHANGELOG.md](CHANGELOG.md).

## Roadmap

See [ROADMAP.md](ROADMAP.md).

