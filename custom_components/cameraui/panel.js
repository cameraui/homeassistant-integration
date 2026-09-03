class CameraUiPanel extends HTMLElement {
  connectedCallback() {
    const parent = this.parentElement;
    if (
      parent &&
      parent.localName === 'ha-panel-custom' &&
      !parent.style.height
    ) {
      parent.style.height = '100%';
    }

    if (!this._onMessage) {
      this._onMessage = (event) => this._handleMessage(event);
    }

    window.addEventListener('message', this._onMessage);
    if (!this._onResize) {
      this._onResize = () => this._postSafeArea();
    }
    window.addEventListener('resize', this._onResize);

    if (this._built) return;
    this._built = true;

    const root = this.attachShadow({ mode: 'open' });
    root.innerHTML = `
      <style>
        :host { display: flex; flex-direction: column; height: 100vh; height: 100dvh; background: #0d0d0d; color-scheme: light dark; }
        iframe { flex: 1; border: 0; width: 100%; background: #0d0d0d; color-scheme: light dark; }
        .probe {
          position: absolute; visibility: hidden; pointer-events: none;
          padding: var(--safe-area-inset-top, 0px) var(--safe-area-content-inset-right, var(--safe-area-inset-right, 0px))
            var(--safe-area-inset-bottom, 0px) var(--safe-area-content-inset-left, var(--safe-area-inset-left, 0px));
        }
        @media (prefers-color-scheme: light) {
          :host, iframe { background: #f8fafc; }
        }
      </style>
      <div class="probe"></div>
      <iframe allow="fullscreen; camera; microphone; autoplay; clipboard-read; clipboard-write"></iframe>
    `;

    this._probe = root.querySelector('.probe');
    this._iframe = root.querySelector('iframe');
    this._iframe.addEventListener('load', () => {
      this._loaded = true;
      // a reload starts the app from scratch, so the posted state is stale
      this._postedMode = null;
      this._postedLang = null;
      this._postedToggle = null;
      this._postedSafeArea = null;
      this._postedBadge = null;
      this._postTheme();
      this._postLang();
      this._postSidebar();
      this._postSafeArea();
      this._postBadge();
      this._postRoute();
    });

    this._apply();
  }

  disconnectedCallback() {
    if (this._onMessage) window.removeEventListener('message', this._onMessage);
    if (this._onResize) window.removeEventListener('resize', this._onResize);
    this._unsubscribeBadges();
  }

  set panel(panel) {
    this._panel = panel;
    this._apply();
  }

  set hass(hass) {
    this._hass = hass;
    this._sync();
  }

  // HA hands the panel only the path, the query (startTs deep links) stays in the location
  set route(route) {
    const base = route && typeof route.path === 'string' ? route.path : '';
    const path = base ? `${base}${window.location.search || ''}` : '';
    if (path === this._routePath) return;
    this._routePath = path;
    if (!this._iframe) return;
    if (!this._iframe.getAttribute('src')) this._apply();
    else if (this._loaded) this._postRoute();
  }

  set narrow(narrow) {
    this._narrow = narrow;
    if (narrow) this.setAttribute('narrow', '');
    else this.removeAttribute('narrow');
    this._postSidebar();
  }

  _mode() {
    return this._hass && this._hass.themes && this._hass.themes.darkMode
      ? 'dark'
      : 'light';
  }

  _lang() {
    return this._hass && this._hass.language ? this._hass.language : null;
  }

  _canToggleMenu() {
    if (this._hass && this._hass.kioskMode) return false;
    const alwaysHidden = !!(
      this._hass && this._hass.dockedSidebar === 'always_hidden'
    );
    return !!this._narrow || alwaysHidden;
  }

  _applyBg(mode) {
    const bg = mode === 'dark' ? '#0d0d0d' : '#f8fafc';
    this.style.background = bg;
    if (this._iframe) this._iframe.style.background = bg;
  }

  _safeArea() {
    const s = getComputedStyle(this._probe);
    return `${s.paddingTop},${s.paddingRight},${s.paddingBottom},${s.paddingLeft}`;
  }

  _appPath() {
    const path = this._routePath || '';
    return path.replace(/^\/+/, '');
  }

  // the src is set once; later route changes go through postMessage so the app keeps its state
  _apply() {
    if (!this._iframe || !this._panel) return;
    const mode = this._hass ? this._mode() : null;
    if (mode) this._applyBg(mode);
    if (!this._iframe.getAttribute('src')) {
      const base = (this._panel.config && this._panel.config.proxyUrl) || '/';
      // the route may carry its own query (startTs deep links), merge instead of appending a second '?'
      const url = new URL(`${base}${this._appPath()}`, window.location.origin);
      if (mode) url.searchParams.set('cui_theme', mode);
      const lang = this._lang();
      if (lang) url.searchParams.set('cui_lang', lang);
      // so the app can render the burger on first paint instead of waiting for cui:sidebar
      url.searchParams.set('cui_menu', this._canToggleMenu() ? '1' : '0');
      url.searchParams.set('cui_safe', this._safeArea());
      this._postedPath = this._routePath || '';
      this._iframe.setAttribute('src', `${url.pathname}${url.search}`);
    }
  }

  _sync() {
    this._subscribeBadges();
    this._countUpdates();
    if (!this._iframe) return;
    this._applyBg(this._mode());
    if (!this._iframe.getAttribute('src')) this._apply();
    if (this._loaded) {
      this._postTheme();
      this._postLang();
      this._postSidebar();
      this._postSafeArea();
      this._postBadge();
    }
  }

  _subscribeBadges() {
    const conn = this._hass && this._hass.connection;
    if (!conn || conn === this._badgeConnection) return;
    this._unsubscribeBadges();
    this._badgeConnection = conn;
    this._unsubs = [];

    const notifications = {};
    this._unsubs.push(
      conn.subscribeMessage(
        (message) => {
          if (message.type === 'removed') {
            for (const id of Object.keys(message.notifications))
              delete notifications[id];
          } else {
            if (message.type === 'current')
              for (const id of Object.keys(notifications))
                delete notifications[id];
            Object.assign(notifications, message.notifications);
          }
          this._notificationCount = Object.keys(notifications).length;
          this._postBadge();
        },
        { type: 'persistent_notification/subscribe' },
      ),
    );

    if (this._hass.user && this._hass.user.is_admin) {
      const refresh = () =>
        conn
          .sendMessagePromise({ type: 'repairs/list_issues' })
          .then((result) => {
            this._issueCount = result.issues.filter(
              (issue) => !issue.ignored,
            ).length;
            this._postBadge();
          })
          .catch(() => {});
      refresh();
      this._unsubs.push(
        conn.subscribeEvents(refresh, 'repairs_issue_registry_updated'),
      );
    }
  }

  _unsubscribeBadges() {
    for (const pending of this._unsubs || [])
      pending.then((unsub) => unsub()).catch(() => {});
    this._unsubs = [];
    this._badgeConnection = null;
  }

  _countUpdates() {
    const states = this._hass && this._hass.states;
    if (!states || states === this._countedStates) return;
    this._countedStates = states;
    const entities = this._hass.entities || {};
    let count = 0;
    for (const id of Object.keys(states)) {
      if (!id.startsWith('update.')) continue;
      if (entities[id] && entities[id].hidden) continue;
      const entity = states[id];
      // UpdateEntityFeature.INSTALL
      if (
        entity.state === 'on' &&
        (entity.attributes.supported_features & 1) !== 0
      )
        count++;
    }
    if (count === this._updateCount) return;
    this._updateCount = count;
    this._postBadge();
  }

  _postBadge() {
    if (!this._loaded) return;
    const count =
      (this._notificationCount || 0) +
      (this._updateCount || 0) +
      (this._issueCount || 0);
    if (count === this._postedBadge) return;
    this._postedBadge = count;
    this._post({ type: 'cui:badge', count });
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

  _postRoute() {
    const path = this._routePath || '';
    if (path === this._postedPath) return;
    this._postedPath = path;
    this._post({ type: 'cui:navigate', path: path || '/' });
  }

  _postSidebar() {
    if (!this._loaded) return;
    const canToggle = this._canToggleMenu();
    if (canToggle === this._postedToggle) return;
    this._postedToggle = canToggle;
    this._post({ type: 'cui:sidebar', canToggle });
  }

  _postSafeArea() {
    if (!this._loaded) return;
    const insets = this._safeArea();
    if (insets === this._postedSafeArea) return;
    this._postedSafeArea = insets;
    this._post({ type: 'cui:safe-area', insets });
  }

  _post(message) {
    if (this._iframe && this._iframe.contentWindow) {
      this._iframe.contentWindow.postMessage(message, window.location.origin);
    }
  }

  _handleMessage(event) {
    if (!this._iframe || event.source !== this._iframe.contentWindow) return;
    if (event.origin !== window.location.origin) return;
    const data = event.data;
    if (!data || data.type !== 'cui:menu') return;
    this._toggleMenu(typeof data.open === 'boolean' ? data.open : undefined);
  }

  _toggleMenu(open) {
    this.dispatchEvent(
      new CustomEvent('hass-toggle-menu', {
        detail: typeof open === 'boolean' ? { open } : undefined,
        bubbles: true,
        composed: true,
      }),
    );
  }
}

customElements.define('cameraui-panel', CameraUiPanel);
