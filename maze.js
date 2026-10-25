// Hidden on the profile: click "reinforcement learning" in the intro for two agents learning the
// same maze by Q-learning, side by side. Each estimates how good every move is with a small neural
// network that sees only the row and the column it's in. The one on the left has no activation
// function, so it's linear: all it can do is add a row score to a column score, and that can't
// describe a maze. The one on the right puts a ReLU between its layers, which lets it bend, and it
// finds the shortest route. Shading is how good each network thinks a square is.
// eggs.js shows the button and loads this file the first time it's clicked.
(() => {
  const trigger = document.querySelector(".maze-egg");
  if (!trigger) return;
  let maze;
  (window.openEgg ||= {}).maze = () => (maze ||= build()).open();

  function build() {
    // # wall, S start, G goal. The shortest route is 31 steps.
    const MAP = [
      "##############",
      "#S...#.......#",
      "#.##.#.####..#",
      "#.#..#....#..#",
      "#.#.####.##.##",
      "#...#....#...#",
      "###.#.####.#.#",
      "#...#......#.#",
      "#.#####..###.#",
      "#.......#...G#",
      "##############",
    ];
    const ROWS = MAP.length, COLS = MAP[0].length, CELL = 30, GAP = 24;
    const MW = COLS * CELL, MH = ROWS * CELL, W = MW * 2 + GAP, H = MH + 26;
    const START = [1, 1], GOAL = [12, 9];
    const wall = (x, y) => MAP[y][x] === "#";
    const MOVES = [[1, 0], [-1, 0], [0, 1], [0, -1]];
    const GAMMA = 0.95, STEP_COST = -0.04, MAX_STEPS = 400, EPISODES = 400, HIDDEN = 64, LR = 0.05, REPLAY = 4;

    const dialog = document.createElement("dialog");
    dialog.className = "pong maze";
    dialog.setAttribute("aria-label", "Two agents learning a maze, with and without an activation function");
    dialog.innerHTML =
      '<div class="pong-head"><p class="pong-score">Same maze, same network, one difference</p>' +
      '<button type="button" class="pong-close" aria-label="Close">×</button></div>' +
      '<canvas aria-label="Animated: two copies of a maze; on the left a linear network never learns the route, on the right a network with ReLU learns it"></canvas>' +
      '<div class="messi-foot"><p class="pong-help">Both networks see only the row and the column. Without an activation function the left one is a straight line: it can only add a row score to a column score, and a maze isn’t that. A ReLU lets the right one bend, and it learns the route.</p>' +
      '<button type="button" class="messi-again">Train again</button></div>';
    document.body.append(dialog);
    const canvas = dialog.querySelector("canvas"), ctx = canvas.getContext("2d");
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr; ctx.scale(dpr, dpr);
    const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

    const argmax = v => { const m = Math.max(v[0], v[1], v[2], v[3]), ties = [0, 1, 2, 3].filter(i => v[i] === m); return ties[Math.floor(Math.random() * ties.length)]; };

    // One hidden layer. Input: a one-hot column plus a one-hot row, so the first layer is a
    // column weight plus a row weight per hidden unit. The output layer starts at zero.
    function agent(label, act) {
      const IN = COLS + ROWS;
      const W1 = Float64Array.from({ length: HIDDEN * IN }, () => (Math.random() * 2 - 1) * 0.5);
      const b1 = new Float64Array(HIDDEN), W2 = new Float64Array(4 * HIDDEN), b2 = new Float64Array(4);
      const h = new Float64Array(HIDDEN), out = new Float64Array(4);
      const forward = (x, y) => {  // fills h and out; returns out (reused, so copy it to keep it)
        for (let j = 0; j < HIDDEN; j++) {
          const z = W1[j * IN + x] + W1[j * IN + COLS + y] + b1[j];
          h[j] = act && z < 0 ? 0 : z;  // ReLU, or nothing at all
        }
        for (let k = 0; k < 4; k++) {
          let sum = b2[k];
          for (let j = 0; j < HIDDEN; j++) sum += W2[k * HIDDEN + j] * h[j];
          out[k] = sum;
        }
        return out;
      };
      const best = (x, y) => { const o = forward(x, y); return Math.max(o[0], o[1], o[2], o[3]); };
      const learn = (x, y, a, target) => {  // one gradient step on (Q(s, a) − target)²
        const err = forward(x, y)[a] - target;
        for (let j = 0; j < HIDDEN; j++) {
          const g = act && h[j] <= 0 ? 0 : err * W2[a * HIDDEN + j];
          W2[a * HIDDEN + j] -= LR * err * h[j];
          W1[j * IN + x] -= LR * g; W1[j * IN + COLS + y] -= LR * g; b1[j] -= LR * g;
        }
        b2[a] -= LR * err;
      };
      return { label, forward, best, learn, memory: [], pos: START.slice(), steps: 0, episode: 0, eps: 1, lengths: [] };
    }

    function step(A) {
      const [x, y] = A.pos;
      const a = Math.random() < A.eps ? Math.floor(Math.random() * 4) : argmax(A.forward(x, y));
      let nx = x + MOVES[a][0], ny = y + MOVES[a][1];
      if (wall(nx, ny)) { nx = x; ny = y; }
      const done = nx === GOAL[0] && ny === GOAL[1], r = done ? 1 : STEP_COST;
      const target = (r2, d, x2, y2) => (d ? r2 : r2 + GAMMA * A.best(x2, y2));
      A.learn(x, y, a, target(r, done, nx, ny));
      A.memory.push([x, y, a, r, nx, ny, done]);
      if (A.memory.length > 4000) A.memory.shift();
      for (let k = 0; k < REPLAY; k++) {  // and a few remembered moves
        const [mx, my, ma, mr, mnx, mny, md] = A.memory[Math.floor(Math.random() * A.memory.length)];
        A.learn(mx, my, ma, target(mr, md, mnx, mny));
      }
      A.pos = [nx, ny]; A.steps++;
      if (done || A.steps >= MAX_STEPS) {
        A.lengths.push(A.steps); A.episode++; A.steps = 0; A.pos = START.slice();
        if (done) A.eps = Math.max(0.02, A.eps * 0.9);  // explore less only once it has found the goal
      }
    }

    function route(A) {  // the greedy route from the start, if it reaches the goal
      const out = [START.slice()], seen = new Set();
      let [x, y] = START;
      while (!(x === GOAL[0] && y === GOAL[1])) {
        const v = [...A.forward(x, y)], a = v.indexOf(Math.max(...v));
        const nx = x + MOVES[a][0], ny = y + MOVES[a][1];
        if (wall(nx, ny) || seen.has(ny * COLS + nx)) return null;
        seen.add(ny * COLS + nx); x = nx; y = ny; out.push([x, y]);
      }
      return out;
    }

    let agents, frame, frames;
    function draw() {
      const s = getComputedStyle(document.documentElement);
      const ink = s.getPropertyValue("--text").trim(), muted = s.getPropertyValue("--muted").trim(),
            accent = s.getPropertyValue("--accent").trim(), warm = s.getPropertyValue("--warm").trim(),
            surface = s.getPropertyValue("--surface").trim();
      ctx.fillStyle = surface; ctx.fillRect(0, 0, W, H);
      agents.forEach((A, i) => {
        const ox = i * (MW + GAP);
        const best = [];
        for (let y = 0; y < ROWS; y++) for (let x = 0; x < COLS; x++) if (!wall(x, y)) best.push([x, y, A.best(x, y)]);
        const lo = Math.min(...best.map(b => b[2])), hi = Math.max(...best.map(b => b[2]));
        ctx.globalAlpha = 0.85; ctx.fillStyle = ink;
        for (let y = 0; y < ROWS; y++) for (let x = 0; x < COLS; x++) if (wall(x, y)) ctx.fillRect(ox + x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2);
        ctx.fillStyle = accent;
        for (const [x, y, v] of best) {
          ctx.globalAlpha = hi > lo ? ((v - lo) / (hi - lo)) * 0.6 : 0;
          ctx.fillRect(ox + x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2);
        }
        ctx.globalAlpha = 1;
        const path = A.episode > 10 && route(A);
        if (path) {
          ctx.strokeStyle = warm; ctx.lineWidth = 3; ctx.lineJoin = ctx.lineCap = "round";
          ctx.beginPath();
          path.forEach(([x, y], k) => ctx[k ? "lineTo" : "moveTo"](ox + x * CELL + CELL / 2, y * CELL + CELL / 2));
          ctx.stroke();
        }
        ctx.fillStyle = warm; ctx.fillRect(ox + GOAL[0] * CELL + 7, GOAL[1] * CELL + 7, CELL - 14, CELL - 14);
        ctx.fillStyle = ink;
        ctx.beginPath(); ctx.arc(ox + A.pos[0] * CELL + CELL / 2, A.pos[1] * CELL + CELL / 2, CELL / 4, 0, Math.PI * 2); ctx.fill();
        const last = A.lengths.slice(-5), avg = last.length ? Math.round(last.reduce((p, q) => p + q) / last.length) : 0;
        ctx.font = "600 12px " + s.getPropertyValue("--sans");
        ctx.fillStyle = ink; ctx.fillText(A.label, ox, MH + 17);
        ctx.fillStyle = muted;
        const note = path ? `found the ${path.length - 1}-step route` : `episode ${A.episode}` + (avg ? ` · ${avg} steps` : "");
        ctx.fillText(note, ox + MW - ctx.measureText(note).width, MH + 17);
      });
    }

    // Slow at first so you can watch them wander, then as many moves as fit in 12 ms a frame;
    // stops once both have run their episodes.
    function tick() {
      const slow = ++frames < 120, until = performance.now() + 12;  // the first 120 frames, one move each
      do agents.forEach(A => A.episode < EPISODES && step(A));
      while (!slow && performance.now() < until && agents.some(A => A.episode < EPISODES));
      draw();
      if (agents.some(A => A.episode < EPISODES)) frame = requestAnimationFrame(tick);
    }
    function start() {
      cancelAnimationFrame(frame);
      agents = [agent("No activation (linear)", false), agent("With ReLU", true)]; frames = 0;
      if (still) { while (agents.some(A => A.episode < EPISODES)) agents.forEach(A => A.episode < EPISODES && step(A)); return draw(); }
      frame = requestAnimationFrame(tick);
    }

    dialog.querySelector(".pong-close").addEventListener("click", () => dialog.close());
    dialog.querySelector(".messi-again").addEventListener("click", start);
    dialog.addEventListener("click", e => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", () => { cancelAnimationFrame(frame); trigger.focus(); });
    return { open() { dialog.showModal(); start(); } };
  }
})();
