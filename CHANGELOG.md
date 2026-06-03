# Changelog

All notable Lyrithm Personal release changes are documented here.

## v1.1.0 - 2026-06-03 — Stage-1 bidirectional channel: alert buttons live, Mini App support

First minor-version bump in the Personal line. v1.1.0 closes the two
"rendered-but-decorative" disclaimers from v1.0.4 by shipping
**Stage-1 of the Lyrithm Pulse relay** — a bidirectional channel
between Cloud and your local engine. Two buyer-visible features land
with it:

1. **Pulse alert quick-action buttons are now interactive.** Tap
   `[Close]` on a trade-opened alert and your engine fires the
   market-order close. Tap `[Reload]` on a drift alert and the
   instance picks up the latest parameter changes from your
   dashboard. Tap `[Info]` and a fresh balance + open-position
   snapshot lands in the chat. No more silent taps.
2. **Telegram Mini App now works for Personal buyers.** Open
   `@lyrithm_pulse_bot` in Telegram, hit the menu button, and the
   Lyrithm dashboard launches inline. All four screens — Overview,
   Strategies, Alerts, Accounts — render live data fetched from your
   own engine, transparently relayed through Cloud.

The relay is **outbound-only**: your engine opens a long-lived HTTPS
stream to `api.lyrithm.io` and the Cloud bot writes through it.
There is no inbound port on your VPS, no DDNS, no proxy. Your
exchange API keys, trade state, and license signing key never cross
the relay — Cloud handles routing, not authentication. The relay is
mutually authenticated by the same `LyrithmLicense` bearer your
engine has used since v1.0.

### Added

- **Stage-1 relay client (engine).** New `RelaySessionClient` opens
  `GET /api/v1/pulse/relay/stream` to Cloud at startup, parses
  Server-Sent Event frames, dispatches inbound `TG_CALLBACK` and
  `API_CALL` requests to the engine, and posts responses back via
  `POST /api/v1/pulse/relay/respond`. Reconnect loop is
  exponential-backoff with full jitter (1s → 2s → … → 30s) and
  uses `X-Lyrithm-Resume-Session-Id` for session continuity through
  network blips. Default-on; opt-out via
  `LYRITHM_PULSE_RELAY_ENABLED=false`.
- **Real engine actions on alert button taps.** `[Close][Yes]` calls
  the same `cancelAllOrders` + `placeMarketOrder` pair the dashboard
  Close button uses. `[Reload]` calls `ReloadService.reload`.
  `[Info]` renders live `AccountInfo` + `PositionInfo` from your
  configured exchange adapter.
- **Mini App `personal_only` state mounts the full AppShell.**
  The Phase 1 placeholder card is gone; Personal-tier buyers now
  see the same four-tab UI as Cloud users. Live KPIs, strategy
  list, accounts table, alerts feed — all fetched from your engine.
- **SETUP.personal.md** has a new "Stage-1 bidirectional channel"
  section explaining the architecture, the opt-out flag, and the
  trust model.

### Changed

- Compose default `LYRITHM_VERSION` bumped to `1.1.0`.
- Engine no longer logs `RelayPulseDelivery disabled` at startup by
  default — the relay is on. Air-gapped buyers see the disabled
  message once they set `LYRITHM_PULSE_RELAY_ENABLED=false`.

### Removed

- The v1.0.4 "Known limitations" disclaimers about alert buttons and
  Mini App support are obsolete. They were the proximate motivation
  for shipping Stage-1.

### Verified

`docker-compose -f docker-compose.personal.yml up -d` on a fresh
Ubuntu 22.04 VPS:

- `ghcr.io/lyrithm-io/lyrithm-personal:1.1.0`
- `ghcr.io/lyrithm-io/lyrithm-dashboard-personal:1.1.0`
- `ghcr.io/lyrithm-io/lyrithm-strategy-worker-python:1.1.0`

Bot-side smoke: pair `@lyrithm_pulse_bot` → open a position from the
dashboard → wait for the `Trade opened` Pulse alert → tap `[Close]`
on the alert → confirm screen renders within ~1s → tap `[Yes]` →
position closes on the exchange → confirmation message lands in
the chat.

Mini App smoke: open the bot in Telegram → tap the menu button →
Mini App opens → Overview shows live total equity, open P&L,
closed-PnL-30d, win rate, equity curve sparkline — all read from
your own engine via the relay.

### Recommended upgrade

If you are on v1.0.4 and want the interactive alert buttons + Mini
App, upgrade in place:

```bash
cd ~/lyrithm-personal
# Update LYRITHM_VERSION=1.1.0 in .env.
docker compose -f docker-compose.personal.yml pull
docker compose -f docker-compose.personal.yml up -d
```

No schema breakage, no config rewrites. The relay client opens its
outbound stream on first boot.

If you are running on an air-gapped network and never want your
engine to talk to `api.lyrithm.io` even for Pulse outbound, set
`LYRITHM_PULSE_RELAY_ENABLED=false` in `.env` before upgrade. Your
engine continues to operate; you lose the new button + Mini App
features but the legacy direct-bot path (using your own
`TELEGRAM_BOT_TOKEN`) still works.

## v1.0.4 - 2026-06-01 — Clean-VPS buyer-ready + multi-tenant Pulse + bot UI redesign

First release that boots end-to-end on a fresh VPS from `docker compose up -d` alone, with no manual `application.yml` mount, no nginx side-car, no DB hack, no chmod workaround. This is the recommended starting point for new buyers.

In addition to the clean-VPS fixes that landed on 2026-05-31, v1.0.4 ships the multi-tenant Lyrithm Pulse alert path so per-buyer alerts route to each owner's own Telegram chat instead of a single shared admin chat, the Stage-0 relay so the Personal binary no longer ships a Telegram bot token, and a redesigned bot UI built entirely on inline keyboards (with quick-action buttons on alert pushes and a two-step confirm before any market close).

### Fixed

- Engine image no longer hard-requires an external `/app/config/application.yml`. The bundled classpath config (`application.yml` + `application-personal.yml`) is now the source of truth; an external file is still honoured if mounted (`--spring.config.additional-location=optional:...`). v1.0.3 buyers had to copy the entire engine config file out of the repo or the engine refused to boot.
- Compose healthcheck endpoint corrected from `/actuator/health` (which always 404'd — the engine has no Spring Actuator dependency) to `/api/v1/health` (the real `HealthController` route). The engine now reports `(healthy)` within 60s of boot instead of permanently `unhealthy`.
- `license.json` permission story rewritten: the file is now `chmod 644` so the non-root engine user can read it. The previous `chmod 600 root:root` guidance silently broke every buyer install (`Permission denied` in the engine log; bot refused to start). The file is Ed25519-signed, so leaking the bytes does not let anyone forge a license.
- Dashboard `/` route no longer crashes the Personal build with `Cannot read properties of null (reading 'sessionId')`. The page now redirects straight to `/dashboard` when `LYRITHM_EDITION=personal` and never touches Clerk.
- Dashboard API proxy honours the runtime `LYRITHM_BACKEND_URL` / `LYRITHM_SANDBOX_URL` env vars. Previously the rewrite was baked into `routes-manifest.json` at `next build` time (a quirk of `output: standalone`), so the prebuilt GHCR image always shipped `http://localhost:8080` and could not reach the engine container at `http://engine:8080` without an nginx side-car. The proxy now runs as middleware and re-reads env vars on every request.
- Backend REST endpoints no longer 401 in Personal mode. The engine's `CurrentUserResolver` now resolves to the single-tenant `LYRITHM_PERSONAL_OWNER_ID` UUID (default = legacy admin UUID) when no Clerk JWT and no `X-Lyrithm-User-Id` header is present. Cloud behaviour is unchanged.
- Account deletion is now safe end-to-end. `DELETE /api/v1/account-credentials/{name}` orchestrates: (1) stop the running worker via `TradingEngine.removeAccount`, (2) delete the matching `strategy_instances` row so the ConfigPoller cannot resurrect the worker on the next 30s tick, (3) delete the encrypted credential row. The dashboard surfaces this in a two-tap confirm modal with an explicit "Exchange position is NOT auto-closed" warning.

### Added

- Default `LYRITHM_TRADING_INITIAL_STATE=idle` for Personal stacks. The bot boots without subscribing any account so a fresh install does not start placing orders before the operator wires their first exchange API key.
- Default `LYRITHM_PERSONAL_OWNER_ID=00000000-0000-0000-0000-000000000001`. Overridable for buyers migrating an existing DB whose rows were stamped with a custom owner.
- `<DeleteAccountButton>` two-tap component on the Accounts table — buyers can safely tear down an account from one click instead of editing the row first.
- Human-readable Live Trade Config view. The Live Trading instance detail page now leads with named field cards (Risk per trade, Leverage base/min/max, Trading hours, ADX thresholds, On/Off pills, X/8 direction-rule pills) instead of dumping the raw three-layer JSON diff. The full template-default / override / effective table and the JSON override editor stay one click away under an "Advanced" collapsible.
- Personal Add-Account form can use the built-in Java `vegas-adx` (`templateId=null`) or an uploaded Python strategy template. v1.0.4 now ships the bundled gRPC Python strategy worker in the Personal compose stack.
- **Per-owner Telegram alert fan-out (sub-task 1).** New `TelegramRouter` + `AccountOwnerRegistry` route every per-account alert (trade open / close, ledger drift, hot-reload, API key health) to the chat owned by the account's owner. Operator-wide events (startup, daily summary) still go to the legacy admin chat. Producer signatures unchanged; behaviour is a drop-in upgrade.
- **Lyrithm Pulse Stage-0 relay (sub-task 2).** Personal binary no longer carries a Telegram bot token. Bind + alert delivery now go through the Cloud relay (`POST /api/v1/pulse/relay/{start-bind,binding,send}`) authenticated by `Authorization: LyrithmLicense <id>`. New V26 Flyway migration adds `pulse_relay_bind_tokens` and `pulse_relay_bindings` tables, license-keyed. `@lyrithm_pulse_bot` deep-link handler tries the per-Clerk-user table first then falls through to the per-license relay table, so both Cloud users and Personal buyers bind through the same dashboard "Bind via Telegram" button and the same bot identity. The buyer's chat ID never leaves Cloud's database — Personal sees only the license id.
- **Bot UI redesign on inline keyboards (sub-task 3).** Main menu is now one row per account that drills into a per-account view (LONG / SHORT / CLOSE / Info / Risk / Reload / Back), plus a global row for Status / Balance / P&L / Risk / Reload / Events / Instances / Emergency Stop. Slash command `/menu` and the persistent `🤖 Menu` reply-keyboard tile both open this surface. Demo button is no longer surfaced in the buyer menu (the `/demo` slash command stays for operators). Closing a position is a two-step `CLOSE` → confirm screen → `CLOSE_GO`, so a misclick on a quick-action button cannot fire a market order. Alert messages now carry one-tap quick-action buttons: trade-opened alerts surface `[Close][Info]`, drift alerts surface `[Reload][Info]`, API-key-failure alerts surface `[Info]`, reload-failed alerts surface `[Retry]`. The first interaction in each chat after upgrade attaches the new `🤖 Menu` reply keyboard, which automatically replaces any stale 11-button keyboard cached on the Telegram client from older builds.

### Verified

`docker-compose -f docker-compose.personal.yml up -d` on a fresh Ubuntu 22.04 VPS, no manual workarounds:

- `ghcr.io/lyrithm-io/lyrithm-personal:1.0.4`
- `ghcr.io/lyrithm-io/lyrithm-dashboard-personal:1.0.4`
- `ghcr.io/lyrithm-io/lyrithm-strategy-worker-python:1.0.4`

Smoke path: pull images without docker login → compose up → all four containers `(healthy)` → SSH-tunnel `/dashboard` → Add Aster mainnet account → Start instance → bot reports `running=true` with a live balance read → Delete account from UI → all rows gone.

Bot-side smoke: pair `@lyrithm_pulse_bot` from the dashboard Settings page → `/start <token>` deep-link from Telegram → bot replies `✨ Lyrithm Pulse connected.` → tap `🤖 Menu` reply-keyboard tile → inline Main menu renders with account list + global actions → tap an account → per-account inline keyboard renders → tap `❌ Close` → two-step confirm screen renders before any market order fires.

### Known limitations

- **Alert quick-action buttons are rendered but not yet interactive on Personal Edition.** Pulse-routed alerts include inline keyboards such as `[Close][Info]`, `[Reload][Info]`, and `[Retry]`. Tapping them is silently dropped today because the callback round-trip from Telegram → Cloud relay → buyer's local engine is not implemented in Stage-0 of the relay (Cloud's bot polling cannot reach back into your VPS). Alerts deliver normally; only the one-tap buttons are decorative. Use the bot's main menu (slash `/menu` or the `🤖 Menu` reply-keyboard tile) or the dashboard to act on alerts. Stage-1 of the relay (v1.1+) adds the bidirectional channel that wires these buttons.
- **Telegram Mini App is not available for Personal Edition in v1.0.** The Mini App at `m.lyrithm.io` (planned for v1.0 Cloud) cannot reach a buyer's self-hosted engine — Personal engines run behind NAT / residential IPs and the Cloud Mini App URL is global. Personal buyers continue to use the local dashboard (over SSH tunnel for now) and the Telegram bot for alerts. Mini App parity for Personal Edition is planned for v1.2 once the Stage-1 bidirectional relay is in place.

### Recommended upgrade

If you are on v1.0.3 and hit any of the clean-VPS workarounds (license permission, nginx proxy, manual `application.yml` mount, DB `template_id` clearing), upgrade to v1.0.4:

```bash
cd ~/lyrithm-personal
# Optional: drop any /app/config/application.yml mount line you added by hand.
# Update LYRITHM_VERSION=1.0.4 in .env.
docker compose -f docker-compose.personal.yml pull
docker compose -f docker-compose.personal.yml up -d
# If your license.json is still chmod 600, run:  chmod 644 license.json
```

## v1.0.3 - 2026-05-30

### Fixed

- License delivery email reverted to a light-first design for consistent Gmail iOS / desktop rendering.
- Manual admin license issuance now uses a unique synthetic session id, preventing idempotent re-use from skipping email delivery.
- Docker Compose wiring includes Resend email-delivery environment variables on the Cloud/operator side.

### Added

- Admin operations API used by the Cloud dashboard Quick Actions menu:
  - reload all running instances
  - reconcile all running workers
- Dashboard Quick Actions menu and Alert Bell.
- Sandbox workbench styled dropdowns and searchable symbol combobox.

### Verified

- `ghcr.io/lyrithm-io/lyrithm-personal:1.0.3`
  - `sha256:4b1f953d8dacefd93718149810c47912ad23dd57472864c683af927b52af3fd4`
- `ghcr.io/lyrithm-io/lyrithm-dashboard-personal:1.0.3`
  - `sha256:8e83697d07632b7a14ff47d24e39e008d4309c1827c68f8a2c1f80447c2f7eb3`

## v1.0.2 - 2026-05-30

### Added

- Founder console for manual Personal license operations.
- License email logo URL cache bust.

## v1.0.1 - 2026-05-30

### Fixed

- Light-first license email template redesign.

## v1.0.0 - 2026-05-29

### Added

- First public Personal Edition image line.
- Personal engine image.
- Personal dashboard image.
- Signed license loading and local dashboard identity.

