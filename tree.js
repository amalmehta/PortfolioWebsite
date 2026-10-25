// Hidden on What I live by: click "Understand from first principles…" for a tree that grows from
// one trunk and splits, again and again, into branches that all grow at the same time: one path
// becoming many concurrent ones. The trunk goes straight; every branch after it bends through a
// tanh, the way an activation function bends a network's straight lines. Each regrow is a new tree.
// eggs.js shows the button and loads this file the first time it's clicked.
(() => {
  const trigger = document.querySelector(".tree-egg");
  if (!trigger) return;
  let tree;
  (window.openEgg ||= {}).tree = () => (tree ||= build()).open();

  function build() {
    const W = 640, H = 480;
    const dialog = document.createElement("dialog");
    dialog.className = "pong tree";
    dialog.setAttribute("aria-label", "A branching tree");
    dialog.innerHTML =
      '<div class="pong-head"><p class="pong-score">One path, many</p>' +
      '<button type="button" class="pong-close" aria-label="Close">×</button></div>' +
      '<canvas aria-label="Animated drawing: a single trunk grows and splits into branches that all keep growing at once"></canvas>' +
      '<div class="messi-foot"><p class="pong-help">Go straight, then bend: each split passes through a tanh, like an activation function, and that’s what lets one path become many, all growing at once.</p>' +
      '<button type="button" class="messi-again">Grow another</button></div>';
    document.body.append(dialog);
    const canvas = dialog.querySelector("canvas"), ctx = canvas.getContext("2d");
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr; ctx.scale(dpr, dpr);
    const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

    // A small seeded random, so each tree is its own shape but stays the same while it grows.
    const rand = seed => () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32);
    const GROW = 0.55, DEPTH = 8;  // seconds per branch; levels of splitting

    // Every branch starts the moment its parent finishes, so all branches of a level grow together.
    function grow(seed) {
      const r = rand(seed), out = [];
      (function branch(x, y, angle, len, width, depth, start) {
        const x2 = x + Math.cos(angle) * len, y2 = y + Math.sin(angle) * len;
        // Straight trunk; each branch after it bends sideways by tanh of a random pre-activation.
        const bend = depth ? Math.tanh((r() - 0.5) * 4) * len * 0.35 : 0;
        const cx = (x + x2) / 2 - Math.sin(angle) * bend, cy = (y + y2) / 2 + Math.cos(angle) * bend;
        out.push({ x, y, x2, y2, cx, cy, width, depth, start });
        if (depth === DEPTH) return;
        const kids = depth < 2 ? 2 : r() < 0.35 ? 3 : 2;
        const spread = 0.42 + r() * 0.3;
        for (let k = 0; k < kids; k++) {
          const a = angle + (kids === 1 ? 0 : (k / (kids - 1) - 0.5) * 2 * spread) + (r() - 0.5) * 0.25;
          branch(x2, y2, a, len * (0.68 + r() * 0.12), width * 0.68, depth + 1, start + GROW);
        }
      })(W / 2, H - 14, -Math.PI / 2 + (r() - 0.5) * 0.1, 104, 13, 0, 0);
      return out;
    }

    let branches, t0, frame;
    const colours = () => {
      const s = getComputedStyle(document.documentElement);
      return { wood: s.getPropertyValue("--text").trim() || "#1c1b19", leaf: s.getPropertyValue("--accent").trim() || "#2f6fb0",
               bloom: s.getPropertyValue("--warm").trim() || "#b5562f", ground: s.getPropertyValue("--line").trim() || "#ddd" };
    };

    function draw(t) {
      const c = colours();
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = c.ground;
      ctx.fillRect(W / 2 - 120, H - 14, 240, 2);
      ctx.lineCap = "round";
      for (const b of branches) {
        const p = Math.min(Math.max((t - b.start) / GROW, 0), 1);
        if (!p) continue;
        const e = 1 - (1 - p) ** 2;  // ease out
        ctx.strokeStyle = c.wood;
        ctx.globalAlpha = 0.55 + 0.45 * (1 - b.depth / DEPTH);
        ctx.lineWidth = Math.max(b.width, 0.8);
        // The first e of the curve from (x, y) through control (cx, cy) to (x2, y2), split by de Casteljau.
        const ax = b.x + (b.cx - b.x) * e, ay = b.y + (b.cy - b.y) * e;
        const bx = b.cx + (b.x2 - b.cx) * e, by = b.cy + (b.y2 - b.cy) * e;
        ctx.beginPath();
        ctx.moveTo(b.x, b.y);
        ctx.quadraticCurveTo(ax, ay, ax + (bx - ax) * e, ay + (by - ay) * e);
        ctx.stroke();
        if (b.depth === DEPTH && p === 1) {  // a bud on every tip once it's done
          ctx.globalAlpha = 0.85;
          ctx.fillStyle = (b.x2 * 7 + b.y2 * 3) % 5 < 1 ? c.bloom : c.leaf;
          ctx.beginPath();
          ctx.arc(b.x2, b.y2, 3.2, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      ctx.globalAlpha = 1;
    }

    const end = () => (DEPTH + 1) * GROW + 0.1;
    function tick(now) {
      const t = (now - t0) / 1000;
      draw(t);
      if (t < end()) frame = requestAnimationFrame(tick);
    }
    function start() {
      cancelAnimationFrame(frame);
      branches = grow((Math.random() * 2 ** 32) >>> 0);
      if (still) return draw(end());
      t0 = performance.now();
      frame = requestAnimationFrame(tick);
    }

    dialog.querySelector(".pong-close").addEventListener("click", () => dialog.close());
    dialog.querySelector(".messi-again").addEventListener("click", start);
    dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); });  // click outside closes
    dialog.addEventListener("close", () => { cancelAnimationFrame(frame); trigger.focus(); });
    return { open() { dialog.showModal(); start(); } };
  }
})();
