# Changelog

All notable Lyrithm Personal release changes are documented here.

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
