// Pong, hidden behind the skier on the Hokkaido drawing (photos.html).
// Without JavaScript the skier stays hidden, since it would do nothing.
(() => {
  const skier = document.querySelector(".skier");
  if (!skier) return;
  skier.hidden = false;
  let game;
  skier.addEventListener("click", () => (game ||= makeGame()).open());

  function makeGame() {
    const W = 640, H = 400, PW = 10, PH = 72, R = 7, WIN = 5, X = 26;
    const dialog = document.createElement("dialog");
    dialog.className = "pong";
    dialog.setAttribute("aria-label", "Pong");
    dialog.innerHTML =
      '<div class="pong-head"><p class="pong-score" aria-live="polite"></p>' +
      '<button type="button" class="pong-close" aria-label="Close">×</button></div>' +
      '<canvas tabindex="0" aria-label="Pong court: you are the left paddle"></canvas>' +
      '<p class="pong-help">Move with the mouse, a finger or the arrow keys. First to 5. Esc to leave.</p>';
    document.body.append(dialog);
    const canvas = dialog.querySelector("canvas"), ctx = canvas.getContext("2d");
    const scoreEl = dialog.querySelector(".pong-score");
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.scale(dpr, dpr);

    // Physics runs on a fixed 120 Hz clock and drawing blends the last two steps,
    // so motion looks the same at any frame rate. Paddles ease towards where they're
    // headed instead of jumping there.
    const STEP = 1 / 120;
    let me, meTo, cpu, ball, score, over, raf, last, acc = 0, prev, col;
    const keys = {};
    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
    const ease = (rate, dt) => 1 - Math.exp(-rate * dt);
    const lerp = (a, b, t) => a + (b - a) * t;
    const readColors = () => {
      const cs = getComputedStyle(document.documentElement), c = n => cs.getPropertyValue(n).trim();
      return { bg: c("--surface"), line: c("--line"), me: c("--accent"), cpu: c("--muted"), ball: c("--warm"),
               text: c("--text"), serif: c("--serif"), sans: c("--sans") };
    };
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { col = readColors(); });

    function reset() { me = meTo = cpu = H / 2; score = [0, 0]; over = false; serve(1); show(); }
    function serve(dir) {
      const a = Math.random() * 0.8 - 0.4;
      ball = { x: W / 2, y: H / 2, vx: dir * Math.cos(a) * 300, vy: Math.sin(a) * 300, wait: 0.8 };
      snapshot();
    }
    function snapshot() { prev = { me, cpu, x: ball.x, y: ball.y }; }
    function show() {
      scoreEl.textContent = over
        ? (score[0] > score[1] ? `You win, ${score[0]}–${score[1]}!` : `The mountain wins, ${score[1]}–${score[0]}.`)
        : `You ${score[0]} · Mountain ${score[1]}`;
    }

    function step(dt) {
      snapshot();
      if (over) return;
      if (keys.ArrowUp) meTo -= 480 * dt;
      if (keys.ArrowDown) meTo += 480 * dt;
      meTo = clamp(meTo, PH / 2, H - PH / 2);
      me += (meTo - me) * ease(30, dt);
      // The mountain eases after the ball at a capped speed, and drifts home when it's moving away.
      const target = ball.vx > 0 ? ball.y : H / 2;
      cpu = clamp(cpu + clamp((target - cpu) * ease(9, dt), -260 * dt, 260 * dt), PH / 2, H - PH / 2);
      if (ball.wait > 0) { ball.wait -= dt; return; }
      const x0 = ball.x;
      ball.x += ball.vx * dt; ball.y += ball.vy * dt;
      if (ball.y < R) { ball.y = 2 * R - ball.y; ball.vy = Math.abs(ball.vy); }
      if (ball.y > H - R) { ball.y = 2 * (H - R) - ball.y; ball.vy = -Math.abs(ball.vy); }
      hit(x0, X + PW, me, 1);          // your paddle's right face
      hit(x0, W - X - PW, cpu, -1);    // the mountain's left face
      if (ball.x < -R) point(1);
      else if (ball.x > W + R) point(0);
    }
    // Bounce if the ball's leading edge crossed a paddle's face during this step (so a
    // fast ball can't slip through); where it lands sets the angle, and each hit speeds it up.
    function hit(x0, face, py, dir) {
      if (Math.sign(ball.vx) === dir) return;
      const lead0 = x0 - dir * R, lead1 = ball.x - dir * R;
      if (dir * (lead0 - face) < 0 || dir * (lead1 - face) > 0) return;
      const t = (lead0 - face) / (lead0 - lead1 || 1);
      const y = ball.y - ball.vy * STEP * (1 - t);
      if (Math.abs(y - py) > PH / 2 + R) return;
      const a = clamp((y - py) / (PH / 2), -1, 1);
      const speed = Math.min(Math.hypot(ball.vx, ball.vy) * 1.06, 720);
      ball.vx = dir * Math.cos(a) * speed;
      ball.vy = Math.sin(a) * speed;
      ball.x = face + dir * R;
    }
    function point(who) {
      score[who]++;
      if (score[who] >= WIN) over = true;
      else serve(who === 0 ? 1 : -1);
      show();
    }

    function draw(t) {
      ctx.fillStyle = col.bg; ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = col.line;
      for (let y = 8; y < H; y += 24) ctx.fillRect(W / 2 - 1, y, 2, 12);
      ctx.fillStyle = col.me; roundRect(X, lerp(prev.me, me, t) - PH / 2);
      ctx.fillStyle = col.cpu; roundRect(W - X - PW, lerp(prev.cpu, cpu, t) - PH / 2);
      if (!over) {
        ctx.fillStyle = col.ball;
        ctx.beginPath(); ctx.arc(lerp(prev.x, ball.x, t), lerp(prev.y, ball.y, t), R, 0, Math.PI * 2); ctx.fill();
      } else {
        ctx.fillStyle = col.text; ctx.textAlign = "center";
        ctx.font = "600 30px " + col.serif;
        ctx.fillText(score[0] > score[1] ? "You win!" : "The mountain wins.", W / 2, H / 2 - 8);
        ctx.font = "16px " + col.sans; ctx.fillStyle = col.cpu;
        ctx.fillText("Click or press Space to play again", W / 2, H / 2 + 24);
      }
    }
    function roundRect(x, y) {
      if (!ctx.roundRect) return ctx.fillRect(x, y, PW, PH);  // older browsers: square ends
      ctx.beginPath(); ctx.roundRect(x, y, PW, PH, PW / 2); ctx.fill();
    }
    function loop(now) {
      acc += Math.min((now - (last ?? now)) / 1000, 0.1);
      last = now;
      while (acc >= STEP) { step(STEP); acc -= STEP; }
      draw(acc / STEP);
      raf = requestAnimationFrame(loop);
    }

    canvas.addEventListener("pointermove", e => {
      const r = canvas.getBoundingClientRect();
      meTo = clamp((e.clientY - r.top) / r.height * H, PH / 2, H - PH / 2);
    });
    canvas.addEventListener("pointerdown", e => {
      canvas.setPointerCapture(e.pointerId);
      if (over) reset();
    });
    dialog.addEventListener("keydown", e => {
      if (e.key === "ArrowUp" || e.key === "ArrowDown") { keys[e.key] = true; e.preventDefault(); }
      if (over && (e.key === " " || e.key === "Enter")) { reset(); e.preventDefault(); }
    });
    dialog.addEventListener("keyup", e => { keys[e.key] = false; });
    dialog.querySelector(".pong-close").addEventListener("click", () => dialog.close());
    // A click on the backdrop (outside the dialog's box) closes it too.
    dialog.addEventListener("click", e => {
      const r = dialog.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close();
    });
    dialog.addEventListener("close", () => { cancelAnimationFrame(raf); last = undefined; acc = 0; skier.focus(); });

    return {
      open() {
        if (!ball || over) reset();
        col = readColors();
        dialog.showModal();
        canvas.focus();
        raf = requestAnimationFrame(loop);
      },
    };
  }
})();
