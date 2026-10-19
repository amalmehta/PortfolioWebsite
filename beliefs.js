// Values page: shows Beliefs as two tabs, "What I believe currently" and "Outdated".
// Without JavaScript both lists show one after the other, each under its own heading.
(() => {
  const section = document.querySelector(".beliefs");
  if (!section) return;
  const tabs = [...section.querySelectorAll('[role="tab"]')];
  const show = tab => tabs.forEach(t => {
    const on = t === tab;
    t.setAttribute("aria-selected", on);
    t.tabIndex = on ? 0 : -1;
    document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
  });
  tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => show(tab));
    tab.addEventListener("keydown", e => {  // arrow keys move between tabs
      const step = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (!step) return;
      const next = tabs[(i + step + tabs.length) % tabs.length];
      show(next); next.focus(); e.preventDefault();
    });
  });
  section.querySelector('[role="tablist"]').hidden = false;
  section.classList.add("tabbed");
  show(tabs[0]);
})();
