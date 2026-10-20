// Hidden on the profile: click "soccer tournaments" in Outside work for a stylised
// replay inspired by Messi's solo goal against Real Madrid at the Bernabéu
// (2011 Champions League semi-final). Dots on half a pitch, no photos or logos.
// The run is an approximation, not tracking data.
// eggs.js shows the button and loads this file the first time it's clicked.
(() => {
  const trigger = document.querySelector(".messi-egg");
  if (!trigger) return;
  let replay;
  (window.openEgg ||= {}).messi = () => (replay ||= build()).open();

  function build() {
    // Pitch in metres at 12 px each: x from just behind halfway (50) to past the goal line (106),
    // y across the 48 m band around the penalty area (10 to 58).
    const X0 = 50, X1 = 106, Y0 = 10, Y1 = 58, PX = 12, W = (X1 - X0) * PX, H = (Y1 - Y0) * PX;
    const sx = x => (x - X0) * PX, sy = y => (y - Y0) * PX;
    const dialog = document.createElement("dialog");
    dialog.className = "pong messi";
    dialog.setAttribute("aria-label", "Messi's solo goal against Real Madrid, replayed");
    dialog.innerHTML =
      '<div class="pong-head"><p class="pong-score">Bernabéu, 2011</p>' +
      '<button type="button" class="pong-close" aria-label="Close">×</button></div>' +
      '<canvas aria-label="Animated replay: a dot for Messi carries the ball past white defenders and scores"></canvas>' +
      '<div class="messi-foot"><p class="pong-help">A stylised replay inspired by Messi’s solo goal against Real Madrid in the 2011 Champions League semi-final. Dots, not tracking data.</p>' +
      '<button type="button" class="messi-again">Replay</button></div>';
    document.body.append(dialog);
    const canvas = dialog.querySelector("canvas"), ctx = canvas.getContext("2d");
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr; ctx.scale(dpr, dpr);
    const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

    // His run: picks it up near halfway on the right, cuts inside past the defenders, finishes low.
    const path = [[56, 50], [61, 47], [66, 47.5], [71, 44], [76, 45], [81, 41], [86, 42], [90.5, 38], [94.5, 38.5], [97.5, 36.5]];
    const RUN = 6.2, SHOT = 0.7, HOLD = 2.4;  // seconds: dribble, ball in flight, celebrate
    const defenders = [[64, 41], [72, 51], [79, 37], [87.5, 47], [92.5, 31]].map(([x, y]) => ({ x0: x, y0: y, x, y, beaten: false }));
    const keeper = { x: 103.4, y: 34 };
    const target = [105.3, 30.5];

    // Catmull-Rom through the run's points, sampled by distance so the speed stays even.
    const lerp = (a, b, t) => a + (b - a) * t;
    const cr = (p0, p1, p2, p3, t) => {
      const t2 = t * t, t3 = t2 * t;
      return [0, 1].map(i => 0.5 * (2 * p1[i] + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t2 + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t3));
    };
    const samples = [];
    for (let i = 0; i < path.length - 1; i++)
      for (let k = 0; k < 20; k++) samples.push(cr(path[Math.max(i - 1, 0)], path[i], path[i + 1], path[Math.min(i + 2, path.length - 1)], k / 20));
    samples.push(path[path.length - 1]);
    const dist = [0];
    for (let i = 1; i < samples.length; i++) dist.push(dist[i - 1] + Math.hypot(samples[i][0] - samples[i - 1][0], samples[i][1] - samples[i - 1][1]));
    const at = f => {
      const d = f * dist[dist.length - 1];
      let i = dist.findIndex(v => v >= d); if (i <= 0) return samples[0];
      const t = (d - dist[i - 1]) / (dist[i] - dist[i - 1] || 1);
      return [lerp(samples[i - 1][0], samples[i][0], t), lerp(samples[i - 1][1], samples[i][1], t)];
    };

    let t0, raf;
    function frame(now) {
      if (still) {  // reduced motion: play it through off screen, show only the final picture
        for (let s = 0; s <= RUN + SHOT + HOLD; s += 1 / 60) draw(s);
        return;
      }
      t0 ??= now;
      const t = (now - t0) / 1000;
      draw(t);
      if (t < RUN + SHOT + HOLD) raf = requestAnimationFrame(frame);
    }

    function draw(t) {
      const f = Math.min(t / RUN, 1), ease = f < 1 ? f : 1;
      const [mx, my] = at(ease);
      // Defenders close him down as he nears; once he's past, they're left behind,
      // sliding off to the side of his line and fading a little.
      defenders.forEach(d => {
        const r = Math.hypot(mx - d.x, my - d.y);
        if (!d.beaten && mx > d.x + 1) {
          d.beaten = true;
          const side = Math.sign(d.y - my) || 1;
          d.tx = d.x - 2.5; d.ty = d.y + side * 3.5;
        }
        if (!d.beaten && r < 10) { d.x = lerp(d.x, mx, 0.045); d.y = lerp(d.y, my + Math.sign(d.y0 - my) * 2.2, 0.045); }
        if (d.beaten) { d.x = lerp(d.x, d.tx, 0.05); d.y = lerp(d.y, d.ty, 0.05); d.fade = Math.min((d.fade || 0) + 0.02, 0.45); }
      });
      // The ball runs a touch ahead of him, then flies in after the shot.
      const shot = Math.max(0, Math.min((t - RUN) / SHOT, 1));
      const ahead = at(Math.min(ease + 0.012, 1));
      const touch = 0.6 + 0.4 * Math.abs(Math.sin(t * 9));
      let bx = lerp(mx, ahead[0], touch), by = lerp(my, ahead[1], touch);
      if (t > RUN) { bx = lerp(path[path.length - 1][0] + 0.8, target[0], shot); by = lerp(path[path.length - 1][1], target[1], shot); }
      const kd = t > RUN ? Math.min((t - RUN) / (SHOT * 0.8), 1) : 0;  // the keeper dives the wrong way
      const ky = lerp(keeper.y, keeper.y + 4, kd);

      // Pitch
      for (let i = 0; i < 8; i++) { ctx.fillStyle = i % 2 ? "#3f8a4f" : "#459457"; ctx.fillRect(i * W / 8, 0, W / 8 + 1, H); }
      ctx.strokeStyle = "rgba(255,255,255,0.85)"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(sx(52.5), 0); ctx.lineTo(sx(52.5), H); ctx.moveTo(sx(105), 0); ctx.lineTo(sx(105), H); ctx.stroke();
      ctx.beginPath(); ctx.arc(sx(52.5), sy(34), 9.15 * PX, -Math.PI / 2, Math.PI / 2); ctx.stroke();
      ctx.strokeRect(sx(105 - 16.5), sy(34 - 20.16), sx(105) - sx(105 - 16.5), sy(34 + 20.16) - sy(34 - 20.16));
      ctx.strokeRect(sx(105 - 5.5), sy(34 - 9.16), sx(105) - sx(105 - 5.5), sy(34 + 9.16) - sy(34 - 9.16));
      ctx.beginPath(); ctx.arc(sx(105 - 11), sy(34), 2.5, 0, Math.PI * 2); ctx.fillStyle = "#fff"; ctx.fill();
      ctx.beginPath(); ctx.arc(sx(105 - 11), sy(34), 9.15 * PX, Math.PI * 0.705, Math.PI * 1.295); ctx.stroke();
      ctx.fillStyle = "rgba(255,255,255,0.9)"; ctx.fillRect(sx(105), sy(34 - 3.66), 6, sy(34 + 3.66) - sy(34 - 3.66));

      // His trail so far
      ctx.save(); ctx.setLineDash([5, 6]); ctx.strokeStyle = "rgba(255,214,90,0.9)"; ctx.lineWidth = 2.5; ctx.beginPath();
      samples.forEach(([x, y], i) => { if (dist[i] <= ease * dist[dist.length - 1]) (i ? ctx.lineTo(sx(x), sy(y)) : ctx.moveTo(sx(x), sy(y))); });
      ctx.lineTo(sx(mx), sy(my)); ctx.stroke(); ctx.restore();

      const dot = (x, y, r, fill, ring) => { ctx.beginPath(); ctx.arc(sx(x), sy(y), r, 0, Math.PI * 2); ctx.fillStyle = fill; ctx.fill(); if (ring) { ctx.lineWidth = 2; ctx.strokeStyle = ring; ctx.stroke(); } };
      defenders.forEach(d => { ctx.globalAlpha = 1 - (d.fade || 0); dot(d.x, d.y, 9, "#f4f4f2", "#c9a227"); ctx.globalAlpha = 1; });
      dot(keeper.x, ky, 9, "#2b2b2b", "#f4f4f2");
      // Messi: blaugrana, with his number
      ctx.save(); ctx.beginPath(); ctx.arc(sx(mx), sy(my), 10, 0, Math.PI * 2); ctx.clip();
      ctx.fillStyle = "#a50044"; ctx.fillRect(sx(mx) - 10, sy(my) - 10, 20, 20);
      ctx.fillStyle = "#004d98"; for (let k = -10; k < 10; k += 6.6) ctx.fillRect(sx(mx) + k, sy(my) - 10, 3.3, 20);
      ctx.restore();
      ctx.lineWidth = 2; ctx.strokeStyle = "#fff"; ctx.beginPath(); ctx.arc(sx(mx), sy(my), 10, 0, Math.PI * 2); ctx.stroke();
      ctx.fillStyle = "#fff"; ctx.font = "700 9px system-ui, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText("10", sx(mx), sy(my) + 0.5);
      // Ball
      dot(bx, by, 4.5, "#ffffff", "#222");

      if (t > RUN + SHOT) {
        const a = Math.min((t - RUN - SHOT) / 0.4, 1);
        ctx.fillStyle = `rgba(255,255,255,${a})`; ctx.font = "700 44px " + getComputedStyle(document.documentElement).getPropertyValue("--serif");
        ctx.textAlign = "center"; ctx.textBaseline = "alphabetic"; ctx.fillText("Goal!", W * 0.42, H * 0.2);
      }
    }

    function start() {
      cancelAnimationFrame(raf); t0 = undefined;
      defenders.forEach(d => { d.x = d.x0; d.y = d.y0; d.beaten = false; d.fade = 0; });
      raf = requestAnimationFrame(frame);
    }
    dialog.querySelector(".pong-close").addEventListener("click", () => dialog.close());
    dialog.querySelector(".messi-again").addEventListener("click", start);
    dialog.addEventListener("click", e => {
      const r = dialog.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close();
    });
    dialog.addEventListener("close", () => { cancelAnimationFrame(raf); trigger.focus(); });
    return { open() { dialog.showModal(); start(); } };
  }
})();
