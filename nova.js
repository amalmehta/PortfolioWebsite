// Hidden on the profile: click the star by "North star" for a supernova. A star swells and reddens,
// collapses, flashes white, and a shockwave throws out glowing gas that slows into a nebula around a
// spinning pulsar. Drawn on a canvas with additive light; reduced motion shows the finished nebula.
// eggs.js shows the button and loads this file the first time it's clicked.
(() => {
  const trigger = document.querySelector(".nova-egg");
  if (!trigger) return;
  let nova;
  (window.openEgg ||= {}).nova = () => (nova ||= build()).open();

  function build() {
    const W = 760, H = 500, CX = W / 2, CY = H / 2;
    const dialog = document.createElement("dialog");
    dialog.className = "pong nova";
    dialog.setAttribute("aria-label", "A supernova");
    dialog.innerHTML =
      '<div class="pong-head"><p class="pong-score">North star</p>' +
      '<button type="button" class="pong-close" aria-label="Close">×</button></div>' +
      '<canvas aria-label="Animated: a star swells, collapses and explodes, leaving a glowing nebula around a spinning pulsar"></canvas>' +
      '<div class="messi-foot"><p class="pong-help">Even the brightest stars burn out. When the biggest ones do, they make the elements everything else is built from.</p>' +
      '<button type="button" class="messi-again">Again</button></div>';
    document.body.append(dialog);
    const canvas = dialog.querySelector("canvas"), ctx = canvas.getContext("2d");
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr; ctx.scale(dpr, dpr);
    const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const rand = (a, b) => a + Math.random() * (b - a);

    // A sky of faint stars, a little blue and a little gold
    const sky = Array.from({ length: 260 }, () => ({ x: rand(0, W), y: rand(0, H), r: rand(0.3, 1.3), a: rand(0.2, 0.9), t: rand(0, 6.28),
      c: Math.random() < 0.15 ? "255,210,160" : Math.random() < 0.3 ? "170,200,255" : "235,240,255" }));
    // The ejecta, as in a real remnant: a lumpy shell of red-orange filaments outside, a hot blue glow within.
    // Drawn into a quarter-size canvas and scaled up, so the gas reads as glowing fog, with a few sharp specks.
    const OUTER = ["255,120,70", "255,90,110", "255,170,90", "240,80,150"], INNER = ["140,180,255", "190,210,255", "120,230,255", "200,150,255"];
    const fog = document.createElement("canvas"), F = 3;
    fog.width = W / F; fog.height = H / F;
    const fctx = fog.getContext("2d");
    let gas, t0, frame;
    function seed() {
      // A different lumpy outline every time: a few sine waves of random frequency and phase around the circle
      const waves = Array.from({ length: 5 }, () => [Math.floor(rand(2, 10)), rand(0, 6.28), rand(0.04, 0.12)]);
      const lump = a => waves.reduce((s, [k, p, amp]) => s + amp * Math.sin(k * a + p), 0);
      gas = Array.from({ length: 3200 }, () => {
        const a = rand(0, Math.PI * 2), outer = Math.random() < 0.45;
        // filaments in a thin outer shell; the blue glow fills the inside, thinning towards the middle
        const shell = outer ? rand(0.78, 1.02) : Math.pow(rand(0.02, 1), 0.6) * 0.78;
        const pool = outer ? OUTER : INNER;
        return { a, s: 200 * shell * (1 + lump(a)), outer, len: outer ? rand(4, 16) : 0, size: outer ? rand(0.5, 1.3) : rand(1, 2.6),
                 c: pool[Math.floor(Math.random() * pool.length)], wob: rand(-0.2, 0.2), life: rand(0.4, 1), speck: Math.random() < 0.08 };
      });
    }

    const glow = (x, y, r, rgb, alpha) => {
      const g = ctx.createRadialGradient(x, y, 0, x, y, r);
      g.addColorStop(0, `rgba(${rgb},${alpha})`); g.addColorStop(1, `rgba(${rgb},0)`);
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
    };

    // Timeline, in seconds: 0–2.6 the star swells and reddens; 2.6–3.3 it collapses;
    // 3.3 the flash; then the shockwave and the gas spread and slow; from ~6 s the nebula glows on.
    function draw(t) {
      ctx.globalCompositeOperation = "source-over";
      ctx.fillStyle = "#04050c"; ctx.fillRect(0, 0, W, H);
      ctx.globalCompositeOperation = "lighter";
      for (const s of sky) {
        ctx.fillStyle = `rgba(${s.c},${s.a * (0.6 + 0.4 * Math.sin(t * 1.5 + s.t))})`;
        ctx.fillRect(s.x, s.y, s.r, s.r);
      }
      if (t < 2.6) {                       // a red supergiant, swelling and pulsing
        const k = t / 2.6, r = 10 + 26 * k + Math.sin(t * 9) * 1.5 * k;
        const rgb = k < 0.5 ? "255,230,190" : "255,170,110";
        glow(CX, CY, r * 5, rgb, 0.25); glow(CX, CY, r * 2, rgb, 0.6); glow(CX, CY, r, "255,250,235", 0.95);
      } else if (t < 3.3) {                // collapse: it falls in on itself and flickers
        const k = (t - 2.6) / 0.7, r = 36 * (1 - k) ** 2 + 3;
        glow(CX, CY, r * 4, "255,140,90", 0.35 * (1 - k)); glow(CX, CY, r, "255,255,255", 0.9 + 0.1 * Math.sin(t * 60));
      } else {
        const e = t - 3.3;
        if (e < 1.2) {                     // the flash
          const f = 1 - e / 1.2;
          glow(CX, CY, 420 * (1 - f * 0.5), "255,255,255", 0.9 * f * f);
          glow(CX, CY, 160, "200,220,255", 0.8 * f);
        }
        const ring = 40 + 380 * (1 - Math.exp(-e * 0.9));   // the shockwave, fast then slowing
        ctx.strokeStyle = `rgba(170,200,255,${Math.max(0, 0.55 * Math.exp(-e * 0.6))})`;
        ctx.lineWidth = 3 * Math.exp(-e * 0.3) + 0.5;
        ctx.beginPath(); ctx.arc(CX, CY, ring, 0, Math.PI * 2); ctx.stroke();
        const spread = 1 - Math.exp(-e * 0.7);              // the gas, decelerating into the nebula
        fctx.globalCompositeOperation = "source-over"; fctx.clearRect(0, 0, fog.width, fog.height);
        fctx.globalCompositeOperation = "lighter";
        for (const g of gas) {
          const d = g.s * spread, a = g.a + g.wob * spread * 0.3;
          const x = CX + Math.cos(a) * d, y = CY + Math.sin(a) * d * 0.82;
          const fade = Math.min(1, e * 2) * (0.35 + 0.65 * g.life) * (e > 6 ? 0.88 + 0.12 * Math.sin(t * 0.7 + g.a * 5) : 1);
          if (g.outer) {                     // a filament: a short streak pointing outwards
            const l = g.len * (0.4 + spread);
            fctx.strokeStyle = `rgba(${g.c},${0.16 * fade})`; fctx.lineWidth = (g.size * (1 + spread)) / F + 0.4;
            fctx.beginPath(); fctx.moveTo(x / F, y / F); fctx.lineTo((x + Math.cos(a) * l) / F, (y + Math.sin(a) * l * 0.82) / F); fctx.stroke();
          } else {
            fctx.fillStyle = `rgba(${g.c},${0.07 * fade})`;
            fctx.beginPath(); fctx.arc(x / F, y / F, (g.size * (1 + 2 * spread)) / F + 0.5, 0, Math.PI * 2); fctx.fill();
          }
          if (g.speck) { ctx.fillStyle = `rgba(255,240,230,${0.55 * fade})`; ctx.fillRect(x, y, 1.2, 1.2); }
        }
        ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = "high";
        ctx.drawImage(fog, 0, 0, W, H); ctx.drawImage(fog, -2, -2, W + 4, H + 4);   // twice, slightly apart, for a softer bloom
        glow(CX, CY, 190 * spread + 20, "120,160,255", 0.12 * spread);      // the nebula's soft blue heart
        glow(CX, CY, 260 * spread + 20, "120,140,255", 0.08 * spread);
        // What's left: a pulsar, spinning, with two beams sweeping round
        const spin = t * 2.4, beam = 160 + 60 * spread;
        for (const side of [0, Math.PI]) {
          const a = spin + side, g2 = ctx.createLinearGradient(CX, CY, CX + Math.cos(a) * beam, CY + Math.sin(a) * beam);
          g2.addColorStop(0, `rgba(190,220,255,${0.5 * spread})`); g2.addColorStop(1, "rgba(190,220,255,0)");
          ctx.strokeStyle = g2; ctx.lineWidth = 2.2;
          ctx.beginPath(); ctx.moveTo(CX, CY); ctx.lineTo(CX + Math.cos(a) * beam, CY + Math.sin(a) * beam); ctx.stroke();
        }
        glow(CX, CY, 14, "220,235,255", 0.9 * Math.min(1, e)); glow(CX, CY, 3, "255,255,255", 1);
      }
      ctx.globalCompositeOperation = "source-over";
    }

    function tick(now) { draw((now - t0) / 1000); frame = requestAnimationFrame(tick); }
    function start() {
      cancelAnimationFrame(frame); seed();
      if (still) return draw(14);
      t0 = performance.now(); frame = requestAnimationFrame(tick);
    }
    dialog.querySelector(".pong-close").addEventListener("click", () => dialog.close());
    dialog.querySelector(".messi-again").addEventListener("click", start);
    dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", () => { cancelAnimationFrame(frame); trigger.focus(); });
    return { open() { dialog.showModal(); start(); } };
  }
})();
