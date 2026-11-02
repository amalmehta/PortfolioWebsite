// The profile's North star: the Belief card fades through my current beliefs, starting from a different one each
// visit. It holds while a cursor or keyboard is on it, and a tap holds or resumes it. Without JS, or with reduced
// motion, it stays on the first line.
(() => {
  const line = document.querySelector(".ns-text[data-lines]");
  if (!line || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const lines = JSON.parse(line.dataset.lines), EVERY = 7000, FADE = 400;
  let at = Math.floor(Math.random() * lines.length), hovered = false, focused = false, held = false;

  // Room for the longest line, so the page below doesn't shift as they change.
  const fit = () => {
    line.style.minHeight = "";
    let tallest = 0;
    const shown = line.textContent;
    for (const text of lines) { line.textContent = text; tallest = Math.max(tallest, line.offsetHeight); }
    line.textContent = shown;
    line.style.minHeight = `${tallest}px`;
  };

  line.textContent = lines[at];
  line.classList.add("rotating");
  line.tabIndex = 0;
  fit();
  new ResizeObserver(() => requestAnimationFrame(fit)).observe(line.parentElement);

  line.addEventListener("pointerenter", e => { if (e.pointerType === "mouse") hovered = true; });
  line.addEventListener("pointerleave", () => { hovered = false; });
  line.addEventListener("focus", () => { focused = line.matches(":focus-visible"); });
  line.addEventListener("blur", () => { focused = false; });
  line.addEventListener("pointerup", e => { if (e.pointerType !== "mouse") held = !held; });

  setInterval(() => {
    if (hovered || focused || held || document.hidden) return;
    line.classList.add("fading");
    setTimeout(() => {
      at = (at + 1) % lines.length;
      line.textContent = lines[at];
      line.classList.remove("fading");
    }, FADE);
  }, EVERY);
})();
