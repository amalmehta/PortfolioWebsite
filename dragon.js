// Hidden on Interests: click the ring on The Lord of the Rings tile. A dragon flies in over moonlit
// mountains, hovers, rears back and breathes fire that lights the peaks, then does it again.
// The body is a chain of points that follows the head, so the neck and tail move like one animal;
// the fire is glowing particles that cool from white to orange to smoke. Reduced motion shows one still frame.
// eggs.js shows the button and loads this file the first time it's clicked.
(() => {
  const trigger = document.querySelector(".dragon-egg");
  if (!trigger) return;
  let dragon;
  (window.openEgg ||= {}).dragon = () => (dragon ||= build()).open();

  function build() {
    const W = 760, H = 500;
    const dialog = document.createElement("dialog");
    dialog.className = "pong dragon";
    dialog.setAttribute("aria-label", "A dragon breathing fire");
    dialog.innerHTML =
      '<div class="pong-head"><p class="pong-score">Over the Misty Mountains</p>' +
      '<button type="button" class="pong-close" aria-label="Close">×</button></div>' +
      '<canvas aria-label="Animated: a dragon flies in over moonlit mountains and breathes a stream of fire that lights the peaks"></canvas>' +
      '<div class="messi-foot"><p class="pong-help">Not all those who wander are lost, but some of them are dragons.</p>' +
      '<button type="button" class="messi-again">Again</button></div>';
    document.body.append(dialog);
    const canvas = dialog.querySelector("canvas"), ctx = canvas.getContext("2d");
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr; ctx.scale(dpr, dpr);
    const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const rand = (a, b) => a + Math.random() * (b - a);
    const norm = (x, y) => { const l = Math.hypot(x, y) || 1; return [x / l, y / l]; };

    // The land: three ridges of mountains, far to near, and a sky of stars
    const ridge = (base, amp, seed, step) => {
      const pts = []; let y = base;
      for (let x = -20; x <= W + 20; x += step) { y = base - amp * Math.abs(Math.sin(x * 0.011 + seed) * Math.sin(x * 0.0047 + seed * 2)) - rand(0, amp * 0.15); pts.push([x, y]); }
      return pts;
    };
    const RIDGES = [[ridge(330, 120, 1.3, 14), "#2a2440"], [ridge(390, 110, 4.1, 12), "#1d1830"], [ridge(450, 90, 2.2, 10), "#120f1f"]];
    const STARS = Array.from({ length: 140 }, () => [rand(0, W), rand(0, H * 0.55), rand(0.3, 1.2), rand(0, 6.28)]);

    // The dragon: a chain of 30 points behind the head, kept a fixed distance apart
    const N = 30, LINK = 11;
    let spine, fire, t0, frame, last;
    const thick = i => i < 6 ? 6 + i * 2.2 : i < 13 ? 19 - (i - 9) ** 2 * 0.35 : Math.max(1.4, 16 * (1 - (i - 13) / (N - 13)) ** 1.4);  // neck, chest, tapering tail

    function reset() {
      spine = Array.from({ length: N }, (_, i) => [W + 120 + i * LINK, 120 + i * 2]);
      fire = [];
    }
    // Where the head is at time t: a swoop in from the right, then a hover with a slow figure eight
    function headAt(t) {
      if (t < 3.2) { const k = t / 3.2, e = 1 - (1 - k) ** 3; return [W + 120 - (W + 120 - 470) * e, 120 + 70 * Math.sin(k * Math.PI) * 0.6 + 60 * e]; }
      const h = t - 3.2; return [470 + 18 * Math.sin(h * 0.7), 185 + 10 * Math.sin(h * 1.4)];
    }
    // Breathing: in 2.4 s bursts, every 5 s once it has arrived; just before each, the head rears back
    const breath = t => { if (t < 4.2) return { on: false, rear: 0 }; const c = (t - 4.2) % 5; return { on: c > 0.5 && c < 2.9, rear: c < 0.5 ? c / 0.5 : c < 2.9 ? 1 - Math.min(1, (c - 0.5) / 0.3) : 0 }; };

    function step(t, dt) {
      const b = breath(t);
      let [hx, hy] = headAt(t);
      hx += 22 * b.rear; hy -= 16 * b.rear;            // rearing back before the fire
      spine[0] = [hx, hy];
      for (let i = 1; i < N; i++) {
        const [px, py] = spine[i - 1];
        let [x, y] = spine[i];
        // the body trails behind and a little below, and the tail sways
        x += 0.9 + 0.02 * i; y += 0.25 + Math.sin(t * 2.2 - i * 0.35) * 0.18 * (i / N) * 6;
        const [dx, dy] = norm(x - px, y - py);
        spine[i] = [px + dx * LINK, py + dy * LINK];
      }
      // fire from the mouth, down and forward
      const [ux, uy] = norm(spine[0][0] - spine[2][0], spine[0][1] - spine[2][1]);
      const [fx, fy] = norm(ux * 0.45 - 0.55, uy * 0.45 + 0.4);   // mostly forward (left) and a little down
      if (b.on) for (let k = 0; k < 55; k++) {
        const sp = rand(230, 360), sx = fx + rand(-0.12, 0.12), sy = fy + rand(-0.12, 0.12);
        fire.push({ x: hx + ux * 38, y: hy + uy * 38 + 4, vx: sx * sp, vy: sy * sp, age: 0, life: rand(0.8, 1.35), ember: Math.random() < 0.04, seed: rand(0, 6.28) });
      }
      for (const p of fire) {
        p.age += dt; const k = p.age / p.life;
        p.vx *= 1 - 1.6 * dt; p.vy *= 1 - 1.6 * dt; p.vy -= (p.ember ? 40 : 90 * k) * dt;   // slows, and the hot gas rises
        p.vy += Math.sin(p.age * 18 + p.seed) * 140 * k * dt; p.vx += Math.cos(p.age * 13 + p.seed) * 60 * k * dt;   // and curls
        p.x += p.vx * dt; p.y += p.vy * dt;
      }
      fire = fire.filter(p => p.age < p.life * (p.ember ? 2.2 : 1));
      return b;
    }

    function drawWing(sh, fwd, up, phase, far, rim) {
      const back = [-fwd[0], -fwd[1]], lift = 0.55 + 0.45 * Math.sin(phase);   // from half raised to fully raised
      const at = (o, a, b) => [o[0] + back[0] * a + up[0] * b, o[1] + back[1] * a + up[1] * b];
      const elbow = at(sh, 10, 18 + 62 * lift), wrist = at(elbow, 36, 8 + 50 * lift);
      const tips = [at(wrist, 72, 34 * lift - 6), at(wrist, 100, 4 * lift - 10), at(wrist, 92, -34), at(wrist, 62, -66), at(wrist, 26, -86)];
      const root = spine[15];
      ctx.fillStyle = far ? "rgba(22,12,26,0.95)" : "#0c0710";
      ctx.beginPath(); ctx.moveTo(sh[0], sh[1]); ctx.lineTo(elbow[0], elbow[1]); ctx.lineTo(wrist[0], wrist[1]);
      let prev = wrist;
      for (const tip of tips) {   // the membrane scallops between the finger tips
        ctx.quadraticCurveTo((prev[0] + tip[0]) / 2 - up[0] * 8, (prev[1] + tip[1]) / 2 - up[1] * 8, tip[0], tip[1]);
        prev = tip;
      }
      ctx.quadraticCurveTo((prev[0] + root[0]) / 2 - up[0] * 14, (prev[1] + root[1]) / 2 - up[1] * 14, root[0], root[1]);
      ctx.closePath(); ctx.fill();
      if (rim > 0.02) { ctx.strokeStyle = `rgba(255,130,50,${0.5 * rim})`; ctx.lineWidth = 1.2; ctx.stroke(); }
      ctx.strokeStyle = far ? "#2a1a30" : "#2c1820"; ctx.lineWidth = 2.6; ctx.lineCap = "round";   // the bones
      ctx.beginPath(); ctx.moveTo(sh[0], sh[1]); ctx.lineTo(elbow[0], elbow[1]); ctx.lineTo(wrist[0], wrist[1]);
      for (const tip of tips.slice(0, 4)) { ctx.moveTo(wrist[0], wrist[1]); ctx.lineTo(tip[0], tip[1]); }
      ctx.stroke();
    }

    function draw(t, b) {
      const heat = Math.min(1, fire.length / 900);
      // sky, moon, stars
      const sky = ctx.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, "#090b1f"); sky.addColorStop(0.6, "#22183a"); sky.addColorStop(1, "#3b1f33");
      ctx.fillStyle = sky; ctx.fillRect(0, 0, W, H);
      for (const [x, y, r, p] of STARS) { ctx.fillStyle = `rgba(235,235,255,${0.35 + 0.35 * Math.sin(t * 1.3 + p)})`; ctx.fillRect(x, y, r, r); }
      const moon = ctx.createRadialGradient(130, 90, 0, 130, 90, 90);
      moon.addColorStop(0, "rgba(255,244,220,0.9)"); moon.addColorStop(0.3, "rgba(255,244,220,0.25)"); moon.addColorStop(1, "rgba(255,244,220,0)");
      ctx.fillStyle = moon; ctx.beginPath(); ctx.arc(130, 90, 90, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#f6ecd6"; ctx.beginPath(); ctx.arc(130, 90, 26, 0, Math.PI * 2); ctx.fill();
      // the mountains, far to near, warmed by the fire
      RIDGES.forEach(([pts, col], i) => {
        ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(-20, H);
        for (const [x, y] of pts) ctx.lineTo(x, y);
        ctx.lineTo(W + 20, H); ctx.closePath(); ctx.fill();
        if (heat > 0.02) { ctx.globalCompositeOperation = "lighter"; ctx.fillStyle = `rgba(255,110,40,${0.10 * heat * (3 - i) / 3})`; ctx.fill(); ctx.globalCompositeOperation = "source-over"; }
      });
      // the dragon: far wing, body, near wing, head
      const sh = spine[7], [fx, fy] = norm(spine[5][0] - spine[9][0], spine[5][1] - spine[9][1]), up = [fy, -fx];
      const upv = up[1] > 0 ? [-up[0], -up[1]] : up;                      // wings always rise upwards on screen
      const phase = t * (t < 3.2 ? 7 : 4.4);
      const rim = heat;
      drawWing(sh, [fx, fy], upv, phase + 0.5, true, rim);
      const L = [], R = [];
      for (let i = 0; i < N; i++) {
        const a = spine[Math.max(0, i - 1)], c = spine[Math.min(N - 1, i + 1)], [dx, dy] = norm(c[0] - a[0], c[1] - a[1]), w = thick(i);
        L.push([spine[i][0] - dy * w, spine[i][1] + dx * w]); R.push([spine[i][0] + dy * w, spine[i][1] - dx * w]);
      }
      ctx.fillStyle = "#0c0710"; ctx.beginPath(); ctx.moveTo(L[0][0], L[0][1]);
      for (const p of L) ctx.lineTo(p[0], p[1]);
      for (const p of R.reverse()) ctx.lineTo(p[0], p[1]);
      ctx.closePath(); ctx.fill();
      if (rim > 0.02) { ctx.strokeStyle = `rgba(255,140,60,${0.55 * rim})`; ctx.lineWidth = 1.4; ctx.stroke(); }   // lit by its own fire
      ctx.fillStyle = "#0c0710";                                           // spines along the back
      for (let i = 3; i < N - 4; i += 2) { const p = R[R.length - 1 - i]; ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(p[0] + upv[0] * 7, p[1] + upv[1] * 7); ctx.lineTo(p[0] + 5, p[1]); ctx.fill(); }
      drawWing(sh, [fx, fy], upv, phase, false, rim);
      // head and jaw, opening while it breathes
      const [hx, hy] = spine[0], [ux, uy] = norm(hx - spine[2][0], hy - spine[2][1]), nx = -uy, ny = ux;
      const open = b.on ? 0.45 : 0.06, side = ny > 0 ? 1 : -1;
      const snout = [hx + ux * 40, hy + uy * 40];
      ctx.fillStyle = "#0c0710"; ctx.beginPath();
      ctx.moveTo(hx - nx * 12 * side, hy - ny * 12 * side); ctx.lineTo(snout[0] - nx * 3 * side, snout[1] - ny * 3 * side);
      ctx.lineTo(hx + ux * 32 + nx * 3 * side, hy + uy * 32 + ny * 3 * side); ctx.lineTo(hx + nx * 8 * side, hy + ny * 8 * side); ctx.closePath(); ctx.fill();
      const ja = Math.atan2(uy, ux) + open * side, jaw = [hx + Math.cos(ja) * 34, hy + Math.sin(ja) * 34];
      ctx.beginPath(); ctx.moveTo(hx, hy + 3); ctx.lineTo(jaw[0], jaw[1]); ctx.lineTo(hx + ux * 6 + nx * 7 * side, hy + uy * 6 + ny * 7 * side); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = "#0c0710"; ctx.lineWidth = 3.5; ctx.lineCap = "round";   // horns
      ctx.beginPath(); ctx.moveTo(hx - ux * 2 - nx * 9 * side, hy - uy * 2 - ny * 9 * side); ctx.lineTo(hx - ux * 24 - nx * 22 * side, hy - uy * 24 - ny * 22 * side);
      ctx.moveTo(hx + ux * 4 - nx * 10 * side, hy + uy * 4 - ny * 10 * side); ctx.lineTo(hx - ux * 12 - nx * 24 * side, hy - uy * 12 - ny * 24 * side); ctx.stroke();
      ctx.fillStyle = "#ffcf6a"; ctx.beginPath(); ctx.arc(hx + ux * 15 - nx * 5 * side, hy + uy * 15 - ny * 5 * side, 2.4, 0, Math.PI * 2); ctx.fill();
      // the fire: white at the mouth, cooling through gold and orange to red, then smoke
      for (const p of fire) {
        const k = p.age / p.life;
        if (k > 0.72 && !p.ember) { ctx.fillStyle = `rgba(60,50,55,${0.12 * (1 - (k - 0.72) / 0.28)})`; ctx.beginPath(); ctx.arc(p.x, p.y, 10 + 30 * k, 0, Math.PI * 2); ctx.fill(); }
      }
      ctx.globalCompositeOperation = "lighter";
      for (const p of fire) {
        const k = p.age / p.life;
        if (p.ember) { ctx.fillStyle = `rgba(255,180,80,${Math.max(0, 0.9 - k * 0.4)})`; ctx.fillRect(p.x, p.y, 1.6, 1.6); continue; }
        if (k > 0.72) continue;
        const rgb = k < 0.12 ? "255,248,220" : k < 0.35 ? "255,205,90" : k < 0.55 ? "255,140,40" : "220,60,25";
        const r = 3 + 26 * k, a = (k < 0.12 ? 0.5 : 0.32) * (1 - k * 0.6);
        const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r);
        g.addColorStop(0, `rgba(${rgb},${a})`); g.addColorStop(1, `rgba(${rgb},0)`);
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2); ctx.fill();
      }
      if (heat > 0.02) {                                                   // the glow it throws on everything near
        const g = ctx.createRadialGradient(hx + fx * 0 - 120, hy + 140, 0, hx - 120, hy + 140, 320);
        g.addColorStop(0, `rgba(255,120,40,${0.22 * heat})`); g.addColorStop(1, "rgba(255,120,40,0)");
        ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      }
      ctx.globalCompositeOperation = "source-over";
    }

    function tick(now) {
      const t = (now - t0) / 1000, dt = Math.min(0.05, last == null ? 0.016 : (now - last) / 1000);
      last = now;
      draw(t, step(t, dt));
      frame = requestAnimationFrame(tick);
    }
    function start() {
      cancelAnimationFrame(frame); reset(); last = null;
      if (still) { let b; for (let t = 0; t < 5.6; t += 1 / 60) b = step(t, 1 / 60); return draw(5.6, b); }
      t0 = performance.now(); frame = requestAnimationFrame(tick);
    }
    dialog.querySelector(".pong-close").addEventListener("click", () => dialog.close());
    dialog.querySelector(".messi-again").addEventListener("click", start);
    dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", () => { cancelAnimationFrame(frame); trigger.focus(); });
    return { open() { dialog.showModal(); start(); } };
  }
})();
