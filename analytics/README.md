# Private gameplay analytics

PHP 8.1+ on the existing Hostinger site. No external service, paid dependency or public stats API.
Deploy the files in this folder (except README/config.example) to `/analytics/` alongside the game.
Generate credentials once with `python tools/prepare-analytics.py <php executable>`; upload the generated
`config.php` directly into `/analytics/`, never inside a ZIP in a publicly served folder. Keep the generated
`build/deploy/analytics-secrets/admin-access.txt` private. Configuration and credentials are gitignored.

`config.php` defines the bcrypt password hash, an HMAC secret and a data directory. Production data defaults
to `/home/u481134120/domains/alphasquaredgames.com/.vertigo-analytics`, outside `public_html`. The code refuses
to report totals if storage cannot be read. PHP creates it with restricted permissions. Do not relocate it
under a public web root. Include this directory in hosting backups; deploying code must never replace it.

The dashboard `/analytics/` uses a password, CSRF-protected login, regenerated sessions, a Secure/HttpOnly/
SameSite cookie and an eight-hour session expiry. Login is rate-limited. Config and library direct access
are also denied by `.htaccess`. The JSON/CSV exports require the same authentication; no public totals
endpoint exists. A future public page must expose only deliberately selected aggregates, never IDs or
session records. Do not publish the private export wholesale.

## Counting definitions

- Unique players: distinct keyed browser-ID digests among sessions that began playing. This is not a
  verified person count. Incognito, storage clearing and another browser/device create another identity.
- Visit: one page load. Play: one Begin or Continue. New games and continues are shown separately.
- Climb attempt: grounded arrival on any stair after beginning or a fatal fall. It is not a completed climb.
- Climbed metres: positive grounded stair movement. Walked metres: grounded planar movement. Teleports,
  falls, airborne jumping and collapse displacement are excluded from distance.
- Falls: deaths that respawn at a checkpoint. Short drops (>1.2 m) are counted separately. Fall distribution
  uses the last grounded stair lap, not the exact death coordinate.
- Roof arrival: transition onto the roof. Button presses count roof use attempts; extinguishes count
  accepted activations. Collapse starts and the actual ending screen are separate milestones.
- Active time: visible, unpaused play, including the collapse. Slow frames: frames longer than 50 ms;
  pauses/hidden tabs and gaps over one second are excluded. This is coarse field performance data.
- Additional totals: jumps/auto-jumps, crumble warnings, broken slabs, creature grabs, nerve stumbles and
  seconds below 35% nerve. Per-lap reach and last-seen distributions help locate difficulty bottlenecks.
- Dashboard periods group visits by server start time in UTC; all activity in that session belongs to that
  cohort. No-update for two minutes means "last seen", not proven abandonment.

## Reliability and privacy

The client sends cumulative snapshots every 15 seconds, on milestones and on page hide. The collector
merges maxima under a per-session file lock with atomic replacement, so retries and out-of-order snapshots
do not add duplicate totals. Random visit IDs distinguish tabs/reloads; random visitor IDs persist locally.
F8/debug marks the entire visit as test traffic (excluded by default), including its earlier snapshots.
Localhost and the review harness never collect production data. Analytics errors do not stop the game.

Schema/body/range checks, same-origin POST enforcement and IP-based request limits reduce abuse. Client
reports are not trusted proof of play and can still be forged. Network failure, opt-out, blockers and abrupt
browser termination can undercount. Tracking starts with this release; past games cannot be reconstructed.

No names, email addresses, raw user agents, referrers, device fingerprints or precise locations are sent.
Analytics does not store raw IPs; abuse-control digests rotate daily and expire after two days (lazy cleanup).
Normal web-server logs are separate. Sessions are retained for analysis. Players can opt out through
`/analytics/privacy.html`; a reload applies the choice to already-open game tabs.

JSON session files are a deliberately small hosting-compatible store. The dashboard scans the files when
refreshed; at high traffic, migrate this schema to an indexed database and roll up historical days. Keep the
store backed up. The collector itself updates only one session record per request.

## Tests

`node tests/telemetry.js` checks client counters, movement bounds, hidden-time exclusion, debug runs and opt-out.
`python tests/analytics-backend.py <php executable>` runs real PHP HTTP integration checks with isolated data:
login, unauthenticated denial, input rejection, deduplication, multiple plays, exports and debug filtering.
Also run the normal build/audio/mobile checks and the browser scene harness before publishing the game.

## Approximate locations

Hostinger GeoIP is enabled only in this analytics directory using `GeoIPEnable On` in `.htaccess`.
The collector reads the server-generated `GEOIP_COUNTRY_CODE`, `GEOIP_COUNTRY_NAME`, and optional
`GEOIP_REGION_NAME`/`GEOIP_REGION` variables. HTTP headers and client-supplied location fields are
never trusted. No browser permission, external IP lookup request, raw IP, city or coordinates are used
or stored by this feature. Hostinger maintains its own database. See
https://www.hostinger.com/support/3738302-how-to-enable-geoip-at-hostinger/ .

Location is captured once per visit. Old visits without location show Unknown; an old visit still sending
updates can gain a location. The private dashboard and JSON export include country/region breakdowns.
Unique browsers within locations may overlap across visits. VPNs, proxies and carrier routing can place
players elsewhere; this is not proof of their physical location. If GeoIP is unavailable, tracking continues
with Unknown. On hosts without this directive, remove `GeoIPEnable On` before deploying.
