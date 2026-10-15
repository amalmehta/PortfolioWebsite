// Listening, reading, watching (interests.html): draws a timeline from the list
// below it. Each <li class="log-item"> carries data-kind (listening, reading or
// watching), data-start (YYYY-MM) and, once it's over, data-end (YYYY-MM).
// The list stays as the accessible, no-JavaScript version; the timeline is a picture of it.
(() => {
  const box = document.querySelector(".log-timeline");
  const items = [...document.querySelectorAll(".log-item")];
  if (!box || !items.length) return;

  const KINDS = [["listening", "Listening"], ["reading", "Reading"], ["watching", "Watching"]];
  const month = s => { const [y, m] = s.split("-").map(Number); return y * 12 + (m - 1); };
  const now = new Date(), thisMonth = now.getFullYear() * 12 + now.getMonth();
  const label = m => new Date(Math.floor(m / 12), m % 12, 1).toLocaleString("en", { month: "short" });

  const entries = items.map(li => ({
    kind: li.dataset.kind,
    title: li.querySelector(".log-title")?.textContent.trim() || li.textContent.trim(),
    by: li.querySelector(".log-by")?.textContent.trim() || "",
    start: month(li.dataset.start),
    end: li.dataset.end ? month(li.dataset.end) : null,  // null: still going
  })).filter(e => KINDS.some(([k]) => k === e.kind) && Number.isFinite(e.start));

  // The window runs from the earliest start to this month, at least six months wide.
  const last = Math.max(thisMonth, ...entries.map(e => e.end ?? thisMonth));
  const first = Math.min(last - 5, ...entries.map(e => e.start));
  const span = last - first + 1;

  // Within a lane, items that overlap in time go on separate rows (greedy packing).
  const lanes = KINDS.map(([kind, name]) => {
    const rows = [];
    entries.filter(e => e.kind === kind).sort((a, b) => a.start - b.start).forEach(e => {
      const until = e.end ?? last;
      let r = rows.findIndex(end => end < e.start);
      if (r < 0) { r = rows.length; rows.push(until); } else rows[r] = until;
      e.row = r;
    });
    return { kind, name, rows: Math.max(rows.length, 1) };
  }).filter(l => entries.some(e => e.kind === l.kind));

  const NS = "http://www.w3.org/2000/svg";
  const el = (tag, attrs, parent) => {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    parent && parent.appendChild(n);
    return n;
  };

  function draw() {
    const cs = getComputedStyle(document.documentElement), c = n => cs.getPropertyValue(n).trim();
    const colour = { listening: c("--accent"), reading: c("--warm"), watching: c("--muted") };
    const W = box.clientWidth, LEFT = W < 480 ? 74 : 92, RIGHT = 8, ROW = 24, GAP = 14, TOP = 26;
    const x = m => LEFT + (m - first) / span * (W - LEFT - RIGHT);
    const H = TOP + lanes.reduce((h, l) => h + l.rows * ROW + GAP, 0) + 4;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "log-svg" });
    box.replaceChildren(svg);  // in the page first, so labels can be measured

    // Month ticks along the top: every month if there's room, else every few.
    const every = Math.max(1, Math.ceil(span / Math.floor((W - LEFT) / 46)));
    for (let m = first; m <= last + 1; m++) {
      if ((m - first) % every) continue;
      el("line", { x1: x(m), x2: x(m), y1: TOP - 6, y2: H, stroke: c("--line") }, svg);
      if (m <= last) {
        const t = el("text", { x: x(m) + 3, y: TOP - 10, class: "log-tick" }, svg);
        t.textContent = label(m) + (m % 12 === 0 || m === first ? " " + Math.floor(m / 12) : "");
      }
    }

    // Lanes, each with its items as bars; ongoing ones fade out toward "now".
    let y = TOP;
    lanes.forEach(lane => {
      const name = el("text", { x: 0, y: y + ROW / 2 + 4, class: "log-lane" }, svg);
      name.textContent = lane.name;
      entries.filter(e => e.kind === lane.kind).forEach((e, i) => {
        const x0 = x(e.start), x1 = x((e.end ?? thisMonth) + 1), by = y + e.row * ROW + 3;
        const g = el("g", { class: "log-bar" }, svg);
        let fill = colour[e.kind];
        if (e.end === null) {
          const id = `log-fade-${lane.kind}-${i}`;
          const grad = el("linearGradient", { id, x1: 0, x2: 1, y1: 0, y2: 0 }, el("defs", {}, g));
          el("stop", { offset: "0.6", "stop-color": fill }, grad);
          el("stop", { offset: "1", "stop-color": fill, "stop-opacity": "0.25" }, grad);
          fill = `url(#${id})`;
        }
        el("rect", { x: x0 + 1, y: by, width: Math.max(x1 - x0 - 2, 6), height: ROW - 6, rx: 5, fill, opacity: 0.9 }, g);
        el("title", {}, g).textContent = e.title + (e.by ? " — " + e.by : "") + (e.end === null ? " (now)" : "");
        const text = el("text", { x: x0 + 8, y: by + ROW / 2 + 1, class: "log-label" }, g);
        text.textContent = e.title;
        // Too long for its bar: put it just after the bar if there's room before the next
        // bar on that row; otherwise shorten it with an ellipsis, or leave it to the tooltip.
        const room = x1 - x0 - 14;
        if (text.getComputedTextLength() > room) {
          const next = entries.filter(o => o !== e && o.kind === e.kind && o.row === e.row && o.start > e.start)
                              .reduce((m, o) => Math.min(m, x(o.start)), W - RIGHT);
          if (text.getComputedTextLength() + 10 <= next - x1) {
            text.setAttribute("x", x1 + 5);
            text.setAttribute("class", "log-label outside");
            text.style.fill = colour[e.kind];
          } else if (room < 28) {
            text.remove();
          } else {
            let t = e.title;
            while (t.length > 1 && text.getComputedTextLength() > room) { t = t.slice(0, -1); text.textContent = t.trimEnd() + "…"; }
          }
        }
      });
      y += lane.rows * ROW + GAP;
    });

    // "Now": a marker at the current month.
    const nx = x(thisMonth + (now.getDate() - 1) / 31);
    el("line", { x1: nx, x2: nx, y1: TOP - 6, y2: H, class: "log-now" }, svg);
    const nt = el("text", { x: nx, y: H - 2, class: "log-now-label", "text-anchor": "end" }, svg);
    nt.textContent = "now";
  }

  draw();
  let t; addEventListener("resize", () => { clearTimeout(t); t = setTimeout(draw, 120); });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", draw);
})();
