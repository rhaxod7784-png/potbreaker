(() => {
  const footer = document.getElementById("site-footer");
  const game = document.getElementById("gamePanel");
  const end = document.getElementById("end");
  if (!footer || !game || !end) return;

  const sync = () => {
    const active =
      !game.classList.contains("hidden") || !end.classList.contains("hidden");
    footer.classList.toggle("pb-game-hidden", active);
    if (active) {
      document.documentElement.style.setProperty("--pb-footer-h", "0px");
    } else {
      document.documentElement.style.removeProperty("--pb-footer-h");
    }
  };

  sync();
  const observer = new MutationObserver(sync);
  for (const panel of [game, end]) {
    observer.observe(panel, { attributes: true, attributeFilter: ["class"] });
  }
})();
