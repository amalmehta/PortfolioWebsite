// Live interests: the tile icons move on hover, but phones have no hover. So each
// icon also plays its motion once on tap; nothing moves on its own as you scroll.
// (Reduced motion turns every tile animation off in styles.css.)
(() => {
  const tiles = document.querySelectorAll(".tile");
  if (!tiles.length) return;
  const play = tile => {
    if (tile.classList.contains("is-live")) return;
    tile.classList.add("is-live");
    setTimeout(() => tile.classList.remove("is-live"), 2400);
  };
  tiles.forEach(t => t.addEventListener("touchstart", () => play(t), { passive: true }));
})();
