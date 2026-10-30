// Grateful for's lantern garden: each lantern lights in turn as it scrolls into view.
// Without JS, or with reduced motion, they are simply lit.
(() => {
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const list = document.querySelector("#grateful-for .inspo");
  if (!list) return;
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add("lit"); io.unobserve(e.target); }
  }, { rootMargin: "0px 0px -12% 0px" });
  for (const lantern of list.children) {
    lantern.classList.add("unlit");
    io.observe(lantern);
  }
})();
