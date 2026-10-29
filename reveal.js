// Sections on the profile ease up into place the first time they scroll into view.
// Without JS, or with reduced motion, everything is simply shown.
(() => {
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const sections = [...document.querySelectorAll("main .section")];
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  }, { rootMargin: "0px 0px -8% 0px" });
  // Only sections still below the fold wait to fade in; anything already on screen stays put.
  for (const s of sections) if (s.getBoundingClientRect().top > innerHeight * 0.92) { s.classList.add("reveal"); io.observe(s); }
})();
