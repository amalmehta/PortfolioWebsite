// What I live by: each Inspiration drawing tilts a little toward the cursor, like a print held in
// the hand, and settles back when the cursor leaves. Mouse and pen only; reduced motion turns it off.
(() => {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches || !matchMedia("(hover: hover)").matches) return;
  for (const card of document.querySelectorAll(".inspo-card .photo")) {
    card.addEventListener("pointermove", e => {
      const box = card.getBoundingClientRect();
      const x = (e.clientX - box.left) / box.width - 0.5, y = (e.clientY - box.top) / box.height - 0.5;
      card.style.setProperty("--tilt-x", `${(-y * 7).toFixed(2)}deg`);
      card.style.setProperty("--tilt-y", `${(x * 9).toFixed(2)}deg`);
    });
    card.addEventListener("pointerleave", () => {
      for (const p of ["--tilt-x", "--tilt-y"]) card.style.setProperty(p, "0deg");
    });
  }
})();
