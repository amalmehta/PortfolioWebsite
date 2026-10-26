// The eight hidden extras (the ring on The Lord of the Rings tile opens dragon.js): "soccer tournaments" (messi.js), "reinforcement learning" (maze.js) and the
// star by North star (nova.js) on the profile, the skier on the Travel page's Hokkaido drawing (pong.js), the first-principles line on
// What I try to live by (tree.js), "Building worlds" on Interests (world.js) and "many agents" on
// Things I'm thinking about (swarm.js). This shows their buttons, and fetches a game's
// script only the first time its button is clicked, so most visits never download it.
// Without JavaScript the buttons stay hidden and the words stay plain text.
(() => {
  for (const [selector, name, plain] of [[".messi-egg", "messi", ".messi-plain"], [".skier", "pong"], [".tree-egg", "tree", ".tree-plain"], [".nova-egg", "nova"], [".dragon-egg", "dragon", ".dragon-plain"],
    [".maze-egg", "maze", ".maze-plain"], [".world-egg", "world", ".world-plain"], [".swarm-egg", "swarm", ".swarm-plain"]]) {
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
