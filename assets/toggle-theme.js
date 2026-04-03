(function toggleTheme() {
  const STORAGE_KEY = "theme-preference";
  const THEME_ATTR = "data-theme";

  const ICONS = {
    sun: `<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 256 256">
            <path d="M120,40V16a8,8,0,0,1,16,0V40a8,8,0,0,1-16,0Zm8,24a64,64,0,1,0,64,64A64.07,64.07,0,0,0,128,64ZM58.34,69.66A8,8,0,0,0,69.66,58.34l-16-16A8,8,0,0,0,42.34,53.66Zm0,116.68-16,16a8,8,0,0,0,11.32,11.32l16-16a8,8,0,0,0-11.32-11.32ZM192,72a8,8,0,0,0,5.66-2.34l16-16a8,8,0,0,0-11.32-11.32l-16,16A8,8,0,0,0,192,72Zm5.66,114.34a8,8,0,0,0-11.32,11.32l16,16a8,8,0,0,0,11.32-11.32ZM48,128a8,8,0,0,0-8-8H16a8,8,0,0,0,0,16H40A8,8,0,0,0,48,128Zm80,80a8,8,0,0,0-8,8v24a8,8,0,0,0,16,0V216A8,8,0,0,0,128,208Zm112-88H216a8,8,0,0,0,0,16h24a8,8,0,0,0,0-16Z"></path>
            </svg>`,
    moon: `<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 256 256">
            <path d="M235.54,150.21a104.84,104.84,0,0,1-37,52.91A104,104,0,0,1,32,120,103.09,103.09,0,0,1,52.88,57.48a104.84,104.84,0,0,1,52.91-37,8,8,0,0,1,10,10,88.08,88.08,0,0,0,109.8,109.8,8,8,0,0,1,10,10Z"></path>
            </svg>`,
  };

  // Using sessionStorage to ensure that the preference resets after closing the browser tab
  const Storage = {
    get: () => {
      try {
        return sessionStorage.getItem(STORAGE_KEY);
      } catch (e) {
        return null;
      }
    },
    set: (theme) => {
      try {
        sessionStorage.setItem(STORAGE_KEY, theme);
      } catch (e) {
        /* Ignore error */
      }
    },
  };

  function getSystemPreference() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute(THEME_ATTR, theme);
    updateButtonUI(theme);
  }

  function createToggleButton() {
    const btn = document.createElement("button");
    btn.id = "theme-toggle";
    btn.className = "theme-toggle-btn";
    btn.type = "button";

    btn.addEventListener("click", () => {
      const current =
        document.documentElement.getAttribute(THEME_ATTR) ||
        getSystemPreference();
      const next = current === "dark" ? "light" : "dark";

      Storage.set(next);
      applyTheme(next);
    });

    return btn;
  }

  function updateButtonUI(theme) {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;

    if (theme === "dark") {
      btn.classList.add("is-dark");
      btn.innerHTML = ICONS.sun;
    } else {
      btn.classList.remove("is-dark");
      btn.innerHTML = ICONS.moon;
    }
  }

  function resolveCurrentTheme() {
    return Storage.get() || getSystemPreference();
  }

  function init() {
    // Apply the theme as early as possible to prevent flash of unstyled content (FOUC)
    const initialTheme = resolveCurrentTheme();
    document.documentElement.setAttribute(THEME_ATTR, initialTheme);

    // If the DOM is still loading, wait for it to be ready before injecting the button
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", injectButton);
    } else {
      injectButton();
    }
  }

  function injectButton() {
    const header = document.querySelector("header");
    const btn = createToggleButton();

    if (header) {
      header.appendChild(btn);
    } else {
      // If there's no header, append the button to the body as a fallback
      document.body.appendChild(btn);
    }

    updateButtonUI(resolveCurrentTheme());

    // When the system preference changes, we only want to update the theme
    // if the user hasn't explicitly chosen one for this session
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", (e) => {
        if (!Storage.get()) {
          applyTheme(e.matches ? "dark" : "light");
        }
      });
  }

  init();
})();
