// The two hidden extras: "soccer tournaments" on the profile (messi.js) and the skier on the
// Travel page's Hokkaido drawing (pong.js). This shows their buttons, and fetches a game's
// script only the first time its button is clicked, so most visits never download it.
// Without JavaScript the buttons stay hidden and the words stay plain text.
(() => {
  for (const [selector, name, plain] of [[".messi-egg", "messi", ".messi-plain"], [".skier", "pong"]]) {
    const button = document.querySelector(selector);
    if (!button) continue;
    button.hidden = false;
    if (plain) document.querySelector(plain)?.remove();
    let loading;
    button.addEventListener("click", () => {
      loading ||= new Promise((done, failed) => {
        const script = Object.assign(document.createElement("script"), { src: button.dataset.script });
        script.onload = done; script.onerror = failed;
        document.head.append(script);
      });
      loading.then(() => window.openEgg[name](), () => { loading = null; });  // a failed fetch retries next click
    });
  }
})();
