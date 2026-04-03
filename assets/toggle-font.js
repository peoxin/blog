(function toggleFont() {
  const STORAGE_KEY = "font-preference";
  const FONT_ATTR = "data-font";

  // Using localStorage to persist the font preference across sessions
  const Storage = {
    get: () => {
      try {
        return localStorage.getItem(STORAGE_KEY);
      } catch (e) {
        return null;
      }
    },
    set: (font) => {
      try {
        localStorage.setItem(STORAGE_KEY, font);
      } catch (e) {
        /* ignore error */
      }
    },
  };

  function applyFont(font) {
    document.documentElement.setAttribute(FONT_ATTR, font);
    Storage.set(font);
    updateButtonText(font);
  }

  function createToggleButton() {
    const btn = document.createElement("button");
    btn.id = "font-toggle";
    btn.className = "font-toggle-btn";
    btn.type = "button";
    btn.innerHTML = "serif";

    btn.addEventListener("click", () => {
      const current = Storage.get() || "sans";
      const next = current === "sans" ? "serif" : "sans";

      applyFont(next);
    });

    return btn;
  }

  function updateButtonText(font) {
    const btn = document.getElementById("font-toggle");
    if (!btn) return;

    if (font === "serif") {
      btn.innerHTML = "sans";
      btn.classList.remove("is-serif");
    } else {
      btn.innerHTML = "serif";
      btn.classList.add("is-serif");
    }
  }

  function init() {
    const saved = Storage.get();
    if (saved) {
      applyFont(saved);
    }

    const header = document.querySelector("header");
    const btn = createToggleButton();

    if (header) {
      header.appendChild(btn);
    } else {
      document.body.appendChild(btn);
    }

    // Fix first click not working issue by applying the saved font immediately
    if (saved) {
      document.documentElement.setAttribute(FONT_ATTR, saved);
      Storage.set(saved);
      setTimeout(() => {
        updateButtonText(saved);
      }, 0);
    } else {
      document.documentElement.setAttribute(FONT_ATTR, "sans");
      setTimeout(() => {
        updateButtonText("sans");
      }, 0);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
