// Profile: a faint five-pass ridge along the bottom of the intro, and a few dots learning to cross it.
// Each dot is a plan: how hard to push on each stretch of the ridge. Gravity slows them on the climbs
// and pushing costs energy. After every round the best few plans become the starting point for the
// next (the cross-entropy method), so the group gets further the longer you watch. Once they cross
// reliably, it starts again from nothing. Pauses off screen; reduced motion shows just the ridge.
(() => {
  const hero = document.querySelector(".hero");
  if (!hero) return;
  const canvas = document.createElement("canvas");
  canvas.className = "hero-ridge";
  canvas.setAttribute("aria-hidden", "true");
  hero.prepend(canvas);
  const ctx = canvas.getContext("2d");
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // The ridge: five passes, the same profile as the Outside work divider. x and height run 0..1.
  const PEAKS = [[0.12, 0.45], [0.3, 0.75], [0.49, 0.55], [0.68, 1], [0.87, 0.65]];
  const raw = x => PEAKS.reduce((s, [c, h]) => s + h * Math.exp(-Math.abs(x - c) / 0.05), 0);
  const top = Math.max(...Array.from({ length: 400 }, (_, i) => raw(i / 400)));
  const height = x => raw(x) / top;
  const slope = x => (height(x + 0.001) - height(x - 0.001)) / 0.002;

  const SEGMENTS = 12, POP = 14, ELITE = 3, DT = 1 / 240, GRAVITY = 0.25, PUSH = 1, DRAG = 0.6;  // tuned offline: about 40–70 rounds to cross
  let mean, spread, gen, plans, runners, best, wins, frame, w = 0, h = 0, visible = true, resting = false;

  function reset() {
    mean = new Array(SEGMENTS).fill(0.1); spread = new Array(SEGMENTS).fill(0.35);
    gen = 0; best = 0; wins = 0; round();
  }
  function round() {
    gen++;
    plans = Array.from({ length: POP }, () => mean.map((m, i) => Math.min(1, Math.max(0, m + spread[i] * gauss()))));
    runners = plans.map(() => ({ x: 0.005, v: 0.18, far: 0, energy: 0, steps: 0, done: false }));
  }
  function gauss() { let u = 0, v = 0; while (!u) u = Math.random(); while (!v) v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

  // One physics step for one runner: push from its plan, gravity along the slope, a little drag.
  function step(r, plan) {
    if (r.done) return;
    const push = plan[Math.min(SEGMENTS - 1, Math.floor(r.x * SEGMENTS))];
    r.energy += push * DT;
    r.v += (PUSH * push - GRAVITY * slope(r.x) - DRAG * r.v) * DT;
    r.x += r.v * DT;
    r.far = Math.max(r.far, r.x);
    if (r.x >= 0.995) { r.done = true; r.crossed = true; }
    else if (r.v <= 0.01 || r.x <= 0 || ++r.steps > 4000) r.done = true;   // stalled on a climb
  }
  function score(r) { return r.far + (r.crossed ? 1 : 0) - 0.05 * r.energy; }

  function learn() {
    const ranked = runners.map((r, i) => [score(r), i]).sort((a, b) => b[0] - a[0]).slice(0, ELITE).map(([, i]) => plans[i]);
    mean = mean.map((_, k) => ranked.reduce((s, p) => s + p[k], 0) / ELITE);
    spread = spread.map((_, k) => Math.max(0.02, Math.sqrt(ranked.reduce((s, p) => s + (p[k] - mean[k]) ** 2, 0) / ELITE) * 0.9 + 0.01));
    best = Math.max(best, ...runners.map(r => Math.min(r.far, 1)));
    wins = runners.filter(r => r.crossed).length >= POP / 2 ? wins + 1 : 0;
    if (wins >= 3) { resting = true; setTimeout(() => { resting = false; reset(); }, 2500); }  // a pause on success, then again from nothing
    else round();
  }

  const px = x => x * w, py = x => h - 6 - height(x) * (h - 26);
  function draw() {
    const s = getComputedStyle(document.documentElement);
    const line = s.getPropertyValue("--warm").trim(), dot = s.getPropertyValue("--accent").trim(), faint = s.getPropertyValue("--faint").trim();
    ctx.clearRect(0, 0, w, h);
    ctx.globalAlpha = 0.5; ctx.strokeStyle = line; ctx.lineWidth = 1.5; ctx.beginPath();
    for (let i = 0; i <= 300; i++) { const x = i / 300; ctx[i ? "lineTo" : "moveTo"](px(x), py(x)); }
    ctx.stroke();
    if (still || !runners) return;
    for (const r of runners) {
      ctx.globalAlpha = r.crossed ? 0.9 : r.done ? 0.25 : 0.7;
      ctx.fillStyle = r.crossed ? line : dot;
      ctx.beginPath(); ctx.arc(px(Math.min(r.x, 1)), py(Math.min(r.x, 1)) - 4, 3, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 0.7; ctx.fillStyle = faint; ctx.font = "11px " + s.getPropertyValue("--sans"); ctx.textAlign = "right";
    ctx.fillText(`learning to cross · round ${gen} · furthest ${Math.round(best * 100)}%`, w - 4, h - 4);
    ctx.globalAlpha = 1;
  }

  function tick() {
    if (!resting) {
      for (let k = 0; k < 6; k++) runners.forEach((r, i) => step(r, plans[i]));
      if (runners.every(r => r.done)) learn();
    }
    draw();
    frame = visible && !document.hidden ? requestAnimationFrame(tick) : null;
  }
  function resize() {
    const dpr = Math.min(devicePixelRatio || 1, 2), box = canvas.getBoundingClientRect();
    w = box.width; h = box.height; canvas.width = w * dpr; canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); draw();
  }
  const go = () => { if (!still && !frame && visible && !document.hidden) frame = requestAnimationFrame(tick); };
  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; go(); }).observe(hero);
  document.addEventListener("visibilitychange", go);
  reset(); resize(); go();
})();
