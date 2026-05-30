# Lyrithm Personal Edition Setup Guide

> v1.0.3 - self-hosted, one-time-payment edition of the Lyrithm trading bot

This guide gets your purchased Lyrithm Personal Edition online from a clean VPS or local machine in about 15 minutes.

If you bought a license from <https://lyrithm.io/personal>, you should have received an email with `license.json` attached. Keep that file private and backed up.

## Requirements

| Item | Notes |
| --- | --- |
| Docker + Docker Compose v2 | `docker --version` and `docker compose version` should work |
| VPS or local machine | 1 vCPU + 1 GB RAM minimum; 2 vCPU + 2 GB recommended |
| `license.json` | Attached to your purchase / invite email |
| Exchange API keys | Add them later from the dashboard Accounts page |

## Step 1 - Prepare the Install Directory

```bash
mkdir -p ~/lyrithm-personal
cd ~/lyrithm-personal

curl -fsSLO https://raw.githubusercontent.com/Lyrithm-io/lyrithm-personal-release/v1.0.3/docker-compose.personal.yml
curl -fsSLO https://raw.githubusercontent.com/Lyrithm-io/lyrithm-personal-release/v1.0.3/.env.personal.example
cp .env.personal.example .env
```

Put your license next to the compose file:

```bash
mv ~/Downloads/license.json ./license.json
chmod 600 license.json .env
```

## Step 2 - Edit `.env`

Set at least these two values:

```bash
DB_PASSWORD=<a long random password>
LYRITHM_MASTER_KEY=<output of: openssl rand -base64 32>
```

Optional Telegram alerts:

```bash
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

## Step 3 - First Boot

```bash
docker compose -f docker-compose.personal.yml pull
docker compose -f docker-compose.personal.yml up -d
```

Expected containers:

```text
lyrithm-personal-postgres
lyrithm-personal-engine
lyrithm-personal-dashboard
```

Watch the engine log:

```bash
docker logs -f lyrithm-personal-engine
```

You want to see license load / activation success. If activation is temporarily unreachable, the bot can enter offline grace mode; see Troubleshooting below.

## Step 4 - Open the Dashboard

Open <http://localhost:3000>.

Personal Edition has no public auth flow. `/sign-in`, `/sign-up`, `/pricing`, `/admin`, and Cloud-only Sandbox/Observatory pages are intentionally hidden or unavailable.

## Step 5 - Add an Exchange Account

Go to **Dashboard -> Accounts -> New**.

1. Pick your exchange.
2. Paste API key and secret.
3. Save.

Credentials are encrypted locally using `LYRITHM_MASTER_KEY`.

## Step 6 - Start Trading

Go to **Live Trading** and create/start an instance using an available strategy. Trades, activity, and risk status appear in the dashboard. Telegram alerts fire if configured.

## Updating Within v1.x

```bash
cd ~/lyrithm-personal
docker compose -f docker-compose.personal.yml pull
docker compose -f docker-compose.personal.yml up -d
```

Your license controls the update window. Stay within v1.x unless your purchase explicitly includes a later major line.

## Backups

Back up these three things:

1. `license.json`
2. `.env` (especially `LYRITHM_MASTER_KEY`)
3. Postgres data volume / database dump

Example database dump:

```bash
docker compose -f docker-compose.personal.yml exec -T postgres \
  pg_dump -U lyrithm lyrithm > backup-$(date +%F).sql
```

## Troubleshooting

### License signature verify failed

The license file may be modified or does not match the public key bundled into your image. Re-download the license from your email and confirm you are on the correct image tag.

### Activation endpoint unreachable

Check outbound HTTPS to `api.lyrithm.io`:

```bash
docker compose -f docker-compose.personal.yml exec engine \
  curl -fs https://api.lyrithm.io/api/v1/health
```

### Dashboard does not load

Check container status:

```bash
docker compose -f docker-compose.personal.yml ps
```

Then logs:

```bash
docker logs lyrithm-personal-dashboard
docker logs lyrithm-personal-engine
```

### Lost `.env` / master key

You can re-add exchange credentials, but encrypted credentials already stored in the database cannot be recovered without the original `LYRITHM_MASTER_KEY`.

### Lost license file

Email `support@lyrithm.io` for a manual re-issue.

## Getting Help

Open a GitHub issue for reproducible technical bugs. For billing, lost license, refunds, or private information, email `support@lyrithm.io`.

Never post secrets in an issue.
