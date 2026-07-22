import type { ReactiveCameraDevice } from '@camera.ui/browser';
import type { AudioStreamInfo, Camera, CameraSource, ProbeStream, SensorType, StreamingRole, VideoStreamInfo } from '@camera.ui/sdk';
import type { ComputedRef } from 'vue';
import type { HaCameraAttributes, HomeAssistant } from './types.js';

export function createHaCameraDevice(attributes: ComputedRef<HaCameraAttributes>, getHass: () => HomeAssistant | undefined): ReactiveCameraDevice {
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

  async function probeStream(sourceId?: string): Promise<ProbeStream | undefined> {
    const hass = getHass();
    const attrs = attributes.value;
    const cameraName = attrs.camera_name;
    const entryId = attrs.entry_id;
    if (!hass || !cameraName || !entryId) return undefined;

    const source = attrs.sources?.find((s) => (s.id ?? s.name) === sourceId) ?? attrs.sources?.[0];
    const sourceName = source?.name ?? source?.id;
    if (!sourceName) return undefined;

    const path = `/api/cameraui/probe/${entryId}/${encodeURIComponent(cameraName)}/${encodeURIComponent(sourceName)}`;
    try {
      const signed = await hass.callWS<{ path: string }>({ type: 'auth/sign_path', path, expires: 30 });
      const res = await fetch(hass.hassUrl(signed.path));
      if (!res.ok) return undefined;
      const flags = (await res.json()) as { has_backchannel?: boolean; has_audio?: boolean; has_video?: boolean };
      const audio: AudioStreamInfo[] = [];
      if (flags.has_audio) audio.push({ direction: 'sendonly' } as AudioStreamInfo);
      if (flags.has_backchannel) audio.push({ direction: 'recvonly' } as AudioStreamInfo);
      const video: VideoStreamInfo[] = flags.has_video ? [{ direction: 'sendonly' } as VideoStreamInfo] : [];
      return { sdp: '', audio, video } as ProbeStream;
    } catch {
      return undefined;
    }
  }

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
    probeStream,
    streamUrl: async () => undefined,
    refreshStates: async () => {},
    reconnect: async () => {},
    close: async () => {},
  };

  return device as unknown as ReactiveCameraDevice;
}
