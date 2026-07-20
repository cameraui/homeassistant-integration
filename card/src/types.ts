import type { StreamingRole } from '@camera.ui/sdk';
import type { VideoStreamingMode } from '@camera.ui/browser';
import type { InjectionKey, ShallowRef } from 'vue';

export interface HassEntityState {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
}

export interface HomeAssistant {
  states: Record<string, HassEntityState | undefined>;
  language?: string;
  callWS<T>(message: Record<string, unknown>): Promise<T>;
  callService(domain: string, service: string, data?: Record<string, unknown>, target?: Record<string, unknown>): Promise<unknown>;
  hassUrl(path?: string): string;
}

export interface CameraUiCardConfig {
  type: string;
  entity: string;
  title?: string;
  source?: StreamingRole;
  mode?: VideoStreamingMode;
  autostart?: boolean;
  snapshot_interval?: number;
}

export interface CameraUiGridConfig {
  type: string;
  cameras: string[];
  columns?: number;
  source?: StreamingRole;
  mode?: VideoStreamingMode;
  autostart?: boolean;
}

export interface HaCameraAttributes {
  camera_name?: string;
  entry_id?: string;
  sources?: { id?: string; name?: string; role?: string }[];
  ptz?: string[];
  friendly_name?: string;
  entity_picture?: string;
}

export const HASS_KEY: InjectionKey<Readonly<ShallowRef<HomeAssistant | undefined>>> = Symbol('cameraui-card-hass');
export const CONFIG_KEY: InjectionKey<Readonly<ShallowRef<CameraUiCardConfig | undefined>>> = Symbol('cameraui-card-config');
export const GRID_CONFIG_KEY: InjectionKey<Readonly<ShallowRef<CameraUiGridConfig | undefined>>> = Symbol('cameraui-grid-config');
