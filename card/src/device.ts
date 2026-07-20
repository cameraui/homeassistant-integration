import type { ReactiveCameraDevice } from '@camera.ui/browser';
import type { Camera, CameraSource, SensorType, StreamingRole } from '@camera.ui/sdk';
import type { ComputedRef } from 'vue';
import type { HaCameraAttributes } from './types.js';

export function createHaCameraDevice(attributes: ComputedRef<HaCameraAttributes>): ReactiveCameraDevice {
  const name = computed(() => attributes.value.camera_name ?? '');
  const sources = computed<CameraSource[]>(() =>
    (attributes.value.sources ?? []).map(
      (source) =>
        ({
          _id: source.id ?? source.name ?? '',
          name: source.name,
          role: source.role,
        }) as CameraSource,
    ),
  );

  function byRole(role: StreamingRole): ComputedRef<CameraSource | undefined> {
    return computed(() => sources.value.find((source) => source.role === role));
  }

  const highResolutionSource = byRole('high-resolution');
  const midResolutionSource = byRole('mid-resolution');
  const lowResolutionSource = byRole('low-resolution');
  const never = computed(() => false);

  const device = {
    id: attributes.value.camera_name ?? 'cameraui-card',
    name,
    room: ref(''),
    nativeId: ref<string | undefined>(undefined),
    disabled: ref(false),
    snooze: ref(false),
    isCloud: ref(false),

    connected: ref(true),
    frameWorkerConnected: ref(false),

    sources,
    streamSource: computed(() => highResolutionSource.value ?? sources.value[0]),
    snapshotSource: computed(() => undefined),
    highResolutionSource,
    midResolutionSource,
    lowResolutionSource,

    capabilities: ref<SensorType[]>([]),
    hasLight: never,
    hasSiren: never,
    hasDoorbell: never,
    hasBattery: never,
    hasAudioSensor: never,
    hasMotionSensor: never,
    hasObjectSensor: never,
    hasPtz: never,

    camera: shallowRef({} as Camera),

    snapshot: shallowRef<ArrayBuffer | undefined>(undefined),
    snapshotLoading: ref(false),

    fetchSnapshot: async () => undefined,
    probeStream: async () => undefined,
    streamUrl: async () => undefined,
    refreshStates: async () => {},
    reconnect: async () => {},
    close: async () => {},
  };

  return device as unknown as ReactiveCameraDevice;
}
