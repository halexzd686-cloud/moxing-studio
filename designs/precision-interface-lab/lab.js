(() => {
  const variantCss = new URL("precision-variant.css", window.location.href).href;
  const specs = {
    c03: {
      code: "C03", name: "SIGNAL / TREND", family: "ROUTE", data: "12T · 2S", state: "TRACE.LOCK",
      background: `
        <path d="M 230 120 H 258" pathLength="1" class="pi-terminal-lead" />
        <rect x="254" y="116" width="8" height="8" class="pi-terminal-node" />
        <text x="266" y="124" font-size="9" class="pi-terminal-id">E03</text>`,
      foreground: `
        <rect x="286" y="325.67" width="12" height="12" class="pi-socket" style="--pi-delay:180ms" />
        <circle cx="1126" cy="115.94" r="14" class="pi-lock-ring" />
        <path d="M 1106 115.94 H 1114 M 1138 115.94 H 1146 M 1126 95.94 V 103.94" class="pi-lock-cross" />
        <text x="1105" y="143" text-anchor="end" font-size="10" class="pi-address pi-address-signal">E03 / T12</text>`
    },
    c08: {
      code: "C08", name: "STAGE / CHANNEL", family: "STAGE", data: "05M · 04L", state: "BOTTLENECK",
      background: `
        <path d="M 230 146 H 270" pathLength="1" class="pi-terminal-lead" />
        <rect x="266" y="142" width="8" height="8" class="pi-terminal-node" />
        <text x="278" y="150" font-size="9" class="pi-terminal-id">E08</text>`,
      foreground: `
        <rect x="380.8" y="416" width="8" height="8" class="pi-socket" style="--pi-delay:180ms" /><text x="384.8" y="443" text-anchor="middle" font-size="9" class="pi-address">S1</text>
        <rect x="546.4" y="416" width="8" height="8" class="pi-socket" style="--pi-delay:300ms" /><text x="550.4" y="443" text-anchor="middle" font-size="9" class="pi-address">S2</text>
        <rect x="712" y="416" width="8" height="8" class="pi-socket" style="--pi-delay:420ms" /><text x="716" y="443" text-anchor="middle" font-size="9" class="pi-address">S3</text>
        <rect x="877.6" y="416" width="8" height="8" class="pi-socket-signal" /><text x="881.6" y="443" text-anchor="middle" font-size="9" class="pi-address pi-address-signal">S4</text>
        <rect x="1043.2" y="416" width="8" height="8" class="pi-socket" style="--pi-delay:660ms" /><text x="1047.2" y="443" text-anchor="middle" font-size="9" class="pi-address">S5</text>
        <circle cx="798.8" cy="250" r="13" class="pi-lock-ring" /><path d="M 781 250 H 788 M 810 250 H 817" class="pi-lock-cross" />
        <text x="798.8" y="279" text-anchor="middle" font-size="10" class="pi-address pi-address-signal">E08 / Δ58</text>`
    },
    c15: {
      code: "C15", name: "COMMERCE / FLOW", family: "PORT", data: "05N · 04R", state: "LEAK.LOCK",
      background: `
        <path d="M 200 142 H 242" pathLength="1" class="pi-terminal-lead" />
        <rect x="238" y="138" width="8" height="8" class="pi-terminal-node" />
        <text x="250" y="146" font-size="9" class="pi-terminal-id">E15</text>`,
      foreground: `
        <rect x="384" y="191" width="8" height="8" class="pi-socket" style="--pi-delay:180ms" />
        <rect x="384" y="341" width="8" height="8" class="pi-socket" style="--pi-delay:260ms" />
        <rect x="526.67" y="266" width="8" height="8" class="pi-socket" style="--pi-delay:380ms" />
        <rect x="638.67" y="266" width="8" height="8" class="pi-socket" style="--pi-delay:500ms" />
        <rect x="781.33" y="266" width="8" height="8" class="pi-socket" style="--pi-delay:620ms" />
        <rect x="893.33" y="266" width="8" height="8" class="pi-socket" style="--pi-delay:740ms" />
        <rect x="1036" y="266" width="8" height="8" class="pi-socket-signal" />
        <circle cx="968.67" cy="270" r="14" class="pi-lock-ring" />
        <text x="968.67" y="300" text-anchor="middle" font-size="10" class="pi-address pi-address-signal">E15 / L04</text>`
    },
    c22: {
      code: "C22", name: "ADDRESS / MATRIX", family: "MATRIX", data: "05×05", state: "PAIR.LOCK",
      background: `
        <path d="M 230 392 H 270" pathLength="1" class="pi-terminal-lead" />
        <rect x="266" y="388" width="8" height="8" class="pi-terminal-node" />
        <text x="278" y="396" font-size="9" class="pi-terminal-id">E22</text>`,
      foreground: `
        <text x="335" y="65" text-anchor="middle" font-size="9" class="pi-address">C1</text><text x="405" y="65" text-anchor="middle" font-size="9" class="pi-address pi-address-signal">C2</text><text x="475" y="65" text-anchor="middle" font-size="9" class="pi-address">C3</text><text x="545" y="65" text-anchor="middle" font-size="9" class="pi-address">C4</text><text x="615" y="65" text-anchor="middle" font-size="9" class="pi-address">C5</text>
        <text x="286" y="109" text-anchor="end" font-size="9" class="pi-address">R1</text><text x="286" y="179" text-anchor="end" font-size="9" class="pi-address pi-address-signal">R2</text><text x="286" y="249" text-anchor="end" font-size="9" class="pi-address">R3</text><text x="286" y="319" text-anchor="end" font-size="9" class="pi-address">R4</text><text x="286" y="389" text-anchor="end" font-size="9" class="pi-address">R5</text>
        <path d="M 369 85 V 69 H 385 M 425 69 H 441 V 85 M 441 125 V 141 H 425 M 385 141 H 369 V 125" class="pi-focus-corner" />
        <text x="451" y="88" font-size="10" class="pi-address pi-address-signal">E22 / A02</text>`
    }
  };

  const state = { active: "c08", view: "focus", surface: "light", output: "ui" };
  const frames = [...document.querySelectorAll("iframe")];
  const frameByChart = (chart) => document.querySelector(`[data-prototype="${chart}"] iframe`);

  function svgGroup(doc, className, markup) {
    const group = doc.createElementNS("http://www.w3.org/2000/svg", "g");
    group.setAttribute("class", className);
    group.innerHTML = markup;
    return group;
  }

  function instrument(frame) {
    const card = frame.closest(".prototype");
    const key = card.dataset.prototype;
    const spec = specs[key];
    const doc = frame.contentDocument;
    if (!doc || !spec || doc.documentElement.dataset.precision === "lab") return;

    const code = doc.querySelector(".chart-code");
    const header = doc.querySelector(".chart-header");
    const controls = doc.querySelector(".motion-controls");
    const svg = doc.querySelector(".chart-body svg");
    if (!code || !header || !controls || !svg) return;

    doc.documentElement.dataset.precision = "lab";
    doc.documentElement.dataset.output = state.output;
    doc.documentElement.dataset.labView = state.view;
    const stylesheet = doc.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = variantCss;
    doc.head.append(stylesheet);

    code.innerHTML = `<div class="pi-code"><div class="pi-code__top"><strong>${spec.code}</strong><span>SYS / 21</span></div><div class="pi-code__name">${spec.name}</div><div class="pi-code__state"><span class="pi-dots" aria-hidden="true">${"<i></i>".repeat(6)}</span>${spec.state}</div></div>`;

    const titleBlock = doc.querySelector(".chart-title").parentElement;
    const meta = doc.createElement("div");
    meta.className = "pi-meta";
    meta.innerHTML = `<span>FAMILY / ${spec.family}</span><span>DATA / ${spec.data}</span><span data-state>STATE / READY</span>`;
    titleBlock.append(meta);

    const ticks = doc.createElement("span");
    ticks.className = "pi-header-ticks";
    ticks.setAttribute("aria-hidden", "true");
    ticks.innerHTML = "<i></i>".repeat(16);
    header.append(ticks);

    const controlCodes = { replay: "R", pause: "H", surface: "S" };
    controls.querySelectorAll("button").forEach((button) => { button.dataset.code = controlCodes[button.dataset.action]; });

    const background = svgGroup(doc, "pi-overlay pi-overlay--background", spec.background);
    const foreground = svgGroup(doc, "pi-overlay pi-overlay--foreground", spec.foreground);
    svg.insertBefore(background, svg.children[1] || null);
    svg.append(foreground);

    frame.contentWindow.Moxing?.setSurface(state.surface);
    frame.dataset.ready = "true";
    frame.contentWindow.Moxing?.settle();
  }

  function applyState() {
    document.body.dataset.active = state.active;
    document.body.dataset.view = state.view;
    document.body.dataset.surface = state.surface;
    document.querySelectorAll("[data-chart]").forEach((button) => {
      if (button.dataset.chart === state.active) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });
    document.querySelector('[data-lab-action="view"]').textContent = `VIEW / ${state.view.toUpperCase()}`;
    document.querySelector('[data-lab-action="surface"]').textContent = `SURFACE / ${state.surface.toUpperCase()}`;
    document.querySelector('[data-lab-action="output"]').textContent = `OUTPUT / ${state.output.toUpperCase()}`;
    document.querySelector('[data-lab-action="output"]').classList.toggle("is-active", state.output === "export");
    document.querySelector('[data-lab-action="replay"]').textContent = state.view === "grid" ? "REPLAY / FOCUS" : "REPLAY / ACTIVE";
    frames.forEach((frame) => {
      const doc = frame.contentDocument;
      if (!doc || frame.dataset.ready !== "true") return;
      doc.documentElement.dataset.output = state.output;
      doc.documentElement.dataset.labView = state.view;
      frame.contentWindow.Moxing?.setSurface(state.surface);
      frame.contentWindow.Moxing?.settle();
    });
    scheduleRescale();
  }

  function rescale(viewport) {
    const stage = viewport.querySelector(".frame-stage");
    const scale = Math.min(1, viewport.clientWidth / 1280);
    const scaleKey = scale.toFixed(5);
    if (stage.dataset.scale === scaleKey) return;
    stage.dataset.scale = scaleKey;
    stage.style.transform = `scale(${scaleKey})`;
    viewport.style.height = `${720 * scale}px`;
  }
  function rescaleAll() { document.querySelectorAll(".frame-viewport").forEach(rescale); }
  let scaleFrame = 0;
  function scheduleRescale() {
    if (scaleFrame) return;
    scaleFrame = requestAnimationFrame(() => { scaleFrame = 0; rescaleAll(); });
  }

  frames.forEach((frame) => frame.addEventListener("load", () => { instrument(frame); applyState(); }));
  frames.forEach((frame) => { if (frame.contentDocument?.readyState === "complete") instrument(frame); });

  document.querySelectorAll("[data-chart]").forEach((button) => button.addEventListener("click", () => {
    state.active = button.dataset.chart;
    state.view = "focus";
    applyState();
  }));
  document.querySelector('[data-lab-action="view"]').addEventListener("click", () => { state.view = state.view === "focus" ? "grid" : "focus"; applyState(); });
  document.querySelector('[data-lab-action="surface"]').addEventListener("click", () => { state.surface = state.surface === "light" ? "dark" : "light"; applyState(); });
  document.querySelector('[data-lab-action="output"]').addEventListener("click", () => { state.output = state.output === "ui" ? "export" : "ui"; applyState(); });
  document.querySelector('[data-lab-action="replay"]').addEventListener("click", () => {
    if (state.view === "grid") { state.view = "focus"; applyState(); }
    const frame = frameByChart(state.active);
    requestAnimationFrame(() => frame?.contentWindow.Moxing?.replay());
  });

  window.addEventListener("keydown", (event) => {
    if (event.key.toLowerCase() === "d") { state.surface = state.surface === "light" ? "dark" : "light"; applyState(); }
    if (event.key.toLowerCase() === "e") { state.output = state.output === "ui" ? "export" : "ui"; applyState(); }
    if (event.key === " ") { event.preventDefault(); document.querySelector('[data-lab-action="replay"]').click(); }
  });
  window.addEventListener("resize", scheduleRescale, { passive: true });
  applyState();
})();
