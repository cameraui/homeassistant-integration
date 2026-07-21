import { createCameraUiPlugin } from '@camera.ui/browser';

import CameraUiCard from './CameraUiCard.vue';
import GridCard from './GridCard.vue';
import tailwind from '@/assets/tailwind.css?inline';
import { createHaCameraUiContext } from './context.js';
import { CONFIG_KEY, GRID_CONFIG_KEY, HASS_KEY } from './types.js';

import type { App, Component, InjectionKey, ShallowRef } from 'vue';
import type { CameraUiCardConfig, CameraUiGridConfig, HaCameraAttributes, HomeAssistant } from './types.js';

function entryIdFrom(hassRef: ShallowRef<HomeAssistant | undefined>, entities: string[]): string | undefined {
  for (const entity of entities) {
    const id = (hassRef.value?.states[entity]?.attributes as HaCameraAttributes | undefined)?.entry_id;
    if (id) return id;
  }
  return undefined;
}

function mountCardApp(
  el: HTMLElement,
  root: Component,
  hassRef: ShallowRef<HomeAssistant | undefined>,
  configKey: InjectionKey<unknown>,
  configRef: ShallowRef<unknown>,
  getEntryId: () => string | undefined,
): App {
  const shadow = el.shadowRoot ?? el.attachShadow({ mode: 'open' });
  shadow.innerHTML = '';
  const style = document.createElement('style');
  style.textContent = tailwind;
  const host = document.createElement('div');
  shadow.append(style, host);

  const context = createHaCameraUiContext({ getHass: () => hassRef.value, getEntryId });
  const app = createApp(root);
  app.provide(HASS_KEY, hassRef);
  app.provide(configKey, configRef);
  app.use(createCameraUiPlugin(context));
  app.mount(host);
  return app;
}

function unmountCardApp(el: HTMLElement, app: App): void {
  app.unmount();
  if (el.shadowRoot) el.shadowRoot.innerHTML = '';
}

class CameraUiCardElement extends HTMLElement {
  private app: App | null = null;
  private readonly hassRef = shallowRef<HomeAssistant | undefined>(undefined);
  private readonly configRef = shallowRef<CameraUiCardConfig | undefined>(undefined);

  public setConfig(config: CameraUiCardConfig): void {
    if (!config?.entity) {
      throw new Error('cameraui-card: "entity" is required');
    }
    this.configRef.value = config;
  }

  public set hass(hass: HomeAssistant) {
    this.hassRef.value = hass;
  }

  public get hass(): HomeAssistant | undefined {
    return this.hassRef.value;
  }

  public getCardSize(): number {
    return 5;
  }

  public static getStubConfig(): Partial<CameraUiCardConfig> {
    return { entity: '' };
  }

  public connectedCallback(): void {
    this.app ??= mountCardApp(
      this,
      CameraUiCard,
      this.hassRef,
      CONFIG_KEY as InjectionKey<unknown>,
      this.configRef as ShallowRef<unknown>,
      () => entryIdFrom(this.hassRef, this.configRef.value?.entity ? [this.configRef.value.entity] : []),
    );
  }

  public disconnectedCallback(): void {
    queueMicrotask(() => {
      if (!this.isConnected && this.app) {
        unmountCardApp(this, this.app);
        this.app = null;
      }
    });
  }
}

class CameraUiGridCardElement extends HTMLElement {
  private app: App | null = null;
  private readonly hassRef = shallowRef<HomeAssistant | undefined>(undefined);
  private readonly configRef = shallowRef<CameraUiGridConfig | undefined>(undefined);

  public setConfig(config: CameraUiGridConfig): void {
    if (!config?.cameras?.length) {
      throw new Error('cameraui-grid-card: "cameras" is required');
    }
    this.configRef.value = config;
  }

  public set hass(hass: HomeAssistant) {
    this.hassRef.value = hass;
  }

  public get hass(): HomeAssistant | undefined {
    return this.hassRef.value;
  }

  public getCardSize(): number {
    return 6;
  }

  public static getStubConfig(): Partial<CameraUiGridConfig> {
    return { cameras: [] };
  }

  public connectedCallback(): void {
    this.app ??= mountCardApp(
      this,
      GridCard,
      this.hassRef,
      GRID_CONFIG_KEY as InjectionKey<unknown>,
      this.configRef as ShallowRef<unknown>,
      () => entryIdFrom(this.hassRef, this.configRef.value?.cameras ?? []),
    );
  }

  public disconnectedCallback(): void {
    queueMicrotask(() => {
      if (!this.isConnected && this.app) {
        unmountCardApp(this, this.app);
        this.app = null;
      }
    });
  }
}

if (!customElements.get('cameraui-card')) {
  customElements.define('cameraui-card', CameraUiCardElement);
}
if (!customElements.get('cameraui-grid-card')) {
  customElements.define('cameraui-grid-card', CameraUiGridCardElement);
}

declare global {
  interface Window {
    customCards?: unknown[];
  }
}

window.customCards = window.customCards ?? [];
window.customCards.push(
  {
    type: 'cameraui-card',
    name: 'camera.ui Card',
    description: 'Live view for camera.ui cameras with WebRTC/MSE, source switching and H.265 support.',
    documentationURL: 'https://github.com/cameraui/homeassistant-integration',
  },
  {
    type: 'cameraui-grid-card',
    name: 'camera.ui Grid',
    description: 'A grid of camera.ui live views, click any tile to go live.',
    documentationURL: 'https://github.com/cameraui/homeassistant-integration',
  },
);
