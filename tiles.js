// Live interests: the tile icons move on hover, but phones have no hover. So each
// icon also plays its motion once as its tile scrolls into view, and again on tap.
// (Reduced motion turns every tile animation off in styles.css.)
(() => {
  const tiles = document.querySelectorAll(".tile");
  if (!tiles.length) return;
  const play = tile => {
    if (tile.classList.contains("is-live")) return;
    tile.classList.add("is-live");
    setTimeout(() => tile.classList.remove("is-live"), 2400);
  };
  const seen = new IntersectionObserver(entries => entries.forEach(e => {
    if (e.isIntersecting) { play(e.target); seen.unobserve(e.target); }
  }), { threshold: 0.6 });
  tiles.forEach(t => { seen.observe(t); t.addEventListener("touchstart", () => play(t), { passive: true }); });
})();
