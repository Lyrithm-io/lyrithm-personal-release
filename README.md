# Lyrithm Personal Edition

Self-hosted Lyrithm trading bot for licensed Personal Edition buyers.

This repository contains the public release files needed to run Lyrithm Personal on your own machine or VPS. The Docker images are published on GitHub Container Registry; your `license.json` unlocks the edition and tier you purchased.

## Quick Start

```bash
mkdir -p ~/lyrithm-personal
cd ~/lyrithm-personal

curl -fsSLO https://raw.githubusercontent.com/Lyrithm-io/lyrithm-personal-release/v1.0.3/docker-compose.personal.yml
curl -fsSLO https://raw.githubusercontent.com/Lyrithm-io/lyrithm-personal-release/v1.0.3/.env.personal.example
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

Open <http://localhost:3000>.

Full walkthrough: [SETUP.personal.md](SETUP.personal.md)

## Images

| Image | Tag | Visibility |
| --- | --- | --- |
| `ghcr.io/lyrithm-io/lyrithm-personal` | `1.0.3` | Public |
| `ghcr.io/lyrithm-io/lyrithm-dashboard-personal` | `1.0.3` | Public |

Verified digests for v1.0.3:

```text
ghcr.io/lyrithm-io/lyrithm-personal:1.0.3
sha256:4b1f953d8dacefd93718149810c47912ad23dd57472864c683af927b52af3fd4

ghcr.io/lyrithm-io/lyrithm-dashboard-personal:1.0.3
sha256:8e83697d07632b7a14ff47d24e39e008d4309c1827c68f8a2c1f80447c2f7eb3
```

## What Is Included

Lyrithm Personal runs as three local containers:

- `lyrithm-personal-engine` - the trading engine
- `lyrithm-personal-dashboard` - the local dashboard
- `lyrithm-personal-postgres` - your local state database

No Clerk, Stripe, or SaaS account is required for the local stack. Your signed `license.json` is the credential.

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
