# Roadmap

This roadmap is intentionally practical: it lists buyer-visible improvements that can land without changing the Personal Edition trust model.

## Shipped

- **v1.0.4** - Clean-VPS buyer-ready. Boots end-to-end on a fresh VPS without manual workarounds; safe Delete-account flow; human-readable Config UI; Personal single-tenant auth fallback; runtime backend URL; local Python strategy worker for Sandbox-uploaded strategies.
- **v1.0.3** - Light-first license email + admin reload/reconcile API.
- **v1.0.2** - Founder console + email logo cache bust.
- **v1.0.1** - Light-first license email template redesign.
- **v1.0.0** - First public Personal Edition image line.

## v1.0.x - next

- Improve first-run diagnostics in the dashboard (license tier, activation status, version mismatch warning).
- Add a dashboard backup/export helper (one-click `pg_dump` + `.env` reminder).
- Add clearer exchange-specific API-key permission guidance.
- Expand troubleshooting docs with common Docker Desktop and VPS firewall cases.

## v1.1.x

- Lyrithm SDK ships full indicator implementations (no more shim layer); sandbox + Personal share the same indicator code path.
- Better Personal/Cloud strategy sync status UI (when the next Observatory pull lands, what is queued, etc.).
- Exchange-aware symbol list in strategy tools.
- More bundled open-source example strategies.
- Cleaner migration path for users moving from local testing to VPS.

## Later

- Optional remote backup target.
- More exchanges, depending on adapter stability and demand.
- Expanded paper-trading / backtesting bridge through Lyrithm Cloud.

