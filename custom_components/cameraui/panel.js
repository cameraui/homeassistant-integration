class CameraUiPanel extends HTMLElement {
  connectedCallback() {
    if (this._built) return;
    this._built = true;

    const root = this.attachShadow({ mode: 'open' });
    root.innerHTML = `
      <style>
        :host { display: flex; flex-direction: column; height: 100%; background: #0d0d0d; color-scheme: light dark; }
        .bar { display: none; align-items: center; height: 48px; padding: 0 4px; }
        :host([narrow]) .bar { display: flex; }
        iframe { flex: 1; border: 0; width: 100%; background: #0d0d0d; color-scheme: light dark; }
        @media (prefers-color-scheme: light) {
          :host, iframe { background: #f8fafc; }
        }
      </style>
      <div class="bar"></div>
      <iframe allow="fullscreen; camera; microphone; autoplay; clipboard-read; clipboard-write"></iframe>
    `;

    this._iframe = root.querySelector('iframe');
    this._iframe.addEventListener('load', () => {
      this._loaded = true;
      this._postTheme();
      this._postLang();
    });
    this._menu = document.createElement('ha-menu-button');
    root.querySelector('.bar').appendChild(this._menu);
    this._apply();
  }

  set panel(panel) {
    this._panel = panel;
    this._apply();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._menu) this._menu.hass = hass;
    this._sync();
  }

  set narrow(narrow) {
    this._narrow = narrow;
    if (narrow) this.setAttribute('narrow', '');
    else this.removeAttribute('narrow');
    if (this._menu) this._menu.narrow = narrow;
  }

  _mode() {
    return this._hass && this._hass.themes && this._hass.themes.darkMode ? 'dark' : 'light';
  }

  _lang() {
    return this._hass && this._hass.language ? this._hass.language : null;
  }

  _applyBg(mode) {
    const bg = mode === 'dark' ? '#0d0d0d' : '#f8fafc';
    this.style.background = bg;
    if (this._iframe) this._iframe.style.background = bg;
  }

  _apply() {
    if (!this._iframe || !this._panel) return;
    const mode = this._hass ? this._mode() : null;
    if (mode) this._applyBg(mode);
    const base = (this._panel.config && this._panel.config.proxyUrl) || '/';
    const params = new URLSearchParams();
    if (mode) params.set('cui_theme', mode);
    const lang = this._lang();
    if (lang) params.set('cui_lang', lang);
    const qs = params.toString();
    const url = qs ? `${base}?${qs}` : base;
    if (this._iframe.getAttribute('src') !== url) this._iframe.setAttribute('src', url);
    if (this._menu) {
      this._menu.hass = this._hass;
      this._menu.narrow = this._narrow;
    }
  }

  _sync() {
    if (!this._iframe) return;
    this._applyBg(this._mode());
    if (!this._iframe.getAttribute('src')) this._apply();
    if (this._loaded) {
      this._postTheme();
      this._postLang();
    }
  }

  _postTheme() {
    const mode = this._mode();
    if (mode === this._postedMode) return;
    this._postedMode = mode;
    this._post({ type: 'cui:theme', mode });
  }

  _postLang() {
    const language = this._lang();
    if (!language || language === this._postedLang) return;
    this._postedLang = language;
    this._post({ type: 'cui:language', language });
  }

  _post(message) {
    if (this._iframe && this._iframe.contentWindow) {
      this._iframe.contentWindow.postMessage(message, window.location.origin);
    }
  }
}

customElements.define('cameraui-panel', CameraUiPanel);
