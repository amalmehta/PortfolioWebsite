// Hidden on Things I'm thinking about: click "many agents" in the first question for a swarm.
// Each agent only sees its neighbours and follows four local rules (keep apart, match their
// heading, stay close, head for the shared goal). Nobody is in charge; the group still gets there.
// Click the field to move the goal. eggs.js shows the button and loads this file on the first click.
(() => {
  const trigger = document.querySelector(".swarm-egg");
  if (!trigger) return;
  let swarm;
  (window.openEgg ||= {}).swarm = () => (swarm ||= build()).open();

  function build() {
    const W = 640, H = 420, N = 90, SEE = 46, APART = 16, SPEED = 2.4;
    const dialog = document.createElement("dialog");
    dialog.className = "pong swarm";
    dialog.setAttribute("aria-label", "A swarm of agents reaching a shared goal");
    dialog.innerHTML =
      '<div class="pong-head"><p class="pong-score">Goals reached: 0</p>' +
      '<button type="button" class="pong-close" aria-label="Close">×</button></div>' +
      '<canvas aria-label="Animated: dozens of small agents flock together and reach a goal, then the goal moves"></canvas>' +
      '<div class="messi-foot"><p class="pong-help">Each agent sees only its neighbours: keep apart, match their heading, stay close, head for the goal. Nobody is in charge. Click to move the goal.</p>' +
      '<button type="button" class="messi-again">Scatter</button></div>';
    document.body.append(dialog);
    const canvas = dialog.querySelector("canvas"), ctx = canvas.getContext("2d"), score = dialog.querySelector(".pong-score");
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr; ctx.scale(dpr, dpr);
    const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

    let agents, goal, reached = 0, frame;
    const newGoal = () => ({ x: 60 + Math.random() * (W - 120), y: 50 + Math.random() * (H - 100) });
    function scatter() {
      agents = Array.from({ length: N }, () => {
        const a = Math.random() * Math.PI * 2;
        return { x: Math.random() * W, y: Math.random() * H, vx: Math.cos(a) * SPEED, vy: Math.sin(a) * SPEED };
      });
      goal = newGoal();
    }

    function step() {
      let near = 0;
      for (const a of agents) {
        let sx = 0, sy = 0, ax = 0, ay = 0, cx = 0, cy = 0, n = 0;
        for (const b of agents) {
          if (a === b) continue;
          const dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy);
          if (d > SEE) continue;
          n++; ax += b.vx; ay += b.vy; cx += dx; cy += dy;
          if (d < APART && d > 0) { sx -= dx / d * (APART - d); sy -= dy / d * (APART - d); }
        }
        const gx = goal.x - a.x, gy = goal.y - a.y, gd = Math.hypot(gx, gy) || 1;
        if (gd < 40) near++;
        a.vx += sx * 0.05 + gx / gd * 0.09 + (n ? (ax / n - a.vx) * 0.05 + cx / n * 0.004 : 0);
        a.vy += sy * 0.05 + gy / gd * 0.09 + (n ? (ay / n - a.vy) * 0.05 + cy / n * 0.004 : 0);
        const v = Math.hypot(a.vx, a.vy) || 1;
        a.vx = a.vx / v * SPEED; a.vy = a.vy / v * SPEED;
        a.x = Math.min(Math.max(a.x + a.vx, 2), W - 2); a.y = Math.min(Math.max(a.y + a.vy, 2), H - 2);
      }
      if (near > N * 0.6) { reached++; goal = newGoal(); }  // most of the group is there: a new goal
    }

    function draw() {
      const s = getComputedStyle(document.documentElement);
      const ink = s.getPropertyValue("--text").trim(), accent = s.getPropertyValue("--accent").trim(),
            warm = s.getPropertyValue("--warm").trim(), surface = s.getPropertyValue("--surface").trim();
      ctx.fillStyle = surface; ctx.fillRect(0, 0, W, H);
      ctx.strokeStyle = warm; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(goal.x, goal.y, 40, 0, Math.PI * 2); ctx.stroke();
      ctx.fillStyle = warm; ctx.beginPath(); ctx.arc(goal.x, goal.y, 5, 0, Math.PI * 2); ctx.fill();
      for (const a of agents) {  // a small arrowhead pointing where it's going
        const h = Math.atan2(a.vy, a.vx);
        ctx.fillStyle = Math.hypot(goal.x - a.x, goal.y - a.y) < 40 ? accent : ink;
        ctx.beginPath();
        ctx.moveTo(a.x + Math.cos(h) * 7, a.y + Math.sin(h) * 7);
        ctx.lineTo(a.x + Math.cos(h + 2.5) * 4.5, a.y + Math.sin(h + 2.5) * 4.5);
        ctx.lineTo(a.x + Math.cos(h - 2.5) * 4.5, a.y + Math.sin(h - 2.5) * 4.5);
        ctx.fill();
      }
      score.textContent = `Goals reached: ${reached}`;
    }

    function tick() { step(); draw(); frame = requestAnimationFrame(tick); }
    function start() {
      cancelAnimationFrame(frame);
      scatter(); reached = 0;
      if (still) { for (let i = 0; i < 300; i++) step(); return draw(); }
      frame = requestAnimationFrame(tick);
    }

    canvas.addEventListener("click", e => {
      const box = canvas.getBoundingClientRect();
      goal = { x: (e.clientX - box.left) / box.width * W, y: (e.clientY - box.top) / box.height * H };
      if (still) { for (let i = 0; i < 300; i++) step(); draw(); }
    });
    dialog.querySelector(".pong-close").addEventListener("click", () => dialog.close());
    dialog.querySelector(".messi-again").addEventListener("click", start);
    dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", () => { cancelAnimationFrame(frame); trigger.focus(); });
    return { open() { dialog.showModal(); start(); } };
  }
})();
