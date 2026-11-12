/*!
 * Vallacar Tracker — light / dark colour mode.
 *
 * Loaded in <head> before the stylesheets so the saved mode is applied
 * before the first paint. The choice is stored under Tabler's own
 * `tabler-theme` key so the built-in Theme Settings drawer stays in sync.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'tabler-theme';
  var root = document.documentElement;

  function normalize(value) {
    return value === 'dark' ? 'dark' : 'light';
  }

  function current() {
    return normalize(root.getAttribute('data-bs-theme'));
  }

  function stored() {
    try {
      return normalize(window.localStorage.getItem(STORAGE_KEY));
    } catch (error) {
      return 'light';
    }
  }

  function apply(theme, persist) {
    theme = normalize(theme);
    root.setAttribute('data-bs-theme', theme);
    root.style.colorScheme = theme;

    if (persist) {
      try {
        window.localStorage.setItem(STORAGE_KEY, theme);
      } catch (error) {
        /* Storage can be unavailable in private browsing; the visual mode
           still changes for the current page. */
      }
    }

    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      if (!meta.getAttribute('data-light-color')) {
        meta.setAttribute('data-light-color', meta.getAttribute('content') || '#ffc72c');
      }
      meta.setAttribute('content', theme === 'dark'
        ? '#0a0f1c'
        : meta.getAttribute('data-light-color'));
    }

    document.querySelectorAll('[data-theme-set]').forEach(function (button) {
      var active = button.getAttribute('data-theme-set') === theme;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    // Keep the Tabler Theme Settings radios aligned with the toggle.
    document.querySelectorAll('input[name="theme"]').forEach(function (radio) {
      radio.checked = radio.value === theme;
    });

    document.dispatchEvent(new CustomEvent('vallacar:themechange', {
      detail: { theme: theme },
    }));
  }

  // Apply immediately (before CSS paints) and expose a tiny public API.
  apply(stored(), false);

  window.VallacarTheme = {
    get: current,
    set: function (theme) { apply(theme, true); },
    toggle: function () { apply(current() === 'dark' ? 'light' : 'dark', true); },
  };

  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target || typeof target.closest !== 'function') {
      return;
    }

    var button = target.closest('[data-theme-set]');
    if (button) {
      event.preventDefault();
      apply(button.getAttribute('data-theme-set'), true);
      return;
    }

    // The settings drawer resets Tabler's stored values without firing a
    // change event, so refresh the toggle afterwards.
    if (target.closest('#reset-changes')) {
      window.setTimeout(function () { apply(stored(), false); }, 0);
    }
  });

  document.addEventListener('change', function (event) {
    if (event.target && event.target.name === 'theme') {
      apply(event.target.value, true);
    }
  });

  document.addEventListener('DOMContentLoaded', function () {
    apply(current(), false);
  });
})();
