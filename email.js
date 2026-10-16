// The email address is written into the page as "name [at] domain" with its parts in
// data attributes, so address-harvesting bots reading the raw HTML don't get it.
// For visitors this turns each one back into a normal mailto link. Without JavaScript
// the link goes to the contact form instead.
document.querySelectorAll("a.email").forEach(a => {
  const address = a.dataset.u + "@" + a.dataset.d;
  a.href = "mailto:" + address;
  a.textContent = address;
});
