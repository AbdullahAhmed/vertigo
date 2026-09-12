// First-party aggregate gameplay telemetry. No names, raw user agents, locations or referrers.
const STATS = {
  enabled: false, metrics: {}, fallsByLap: Array(12).fill(0), reached: Array(12).fill(0), seq: 0,
  climbing: false, lastClock: 0, elapsed: 0, dirty: false, test: false,
  init(touch) {
    if (location.hostname !== 'vertigo.alphasquaredgames.com' || location.protocol !== 'https:' || window.__review || typeof crypto.randomUUID !== 'function') return;
    try {
      if (localStorage.getItem('vertigo.analytics.optout') === '1') return;
      this.visitor = localStorage.getItem('vertigo.visitor.v1');
      if (!/^[a-f0-9-]{36}$/.test(this.visitor || '')) { this.visitor = crypto.randomUUID(); localStorage.setItem('vertigo.visitor.v1', this.visitor); }
    } catch (_) { this.visitor = crypto.randomUUID(); }
    this.session = crypto.randomUUID(); this.platform = touch ? 'mobile' : 'desktop';
    this.enabled = true; this.lastClock = performance.now(); this.add('page_views');
    this.timer = setInterval(() => this.flush(), 15000);
    addEventListener('pagehide', () => this.flush(true));
    document.addEventListener('visibilitychange', () => { if (document.hidden) this.flush(true); this.lastClock = performance.now(); });
    this.flush();
  },
  add(name, amount = 1) { if (!this.enabled) return; this.metrics[name] = (this.metrics[name] || 0) + amount; this.dirty = true; },
  begin(continued) { this.add('plays'); this.add(continued ? 'continues' : 'new_games'); this.climbing = false; this.flush(); },
  event(name) { this.add(name); this.flush(); },
  fall(lap) { this.add('falls'); if (this.enabled) this.fallsByLap[Math.max(0, Math.min(11, lap))]++; this.climbing = false; this.flush(); },
  step(x, y, z, dt) {
    if (!this.enabled || COL.active || G.state !== 'play' || document.hidden || !locked) return;
    const distance = Math.hypot(P.pos.x-x, P.pos.z-z), rise = P.pos.y-y;
    if (P.grounded && distance <= dt*12+.05) this.add('walked_m', distance);
    if (P.grounded && rise > 0 && rise <= STEP+.05) this.add('climbed_m', rise);
    this.metrics.max_height = Math.max(this.metrics.max_height || 0, Math.min(72.5, P.pos.y));
    if (P.onRoof && !this.wasRoof) this.event('roof_arrivals');
    this.wasRoof = P.onRoof;
    if (P.grounded && P.groundRef?.slab !== undefined) {
      const lap = Math.min(11, Math.floor(P.groundRef.slab/16)); this.reached[lap] = 1; this.lastLap = lap;
      if (!this.climbing) { this.climbing = true; this.event('climb_attempts'); }
    }
  },
  frame() {
    if (!this.enabled) return;
    const now = performance.now(), delta = (now-this.lastClock)/1000; this.lastClock = now;
    if (document.hidden || !locked || G.state !== 'play' || delta <= 0 || delta > 1) return;
    this.add('active_seconds', delta); this.add('frames'); if (delta > .05) this.add('slow_frames');
    if (P.nerve < .35) this.add('panic_seconds', delta);
  },
  markTest() { if (this.enabled) { this.test = true; this.event('debug_skips'); } },
  payload() {
    return {v:1, session:this.session, visitor:this.visitor, platform:this.platform, build:'analytics-1', seq:++this.seq,
      test:this.test, metrics:this.metrics, falls_by_lap:this.fallsByLap, reached:this.reached, last_lap:this.lastLap ?? -1};
  },
  flush(beacon = false) {
    if (!this.enabled || !this.dirty) return;
    const body = JSON.stringify(this.payload()); this.dirty = false;
    if (beacon && navigator.sendBeacon?.('analytics/collect.php', new Blob([body],{type:'text/plain'}))) return;
    fetch('analytics/collect.php', {method:'POST',headers:{'Content-Type':'text/plain'},body,keepalive:true,credentials:'omit'})
      .then(r => { if (!r.ok) this.dirty = true; }).catch(() => { this.dirty = true; });
  },
};
