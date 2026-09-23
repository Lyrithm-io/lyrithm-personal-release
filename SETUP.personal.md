# Lyrithm Personal Edition — Setup Guide

> Next-release preparation, not a published release. The last public image set is
> `1.1.0`. Automatic activation and the Settings activation card described below
> require the forthcoming engine and dashboard images. Maintainers must replace
> the version pins with the verified release tags before publishing this guide.

## Prepare the install

Use Docker with Compose v2. Download `docker-compose.personal.yml` and
`.env.personal.example` from the same **published release** of
[lyrithm-personal-release](https://github.com/Lyrithm-io/lyrithm-personal-release/releases).
Keep these files, `.env`, and your purchased `license.json` in one private install
directory. Use the same directory and Compose project name on every upgrade.

```bash
mkdir -p ~/lyrithm-personal
chmod 700 ~/lyrithm-personal
cd ~/lyrithm-personal
# Put the downloaded release files and your license.json here.
cp .env.personal.example .env
chmod 600 .env
chmod 644 license.json
```

The **parent directory stays private (700)** while the read-only bind mount lets
the non-root engine read `license.json`. The license contains a bearer identity
and private cryptographic material: protect it like `.env`; never post it in an
issue or support log. On Windows, restrict the install folder to your own account
using filesystem permissions. Do not run the engine as root to work around a
license-read error.

Set these in `.env`:

```dotenv
DB_PASSWORD=<long random password>
LYRITHM_MASTER_KEY=<output of openssl rand -base64 32>
```

Generate the master key once and keep it: a changed key cannot decrypt existing
exchange credentials. Optional `LYRITHM_BACKUP_ENCRYPTION_KEY` encrypts dashboard
database downloads; save that key separately from the backup.

## Start and check activation

```bash
docker compose -f docker-compose.personal.yml pull
docker compose -f docker-compose.personal.yml up -d
docker compose -f docker-compose.personal.yml ps
docker compose -f docker-compose.personal.yml logs --tail=100 engine
```

There are **five long-running services**: engine, dashboard, Python strategy worker,
PostgreSQL, and Redis. A one-shot `init-data` service prepares volume ownership
and the bundled open-source example, then exits successfully. The engine runs
as a non-root user. Redis persists shared Binance cooldowns and request
budgets. Only the dashboard is published, on `127.0.0.1:3000`.

Open **http://localhost:3000/dashboard**, then **Settings → Activation**:

| State | What to do |
| --- | --- |
| Activated | Setup is complete. The saved activation permits offline restarts with the same valid license and data volume. |
| Owner license verified | Owner licenses are verified locally; paid-license activation is not required. |
| Activation pending — offline grace | First contact failed temporarily. The original 14-day deadline is shown. Restore outbound access to the configured activation endpoint and retry after the displayed retry time. |
| Activation overdue | Restore connectivity and retry before restarting. After the original grace deadline, a still-unactivated engine refuses startup. |
| Activation needs attention | Check the license and activation URL. A definite server rejection does not receive offline grace. Contact support if the license needs replacing. |

The client authenticates its activation request, retries pending activation every
five minutes (respecting a longer server retry delay), and saves success only
after receiving a valid response. Temporary errors do not report "Activated".
The 14-day deadline, next permitted retry time and installation identity survive
container replacement. A missing or mismatched identity alongside an existing
activation marker requires restoring the matching backup; it does not create a
new grace window.
Keep the `lyrithm_data` volume: removing it loses that local state.

If startup is refused, the dashboard may not start because it waits for a healthy
engine. Read `docker compose ... logs engine`, fix the stated license, URL, or
volume-permission issue, and run `up -d` again. Never delete the activation files
to reset the grace period. Once activated, an offline restart still verifies the
signed license locally. It does not periodically re-check Cloud revocation.

Cloud's machine count is a **soft warning**, not a three-machine activation
block. HTTP 429 means temporary request throttling and is retried accordingly.

For a VPS, use an SSH tunnel to reach the loopback dashboard:

```bash
ssh -L 3000:127.0.0.1:3000 your-user@your-vps
```

## Finish buyer setup

The engine starts **IDLE**. Confirm your tier and exchange allowance in Settings.
Add an account under **Accounts → New** only when you are ready to connect your
exchange. Credentials are encrypted in the local database. Choose a strategy and
configure its risk settings before explicitly starting an instance.

Use the dashboard's supported strategy upload/sync flow. Bundled examples remain
inside the image; the optional `./strategies` mount is available under
`/app/strategies/custom` and does not hide those examples. Merely placing a file
there does not create a trading instance.

Telegram binding is under Settings. Pulse uses outbound HTTPS to the configured
Cloud relay; it requires no inbound engine port. Disabling
`LYRITHM_PULSE_RELAY_ENABLED` disables this relay and its remote actions. A legacy
direct Telegram bot still requires an Internet connection and your own bot token.

## Upgrade without losing state

1. Back up the database and the files/volumes listed below. Save the old release
   files and exact image tags or digests.
2. Keep the same install directory, Compose project name, database password, and
   master key. Replace the compose/template files with the new published set;
   merge new settings into your existing `.env` rather than overwriting secrets.
3. Set the exact tested image versions from the release notes. Engine, dashboard,
   and worker can have different release schedules:

```dotenv
# Legacy shared version remains the fallback for any unset component.
LYRITHM_VERSION=1.1.0
# Override only with verified published tags from the release notes:
# LYRITHM_ENGINE_VERSION=...
# LYRITHM_DASHBOARD_VERSION=...
# LYRITHM_WORKER_VERSION=...
```

4. Run `pull` and `up -d` again. Check container health, Settings activation, your
   accounts/instances, and history before resuming trading. Upgrading adds Redis
   when moving from the older four-service compose.

Do **not** run `down -v` or prune these volumes during an upgrade. Schema
migrations run on startup; if a release changes the schema, rollback may require
restoring its pre-upgrade database backup as well as its old images. Follow that
release's rollback instructions. The Jackson 3/activation change itself adds no
database migration.

## Backup and recovery

Preserve all of these together:

| Item | Why it is needed |
| --- | --- |
| `license.json`, `.env`, exact release files/image pins | License, database access, decryption keys, and reproducible configuration |
| PostgreSQL dump | Accounts, instances, history, strategy configuration |
| `lyrithm_data` volume | Activation marker, installation identity, Observatory cache |
| `strategy_sources` volume and custom strategy files | Uploaded strategy source |
| `redis_data` volume | Durable Binance cooldown and budget state |

The dashboard backup downloads the **database only**, not the entire install.
A database-only restore does not restore activation or Redis state. Quiesce the
stack before taking filesystem snapshots of its volumes; use a PostgreSQL dump
for the database. Keep an encrypted copy off the host and verify a restore.

Dashboard downloads end in `.sql.gz`, or `.sql.gz.enc` when
`LYRITHM_BACKUP_ENCRYPTION_KEY` is configured. An encrypted download must be
authenticated and decrypted before using `gunzip`. On a trusted recovery machine
with Python 3 and the `cryptography` package installed, use the original backup
key from `.env` when prompted (the input is hidden):

```bash
python3 - backup.sql.gz.enc recovered.sql.gz <<'PY'
import base64, getpass, os, sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

data = Path(sys.argv[1]).read_bytes()
if len(data) < 34 or data[:6] != b'LYRBK1':
    raise SystemExit('Not a Lyrithm encrypted backup')
secret = os.environ.get('LYRITHM_BACKUP_ENCRYPTION_KEY') or getpass.getpass('Backup key: ')
key = base64.b64decode(secret, validate=True)
plain = AESGCM(key).decrypt(data[6:18], data[18:], None)
with Path(sys.argv[2]).open('xb') as output:
    output.write(plain)
PY
```

The output is created only after authentication succeeds and an existing output
file is never overwritten. Protect the decrypted file as sensitive data. The
backup key decrypts the download; the separate `LYRITHM_MASTER_KEY` is still
required by the engine to read encrypted credentials in the restored database.

Example database dump (using the default database/user names):

```bash
docker compose -f docker-compose.personal.yml exec -T postgres \
  pg_dump -U lyrithm lyrithm > pre-upgrade.sql
```

Restore the original secrets, license and persistent volumes with the same
project name, import the database dump into the matching PostgreSQL version, then
start the matching release. Check logs and IDLE state before enabling trading.

## Troubleshooting

- **Invalid signature / expired or incompatible license:** restore the exact
  file from your purchase email and verify the image version. Do not edit it.
- **Cannot read license:** check the bind-mount path, file type and permissions.
- **Cannot persist activation state:** restore the original `lyrithm_data` backup
  or repair its ownership/permissions; do not replace the marker with an empty file.
- **Temporary activation outage:** check outbound access to the configured
  activation host. Settings shows the fixed deadline and next permitted attempt.
- **Old engine with new dashboard:** activation status may return 404. Install
  the matched engine/dashboard versions from the same release notes.
- **Redis unavailable:** restore Redis service health and its volume before
  using Binance. Do not clear its persisted limiter state to bypass a cooldown.

Send the image versions and redacted error text to `support@lyrithm.io`. Exclude
license files, `.env`, exchange credentials and Telegram tokens.
