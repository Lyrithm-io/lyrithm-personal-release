# Lyrithm Personal Edition Setup Guide

> v1.1.0 - self-hosted, one-time-payment edition of the Lyrithm trading bot

This guide gets your purchased Lyrithm Personal Edition online from a clean VPS or local machine in about 10 minutes.

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

curl -fsSLO https://raw.githubusercontent.com/Lyrithm-io/lyrithm-personal-release/v1.1.0/docker-compose.personal.yml
curl -fsSLO https://raw.githubusercontent.com/Lyrithm-io/lyrithm-personal-release/v1.1.0/.env.personal.example
cp .env.personal.example .env
```

Put your license next to the compose file:

```bash
mv ~/Downloads/license.json ./license.json

# license.json is Ed25519-signed; leaking it does not let anyone forge a
# valid license, so 644 is the right posture. The engine runs as a
# non-root user inside the container ??600 owned by host root cannot
# be read by that uid and the bot would refuse to start. The .env file
# is the real secret-bearing file, so that one stays 600.
chmod 644 license.json
chmod 600 .env
```

## Step 2 - Edit `.env`

Set at least these two values:

```bash
DB_PASSWORD=<a long random password>
LYRITHM_MASTER_KEY=<output of: openssl rand -base64 32>
```

Optional Telegram alerts route through the hosted Lyrithm Pulse relay by default - the Personal binary itself does not ship a Telegram bot token. After Step 4 below you will bind the official `@lyrithm_pulse_bot` to your chat from the dashboard Settings page. The relay endpoint is preconfigured to `https://api.lyrithm.io` and authenticated by your license id; the bound chat ID never leaves the Lyrithm cloud relay.

If you want offline-only Telegram alerts via your own bot identity (no relay round-trip), uncomment and fill these instead - it disables the relay path:

```bash
# TELEGRAM_BOT_TOKEN=...
# TELEGRAM_CHAT_ID=...
# LYRITHM_PULSE_ENABLED=false
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

You should see, in order:

```text
Personal Edition license loaded ...
TradingState initialised: IDLE
Trading engine started in IDLE mode - no accounts will be subscribed.
```

The bot intentionally boots in IDLE so you can wire your first exchange account from the dashboard before any real subscription happens. Telegram alerts (if configured) will fire on activation success.

### Pulse alert quick-action buttons (new in v1.1.0)

Alert messages delivered through the hosted Lyrithm Pulse relay carry inline keyboard buttons such as `[Close]`, `[Reload]`, `[Info]`, and `[Retry]`. In v1.1.0 these buttons **execute on your local engine** through the Stage-1 bidirectional relay channel:

- `[Close]` on a trade-opened alert renders a two-step confirm screen, then fires a market-order close at the same exchange the trade opened on.
- `[Reload]` on a drift alert calls the engine's `ReloadService` to re-apply parameter changes from your dashboard.
- `[Info]` renders live balance + open-position state from your configured exchange adapter.
- `[Retry]` on a reload-failure alert re-runs the reload.

Tap-to-action round-trip is typically under 1.5 seconds. If your engine is offline the bot answers the tap with `"Personal engine offline. Retry shortly."` so the spinner clears immediately.

### Telegram Mini App (new in v1.1.0)

Open `@lyrithm_pulse_bot` in Telegram and tap the chat menu button (left of the text box). The Lyrithm dashboard launches inline as a Telegram Mini App: Overview / Strategies / Alerts / Accounts. All data is fetched live from **your own engine** through the relay; nothing is rendered from a Cloud cache. You can act on your bot from your phone without an SSH tunnel.

If you opted out of the relay (`LYRITHM_PULSE_RELAY_ENABLED=false`), the Mini App will show "Personal engine offline" — use the local dashboard over SSH tunnel instead.

### Activation grace

If activation is temporarily unreachable, the engine enters offline grace mode (14 days); see Troubleshooting.

## Step 4 - Open the Dashboard

Open <http://localhost:3000/dashboard>.

Personal Edition has no public auth flow. `/sign-in`, `/sign-up`, `/pricing`, `/admin`, and Observatory and Cloud execution tools are intentionally hidden or unavailable. Sandbox Labs stays local so you can upload Python strategies for the bundled worker. The single-tenant license file is the credential - anyone who can reach the port can drive the bot, so keep the dashboard bound to localhost (the default) and reach it over an SSH tunnel from your laptop.

```bash
# From your laptop, tunnel the dashboard port off the VPS:
ssh -L 3000:127.0.0.1:3000 <user>@<vps-host>
# Then open http://localhost:3000/dashboard on your laptop.
```

## Step 5 - Add an Exchange Account

Go to **Dashboard -> Accounts -> Add account**.

1. Pick your exchange (Binance / OKX / Bybit / Bitget / Hyperliquid / dYdX v4 / Aster).
2. Paste API key + secret (and the third field for OKX, Bitget, EVM DEX, or dYdX as prompted).
3. Save.

v1.1.0 includes the built-in Java `vegas-adx` strategy and the local gRPC Python strategy worker. You can use `vegas-adx` immediately, or upload a Python template in **Dashboard -> Sandbox Labs** and select it when adding an exchange account.

Credentials are encrypted locally using `LYRITHM_MASTER_KEY`. They never leave your machine.

### Exchange API key permissions

Lyrithm Personal Edition is non-custodial: the bot reads market data, opens / modifies / closes futures positions, but **never withdraws**. Cut your API keys to match — if the bot's key is ever leaked, the blast radius stays inside the futures wallet you fund it with.

| Exchange | Enable | Disable | Required third field |
| --- | --- | --- | --- |
| Binance | Enable Futures, Enable Reading | **Disable Spot trading, Disable Internal Transfer, Disable Universal Transfer, NEVER enable Withdrawals** | — |
| OKX | Trade + Read | **No Withdraw** | API passphrase |
| Bybit | Read-Write (Derivatives only) | **No Withdrawal, No Sub-account transfer** | — |
| Bitget | Read + Trade | **No Withdraw, No Internal transfer** | API passphrase |
| Hyperliquid | Trade | **No Vault transfer** | API wallet private key |
| dYdX v4 | Trade | (no key — wallet-signed) | Stark / mnemonic seed |
| Aster | Read + Trade Perpetual | **No Withdraw** | — |

**IP whitelist** — every CEX listed supports per-key IP allow-listing. Always add your VPS's outbound IP. The whitelist is the single most impactful key-leak mitigation; do not skip it.

If you rotate a key, edit the account from **Dashboard -> Accounts -> [account] -> Edit credentials**. The rotation is hot — the running worker picks up the new key on its next health probe (typically within 5 minutes); restart is not required.

## Step 6 - Start Trading

Go to **Live Trading** and Start the instance the Accounts page created.

The Config page for each instance shows:

- A buyer-friendly summary (Risk per trade, Leverage, Trading hours, Strategy filters, Direction rules, Sizer mode) up top.
- An "Advanced - raw config layers" panel below for power users who want to edit JSON overrides.

Override edits hot-reload the worker in place - no restart, no missed candles.

## Updating Within v1.x

```bash
cd ~/lyrithm-personal
docker compose -f docker-compose.personal.yml pull
docker compose -f docker-compose.personal.yml up -d
```

Your license controls the update window. Stay within v1.x unless your purchase explicitly includes a later major line.

## Removing an Account Safely

Use **Dashboard -> Accounts -> Delete**, or open the account's edit page and use the Delete affordance at the bottom. The two-tap confirm tears down the entire row safely:

1. Stops the running worker (best-effort).
2. Deletes the strategy_instances row so the bot does not auto-resubscribe.
3. Deletes the encrypted credential row.

**Important:** stopping the bot does NOT auto-close any open position on the exchange. If you have an active position you want to close, do it manually on the exchange UI before or after deletion.

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

The license file may have been modified or does not match the public key bundled into your image. Re-download the license from your email and confirm you are on the correct image tag (`LYRITHM_VERSION` in `.env`).

### License permission denied / cannot read license.json

If you see `Permission denied` or `License file unreadable` in the engine log, the file is probably `chmod 600 root:root` from a previous install attempt. The non-root engine user cannot read it. Fix:

```bash
chmod 644 license.json
docker compose -f docker-compose.personal.yml restart engine
```

The license is signed; world-readable is safe (the bytes alone do not let anyone forge a license).

### Docker Desktop on macOS / Windows — file sharing

If you installed Docker Desktop locally (rather than running on a Linux VPS), the install directory needs to be inside a path Docker Desktop is allowed to bind-mount. Symptoms:

- engine logs `License file unreadable` or `failed to read license.json` even though `chmod 644 license.json` is correct,
- engine restarts repeatedly in a `CrashLoopBackOff`-style pattern.

Fix: in Docker Desktop -> Settings -> Resources -> File Sharing, add the parent path of `~/lyrithm-personal` (e.g. `/Users/<you>` on macOS, `C:\Users\<you>` on Windows). Apply & Restart. Alternatively move the install directory under an already-shared path such as `~/Documents/lyrithm-personal`.

### Port already in use (3000 / 5432 / 8080)

```text
Error response from daemon: driver failed programming external connectivity on endpoint
lyrithm-personal-dashboard: Bind for 0.0.0.0:3000 failed: port is already allocated
```

Another process is bound to the same port. Either stop that process, or override the published port in your `.env`:

```bash
# .env — uncomment + change as needed
DASHBOARD_PORT=3010
ENGINE_PORT=8081
```

Then `docker compose -f docker-compose.personal.yml up -d --force-recreate`. Postgres (5432) is only exposed inside the compose network by default, so a local Postgres on the host does not conflict.

### VPS firewall — recommended inbound posture

Lyrithm Personal does NOT need any inbound port open to the public internet. The dashboard at `3000` and the engine at `8080` are only ever reached via the loopback interface inside the VPS (you SSH-tunnel to them from your laptop), and the optional Pulse relay is **outbound-only** to `api.lyrithm.io`.

A safe `ufw` posture on Ubuntu:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp     # SSH only
sudo ufw enable
```

Do not open 3000 / 8080 to the world — the dashboard auth is the license file, and the engine has no auth wall in front of it. SSH-tunneling is the supported access pattern.

### Cannot pull image / 401 Unauthorized on `docker compose pull`

The Lyrithm Personal images are published as **public** packages on GHCR; you should not need `docker login`. If the pull still fails:

1. Confirm you're targeting `ghcr.io/lyrithm-io/...` (not the old `xxxjay123/...` namespace).
2. Confirm Docker daemon has IPv4 internet (`docker pull hello-world`).
3. Clear any stale `docker login` for `ghcr.io`: `docker logout ghcr.io`.
4. If you're behind a corporate proxy, set `HTTP_PROXY` / `HTTPS_PROXY` on the Docker daemon and restart the service.

### Engine reports unhealthy / dashboard says backend offline

Confirm the engine is healthy and `/api/v1/health` responds:

```bash
docker compose -f docker-compose.personal.yml ps
docker compose -f docker-compose.personal.yml exec engine \
  curl -fs http://127.0.0.1:8080/api/v1/health
```

Expected: `{"status":"UP","uptimeMs":??"activeAccounts":??"tradingState":"IDLE","version":"1.1.0-??}`.

If the engine is healthy but the dashboard cannot reach it, confirm the dashboard container is using the same docker network (compose auto-wires this) and that no host firewall is blocking the internal `engine:8080` hop.

### Activation endpoint unreachable

Check outbound HTTPS to `api.lyrithm.io`:

```bash
docker compose -f docker-compose.personal.yml exec engine \
  curl -fs https://api.lyrithm.io/api/v1/health
```

If reachability is the problem, the engine continues running for up to 14 days in OFFLINE_GRACE_MODE before refusing to start.

### Balance is $0.00 / no positions show up

A fresh Personal stack boots in IDLE state and does not auto-subscribe accounts. Until you Start the instance from Live Trading, the dashboard will show your accounts wired up but inactive, with zero balance reads. After Start, balances come from a live exchange call (so the API key must be valid + permissioned for read).

### Emergency stop

```bash
# Stops every container; existing exchange positions stay open.
docker compose -f docker-compose.personal.yml stop
```

To resume:

```bash
docker compose -f docker-compose.personal.yml start
```

**Reminder:** Lyrithm Personal Edition is non-custodial ??stopping the bot never auto-closes exchange positions. Close them manually on the exchange UI if needed.

### Lost `.env` / master key

You can re-add exchange credentials, but encrypted credentials already stored in the database cannot be recovered without the original `LYRITHM_MASTER_KEY`.

### Lost license file

Email `support@lyrithm.io` for a manual re-issue.

## Getting Help

Open a GitHub issue for reproducible technical bugs. For billing, lost license, refunds, or private information, email `support@lyrithm.io`.

Never post secrets in an issue.


