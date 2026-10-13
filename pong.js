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

    let me, cpu, ball, score, over, raf, last;
    const keys = {};
    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

    function reset() { me = cpu = H / 2; score = [0, 0]; over = false; serve(1); show(); }
    function serve(dir) {
      const a = Math.random() * 0.8 - 0.4;
      ball = { x: W / 2, y: H / 2, vx: dir * Math.cos(a) * 300, vy: Math.sin(a) * 300, wait: 0.8 };
    }
    function show() {
      scoreEl.textContent = over
        ? (score[0] > score[1] ? `You win, ${score[0]}–${score[1]}!` : `The mountain wins, ${score[1]}–${score[0]}.`)
        : `You ${score[0]} · Mountain ${score[1]}`;
    }

    function step(dt) {
      if (over) return;
      if (keys.ArrowUp) me -= 420 * dt;
      if (keys.ArrowDown) me += 420 * dt;
      me = clamp(me, PH / 2, H - PH / 2);
      // The mountain follows the ball at a capped speed, and drifts home when it's moving away.
      const target = ball.vx > 0 ? ball.y : H / 2;
      cpu = clamp(cpu + clamp(target - cpu, -250 * dt, 250 * dt), PH / 2, H - PH / 2);
      if (ball.wait > 0) { ball.wait -= dt; return; }
      ball.x += ball.vx * dt; ball.y += ball.vy * dt;
      if ((ball.y < R && ball.vy < 0) || (ball.y > H - R && ball.vy > 0)) ball.vy *= -1;
      hit(X + PW / 2, me, 1);
      hit(W - X - PW / 2, cpu, -1);
      if (ball.x < -R) point(1);
      else if (ball.x > W + R) point(0);
    }
    // Bounce off a paddle; where it lands sets the angle, and every hit speeds it up a little.
    function hit(px, py, dir) {
      if (Math.sign(ball.vx) === dir) return;
      if (Math.abs(ball.x - px) > R + PW / 2 || Math.abs(ball.y - py) > PH / 2 + R) return;
      const a = clamp((ball.y - py) / (PH / 2), -1, 1);
      const speed = Math.min(Math.hypot(ball.vx, ball.vy) * 1.06, 720);
      ball.vx = dir * Math.cos(a) * speed;
      ball.vy = Math.sin(a) * speed;
      ball.x = px + dir * (R + PW / 2);
    }
    function point(who) {
      score[who]++;
      if (score[who] >= WIN) over = true;
      else serve(who === 0 ? 1 : -1);
      show();
    }

    function draw() {
      const cs = getComputedStyle(document.documentElement), c = n => cs.getPropertyValue(n).trim();
      ctx.fillStyle = c("--surface"); ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = c("--line");
      for (let y = 8; y < H; y += 24) ctx.fillRect(W / 2 - 1, y, 2, 12);
      ctx.fillStyle = c("--accent"); ctx.fillRect(X, me - PH / 2, PW, PH);
      ctx.fillStyle = c("--muted"); ctx.fillRect(W - X - PW, cpu - PH / 2, PW, PH);
      if (!over) {
        ctx.fillStyle = c("--warm");
        ctx.beginPath(); ctx.arc(ball.x, ball.y, R, 0, Math.PI * 2); ctx.fill();
      } else {
        ctx.fillStyle = c("--text"); ctx.textAlign = "center";
        ctx.font = "600 30px " + c("--serif");
        ctx.fillText(score[0] > score[1] ? "You win!" : "The mountain wins.", W / 2, H / 2 - 8);
        ctx.font = "16px " + c("--sans"); ctx.fillStyle = c("--muted");
        ctx.fillText("Click or press Space to play again", W / 2, H / 2 + 24);
      }
    }
    function loop(t) {
      const dt = Math.min((t - (last ?? t)) / 1000, 0.033);
      last = t; step(dt); draw();
      raf = requestAnimationFrame(loop);
    }

    canvas.addEventListener("pointermove", e => {
      const r = canvas.getBoundingClientRect();
      me = clamp((e.clientY - r.top) / r.height * H, PH / 2, H - PH / 2);
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
    dialog.addEventListener("close", () => { cancelAnimationFrame(raf); last = undefined; skier.focus(); });

    return {
      open() {
        if (!ball || over) reset();
        dialog.showModal();
        canvas.focus();
        raf = requestAnimationFrame(loop);
      },
    };
  }
})();
