(() => {
  const state = { active: "direct", surface: "light" };
  const cards = [...document.querySelectorAll("[data-specimen]")];
  const tabs = [...document.querySelectorAll("[data-mode]")];
  const stages = [...document.querySelectorAll(".chart-stage")];
  let replayTimer = 0;
  let scaleFrame = 0;

  function activeStage() {
    return document.querySelector(`[data-specimen="${state.active}"] .chart-stage`);
  }

  function applyState() {
    document.body.dataset.active = state.active;
    document.body.dataset.surface = state.surface;
    cards.forEach((card) => card.classList.toggle("is-active", card.dataset.specimen === state.active));
    tabs.forEach((tab) => {
      if (tab.dataset.mode === state.active) tab.setAttribute("aria-current", "page");
      else tab.removeAttribute("aria-current");
    });
    document.querySelector('[data-action="surface"]').textContent = `SURFACE / ${state.surface.toUpperCase()}`;
    scheduleRescale();
  }

  function replay(stage = activeStage()) {
    if (!stage) return;
    clearTimeout(replayTimer);
    stages.forEach((item) => item.classList.remove("is-replaying", "is-preparing"));
    stage.classList.add("is-preparing");
    void stage.offsetWidth;
    requestAnimationFrame(() => {
      stage.classList.add("is-replaying");
      stage.classList.remove("is-preparing");
      replayTimer = window.setTimeout(() => stage.classList.remove("is-replaying"), 1700);
    });
  }

  function toggleSurface() {
    state.surface = state.surface === "light" ? "dark" : "light";
    applyState();
  }

  function rescale(viewport) {
    const stage = viewport.querySelector(".frame-stage");
    const scale = Math.min(1, viewport.clientWidth / 1280);
    const key = scale.toFixed(5);
    if (stage.dataset.scale === key) return;
    stage.dataset.scale = key;
    if (CSS.supports("zoom", "1")) {
      stage.style.zoom = key;
      stage.style.transform = "none";
    } else {
      stage.style.zoom = "1";
      stage.style.transform = `scale(${key})`;
    }
    viewport.style.height = `${720 * scale}px`;
  }

  function scheduleRescale() {
    if (scaleFrame) return;
    scaleFrame = requestAnimationFrame(() => {
      scaleFrame = 0;
      document.querySelectorAll(".frame-viewport").forEach(rescale);
    });
  }

  tabs.forEach((tab) => tab.addEventListener("click", () => {
    state.active = tab.dataset.mode;
    applyState();
    replay();
  }));
  document.querySelector('[data-action="surface"]').addEventListener("click", toggleSurface);
  document.querySelector('[data-action="replay"]').addEventListener("click", () => replay());
  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-stage-action]");
    if (!button) return;
    if (button.dataset.stageAction === "surface") toggleSurface();
    if (button.dataset.stageAction === "replay") replay(button.closest(".chart-stage"));
  });
  window.addEventListener("keydown", (event) => {
    if (event.key.toLowerCase() === "d") toggleSurface();
    if (event.key === " ") { event.preventDefault(); replay(); }
  });
  window.addEventListener("resize", scheduleRescale, { passive: true });
  applyState();
})();
