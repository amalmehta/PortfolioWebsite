// Hidden on Interests: click "Building worlds" for a fictional world, generated on the spot:
// an island from layered noise, rivers that run downhill to the sea, and a few named places.
// Every "Make another" is a new world.
// eggs.js shows the button and loads this file the first time it's clicked.
(() => {
  const trigger = document.querySelector(".world-egg");
  if (!trigger) return;
  let world;
  (window.openEgg ||= {}).world = () => (world ||= build()).open();

  function build() {
    const W = 640, H = 440, R = 4, GW = W / R, GH = H / R;  // drawn in 4 px cells
    const dialog = document.createElement("dialog");
    dialog.className = "pong world";
    dialog.setAttribute("aria-label", "A generated fictional world");
    dialog.innerHTML =
      '<div class="pong-head"><p class="pong-score"></p>' +
      '<button type="button" class="pong-close" aria-label="Close">×</button></div>' +
      '<canvas aria-label="A map of a generated island with mountains, forests, rivers and named places"></canvas>' +
      '<div class="messi-foot"><p class="pong-help">A world made just now: layered noise for the land, rivers that run downhill, and names from a handful of syllables.</p>' +
      '<button type="button" class="messi-again">Make another</button></div>';
    document.body.append(dialog);
    const canvas = dialog.querySelector("canvas"), ctx = canvas.getContext("2d"), title = dialog.querySelector(".pong-score");
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr; ctx.scale(dpr, dpr);

    const rand = seed => () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32);

    // Value noise: random values on a coarse lattice, smoothly blended, several octaves summed.
    function noise(r) {
      const N = 64, lattice = Array.from({ length: N * N }, r);
      const at = (i, j) => lattice[((j % N + N) % N) * N + ((i % N + N) % N)];
      const fade = t => t * t * (3 - 2 * t);
      const one = (x, y) => {
        const i = Math.floor(x), j = Math.floor(y), u = fade(x - i), v = fade(y - j);
        const a = at(i, j) + (at(i + 1, j) - at(i, j)) * u, b = at(i, j + 1) + (at(i + 1, j + 1) - at(i, j + 1)) * u;
        return a + (b - a) * v;
      };
      return (x, y) => { let s = 0, amp = 1, f = 1, norm = 0; for (let o = 0; o < 5; o++) { s += amp * one(x * f, y * f); norm += amp; amp *= 0.5; f *= 2; } return s / norm; };
    }

    const SYL = ["ar", "el", "dor", "mi", "ka", "thas", "ven", "ri", "osh", "lun", "ta", "bri", "mor", "sel", "qua", "ny", "ost", "fen"];
    const name = (r, n) => { let s = ""; for (let i = 0; i < n; i++) s += SYL[Math.floor(r() * SYL.length)]; return s[0].toUpperCase() + s.slice(1); };

    function make(seed) {
      const r = rand(seed), n = noise(r), h = new Float32Array(GW * GH);
      const ox = r() * 50, oy = r() * 50;
      for (let y = 0; y < GH; y++) for (let x = 0; x < GW; x++) {
        const dx = (x / GW - 0.5) * 2, dy = (y / GH - 0.5) * 2;
        const edge = Math.hypot(dx * 0.9, dy * 1.05);  // an island: land falls away towards the edges
        h[y * GW + x] = n(ox + x / 22, oy + y / 22) * 1.25 - edge * 0.55;
      }
      const SEA = 0.34, at = (x, y) => h[y * GW + x];
      const s = getComputedStyle(document.documentElement);
      const ink = s.getPropertyValue("--text").trim(), surface = s.getPropertyValue("--surface").trim();
      const colour = v => v < SEA - 0.08 ? "#3d6f9e" : v < SEA ? "#5c93c2" : v < SEA + 0.03 ? "#e6d6a8"
        : v < SEA + 0.09 ? "#8fbf72" : v < SEA + 0.2 ? "#5f9a5a" : v < SEA + 0.29 ? "#8a8070" : "#f2f0ea";
      for (let y = 0; y < GH; y++) for (let x = 0; x < GW; x++) { ctx.fillStyle = colour(at(x, y)); ctx.fillRect(x * R, y * R, R, R); }

      // Rivers: from high ground, step to the lowest neighbour until reaching the sea.
      ctx.strokeStyle = "#5c93c2"; ctx.lineWidth = 2.2; ctx.lineJoin = ctx.lineCap = "round";
      for (let k = 0, made = 0; k < 400 && made < 5; k++) {
        let x = 2 + Math.floor(r() * (GW - 4)), y = 2 + Math.floor(r() * (GH - 4));
        if (at(x, y) < SEA + 0.17) continue;
        const pts = [[x, y]];
        for (let i = 0; i < 300 && at(x, y) >= SEA; i++) {
          let bx = x, by = y;
          for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]) {
            const nx = x + dx, ny = y + dy;
            if (nx > 0 && ny > 0 && nx < GW - 1 && ny < GH - 1 && at(nx, ny) < at(bx, by)) { bx = nx; by = ny; }
          }
          if (bx === x && by === y) h[y * GW + x] -= 0.002; else { x = bx; y = by; pts.push([x, y]); }  // carve out of pits
        }
        if (pts.length < 12 || at(x, y) >= SEA) continue;
        made++;
        ctx.beginPath();
        pts.forEach(([px, py], i) => ctx[i ? "lineTo" : "moveTo"](px * R + R / 2, py * R + R / 2));
        ctx.stroke();
      }

      // Places on the lowlands, spaced apart, each with a name.
      ctx.font = "600 12px " + s.getPropertyValue("--sans");
      const places = [];
      for (let k = 0; k < 2000 && places.length < 6; k++) {
        const x = 4 + Math.floor(r() * (GW - 8)), y = 4 + Math.floor(r() * (GH - 8)), v = at(x, y);
        if (v < SEA + 0.03 || v > SEA + 0.15 || places.some(([px, py]) => Math.hypot(px - x, py - y) < 26)) continue;
        places.push([x, y]);
        const cx = x * R, cy = y * R, label = name(r, 2 + (r() < 0.4));
        ctx.fillStyle = ink; ctx.beginPath(); ctx.arc(cx, cy, 3.5, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = surface; ctx.globalAlpha = 0.8;
        const w = ctx.measureText(label).width, lx = Math.min(Math.max(cx + 7, 4), W - w - 6);
        ctx.fillRect(lx - 3, cy - 9, w + 6, 16);
        ctx.globalAlpha = 1; ctx.fillStyle = ink; ctx.fillText(label, lx, cy + 3);
      }
      title.textContent = `The world of ${name(r, 3)}`;
    }

    const again = () => make((Math.random() * 2 ** 32) >>> 0);
    dialog.querySelector(".pong-close").addEventListener("click", () => dialog.close());
    dialog.querySelector(".messi-again").addEventListener("click", again);
    dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", () => trigger.focus());
    return { open() { dialog.showModal(); again(); } };
  }
})();
