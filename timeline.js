// A trip's stops on Travel: the line draws itself down and each stop lights up in turn,
// the first time the list scrolls into view. Without JS, or with reduced motion, it is simply shown.
(() => {
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add("play"); io.unobserve(e.target); }
  }, { rootMargin: "0px 0px -15% 0px" });
  for (const list of document.querySelectorAll(".trip-timeline")) {
    list.querySelectorAll("li").forEach((li, i) => li.style.setProperty("--i", i));
    list.classList.add("animated");
    io.observe(list);
  }
})();
