// The email address is written into the page as "name [at] domain" with its parts in
// data attributes, so address-harvesting bots reading the raw HTML don't get it.
// For visitors this turns each one back into a normal mailto link. Without JavaScript
// the link goes to the contact form instead.
document.querySelectorAll("a.email").forEach(a => {
  const address = a.dataset.u + "@" + a.dataset.d;
  a.href = "mailto:" + address;
  a.textContent = address;

  // In the intro's contact list, a Copy button too: many people have no mail app set up,
  // so a mailto link does nothing for them.
  if (!a.closest(".contact")) return;
  // The older way, for browsers that block the clipboard API.
  const fallback = () => {
    const box = Object.assign(document.createElement("textarea"), { value: address });
    box.setAttribute("readonly", ""); box.style.cssText = "position:fixed;opacity:0";
    document.body.append(box); box.select();
    const ok = document.execCommand("copy");
    box.remove();
    if (!ok) throw new Error("copy blocked");
  };
  const copy = document.createElement("button");
  copy.type = "button";
  copy.className = "copy-email";
  copy.textContent = "Copy";
  copy.setAttribute("aria-label", "Copy email address");
  copy.setAttribute("aria-live", "polite");
  let reset;
  copy.addEventListener("click", async () => {
    try {
      try { await navigator.clipboard.writeText(address); } catch { fallback(); }
      copy.textContent = "Copied";
    } catch { copy.textContent = "Couldn’t copy"; }
    clearTimeout(reset);
    reset = setTimeout(() => { copy.textContent = "Copy"; }, 1800);
  });
  a.after(copy);
});
