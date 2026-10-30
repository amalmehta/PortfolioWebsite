// A little mischief. On every main page: a note for anyone reading the console. On What I try to
// live by: "It's not that serious." knocks the Ways list out of place, and it settles back.
// Without JavaScript the line stays plain text; with reduced motion it stays still.
(() => {
  console.log("Oh, you read the console too.\nThe site is plain HTML. The source is on GitHub: https://github.com/amalmehta/PortfolioWebsite\nIt's not that serious.");

  const button = document.querySelector(".serious-egg");
  if (!button) return;
  button.hidden = false;
  document.querySelector(".serious-plain")?.remove();
  const spread = (size) => (Math.random() * 2 - 1) * size;
  button.addEventListener("click", () => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    for (const card of button.closest("ul").children) {
      const away = `translate(${spread(26)}px, ${6 + Math.random() * 22}px) rotate(${spread(7)}deg)`;
      card.animate(
        [{ transform: "none" }, { transform: away, offset: 0.3 }, { transform: away, offset: 0.62 }, { transform: "none" }],
        { duration: 1700, delay: Math.random() * 120, easing: "cubic-bezier(0.34, 1.3, 0.64, 1)" }
      );
    }
  });
})();
