// Profile and Things I'm thinking about: a small "#" beside each entry's heading. It shows on
// hover or focus; clicking it puts that entry's address in the address bar and on the clipboard.
(() => {
  document.querySelectorAll(".project[id] > div > h3, .role[id] > div > h3, .mini[id] > h3, .thought[id] > h2").forEach(h => {
    const id = h.closest("[id]").id;
    const link = document.createElement("a");
    link.className = "anchor";
    link.href = "#" + id;
    link.textContent = "#";
    link.setAttribute("aria-label", "Link to " + h.textContent.trim());
    link.setAttribute("aria-live", "polite");  // so "Copied" is read out
    link.addEventListener("click", e => {
      e.preventDefault();
      history.replaceState(null, "", "#" + id);
      const url = location.href;
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(() => {
        link.textContent = "Copied";
        setTimeout(() => { link.textContent = "#"; }, 1500);
      }, () => {});
    });
    h.append(" ", link);
  });

  // A link to an entry inside a closed group (Built for fun) opens the group, then goes to the entry.
  // Printing opens every group, since paper can't be clicked.
  const reveal = () => {
    const target = location.hash.length > 1 && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    const group = target && target.closest("details:not([open])");
    if (!group) return;
    group.open = true;
    target.scrollIntoView();
  };
  reveal();
  addEventListener("hashchange", reveal);
  addEventListener("beforeprint", () => document.querySelectorAll("details").forEach(d => { d.open = true; }));
})();
