<template>
  <div
    ref="wrapperEl"
    class="cui-player group relative aspect-video w-full overflow-hidden bg-black"
    @pointermove="revealControls"
    @pointerdown="revealControls"
    @pointerleave="onPointerLeave"
  >
    <div ref="containerEl" class="absolute inset-0" />

    <img
      v-if="(!live || !hasVideo) && snapshotSrc"
      class="absolute inset-0 h-full w-full object-cover"
      :src="snapshotSrc"
      alt=""
      @load="onSnapshotLoad"
      @error="onSnapshotError"
    />

    <div v-if="(!live || !hasVideo) && !snapshotSrc" class="pointer-events-none absolute inset-0 flex items-center justify-center">
      <img :src="logoUrl" class="h-1/3 max-h-20 w-auto opacity-20" alt="" />
    </div>

    <button
      v-if="!live"
      type="button"
      class="group/tap absolute inset-0 flex cursor-pointer items-center justify-center bg-transparent transition-colors hover:bg-black/20"
      :aria-label="`Go live: ${title ?? ''}`"
      @click="goLive"
    >
      <span
        class="flex h-14 w-14 items-center justify-center rounded-full bg-black/45 pl-1 text-white transition group-hover/tap:scale-105"
      >
        <IconPlay class="h-7 w-7" />
      </span>
    </button>

    <div class="pointer-events-none absolute bottom-2.5 left-2.5 flex items-center">
      <span v-if="snapshotLoading && !snapshotAt && !live" class="flex h-6 w-6 items-center justify-center rounded-[10px] bg-black/50">
        <CardSpinner :size="14" />
      </span>
      <span v-else-if="snapshotAge" class="rounded-[10px] bg-black/50 px-2 py-0.5 text-xs font-semibold text-white">{{ snapshotAge }}</span>
    </div>

    <div v-if="showSpinner" class="pointer-events-none absolute inset-0 z-20 flex items-center justify-center">
      <CardSpinner :size="30" />
    </div>
    <div
      v-else-if="live && status === 'error'"
      class="pointer-events-none absolute inset-0 z-20 flex flex-col items-center justify-center gap-2 px-4 text-center text-white/60"
    >
      <IconVideoOff class="h-10 w-10" />
      <span class="text-xs">{{ error?.message || 'Stream unavailable' }}</span>
    </div>

    <div
      class="pointer-events-none absolute inset-x-0 top-0 flex items-center gap-2 bg-gradient-to-b from-black/55 to-transparent px-3 py-2.5 pr-28 text-sm font-medium text-white transition-opacity"
      :class="controlsClass"
    >
      <span v-if="showLiveDot" class="inline-flex h-2 w-2 flex-none rounded-full bg-[#f5222d]" :class="{ 'animate-pulse !bg-[#ff9800]': isReconnecting }" />
      <span v-if="title" class="overflow-hidden text-ellipsis whitespace-nowrap">{{ title }}</span>
    </div>

    <div v-if="live && showPills" class="absolute right-2 top-2 z-10 flex items-center gap-1 transition-opacity" :class="controlsClass">
      <button v-if="availableRoles.length > 1" :class="pillBtn" @click="cycleResolution">{{ RESOLUTION_LABELS[activeResolution] ?? activeResolution }}</button>
      <button :class="pillBtn" @click="cycleMode">{{ modeLabel }}</button>
    </div>

    <div
      v-if="live"
      class="absolute inset-x-0 bottom-0 flex items-center gap-0.5 bg-gradient-to-t from-black/70 via-black/40 to-transparent px-2 pb-2 pt-8 text-white transition-opacity"
      :class="controlsClass"
    >
      <button :class="iconBtn" title="Pause" @click="togglePlay"><IconPause class="h-[18px] w-[18px]" /></button>
      <span class="flex-1" />
      <button v-if="ptzCaps.length && hasVideo && ptzRoom" :class="[iconBtn, showPtz && 'bg-white/20']" title="PTZ" @click="showPtz = !showPtz">
        <IconPtz class="h-[18px] w-[18px]" />
      </button>
      <button v-if="hasAudio && showMute" :class="iconBtn" :title="muted ? 'Unmute' : 'Mute'" @click="toggleMute">
        <IconMute v-if="muted" class="h-[18px] w-[18px]" />
        <IconVolume v-else class="h-[18px] w-[18px]" />
      </button>
      <button v-if="hasIntercom && showMute" :class="[iconBtn, micActive && 'bg-white/20']" :title="micActive ? 'Stop talking' : 'Talk'" @click="toggleMic">
        <IconMic class="h-[18px] w-[18px]" />
      </button>
      <button v-if="pipSupported && showPip" :disabled="!hasVideo" :class="iconBtn" @click="stream.togglePip()">
        <IconPipOn v-if="isPip" class="h-[18px] w-[18px]" />
        <IconPipOff v-else class="h-[18px] w-[18px]" />
      </button>
      <button :class="iconBtn" @click="toggleFullscreen">
        <IconFullscreenExit v-if="isFullscreen" class="h-[18px] w-[18px]" />
        <IconFullscreen v-else class="h-[18px] w-[18px]" />
      </button>
    </div>

    <CardPtz v-if="entity && ptzCaps.length && hasVideo && showPtz && ptzRoom" :entity="entity" :caps="ptzCaps" />
  </div>
</template>

<script setup lang="ts">
import { useCameraStream } from '@camera.ui/browser';

import logoUrl from '@/assets/logo.svg?url';
import CardPtz from './CardPtz.vue';
import CardSpinner from './CardSpinner.vue';
import { createHaCameraDevice } from './device.js';
import { HASS_KEY } from './types.js';

import IconPause from '~icons/basil/pause-solid';
import IconPlay from '~icons/basil/play-solid';
import IconPipOn from '~icons/fluent/picture-in-picture-16-filled';
import IconPipOff from '~icons/fluent/picture-in-picture-16-regular';
import IconVideoOff from '~icons/fluent/video-off-32-filled';
import IconMic from '~icons/heroicons/microphone-16-solid';
import IconVolume from '~icons/heroicons/speaker-wave-16-solid';
import IconMute from '~icons/heroicons/speaker-x-mark-16-solid';
import IconPtz from '~icons/mdi/arrow-all';
import IconFullscreenExit from '~icons/mingcute/fullscreen-exit-fill';
import IconFullscreen from '~icons/mingcute/fullscreen-fill';

import type { VideoStreamingMode } from '@camera.ui/browser';
import type { StreamingRole } from '@camera.ui/sdk';
import type { HaCameraAttributes } from './types.js';

const props = defineProps<{
  attributes: HaCameraAttributes;
  entity?: string;
  poster?: string;
  title?: string;
  source?: StreamingRole;
  mode?: VideoStreamingMode;
  autostart?: boolean;
  snapshotInterval?: number;
  lang?: string;
}>();

const hass = inject(HASS_KEY);

const device = createHaCameraDevice(
  computed(() => props.attributes),
  () => hass?.value,
);
const stream = useCameraStream({
  camera: device,
  mode: props.mode ?? 'auto',
  resolution: props.source ?? 'high-resolution',
  autoStart: false,
  videoClass: 'cui-video',
  isolated: true,
});

const { status, isReconnecting, activeMode, activeResolution, muted, isPip, nativeWidth, error, hasIntercom, hasAudio } = stream;

const RESOLUTION_LABELS: Record<string, string> = {
  'high-resolution': 'HD',
  'mid-resolution': 'MD',
  'low-resolution': 'SD',
};
const iconBtn =
  'flex h-9 w-9 shrink-0 cursor-pointer items-center justify-center rounded-md text-white transition-colors hover:bg-white/15 disabled:cursor-default disabled:opacity-40';
const pillBtn = 'flex h-7 cursor-pointer items-center rounded-md bg-black/40 px-2 text-[11px] font-semibold text-white transition-colors hover:bg-black/60';
const pipSupported = typeof document !== 'undefined' && document.pictureInPictureEnabled;

let userMediaStream: MediaStream | undefined;

const wrapperEl = useTemplateRef<HTMLElement>('wrapperEl');
const containerEl = useTemplateRef<HTMLElement>('containerEl');
const { width: cardWidth } = useElementSize(wrapperEl);
const nowTick = useTimestamp({ interval: 1000 });

const live = ref(props.autostart ?? false);
const isFullscreen = ref(false);
const showPtz = ref(false);
const requestedMode = ref(props.mode ?? 'auto');
const snapshotSrc = ref(props.poster);
const snapshotAt = ref(0);
const snapshotLoading = ref(false);
const micActive = ref(false);
const controlsVisible = ref(false);

const ptzCaps = computed(() => props.attributes.ptz ?? []);
const hasVideo = computed(() => nativeWidth.value > 0);
const showPills = computed(() => cardWidth.value === 0 || cardWidth.value >= 300);
const showPip = computed(() => cardWidth.value === 0 || cardWidth.value >= 260);
const showMute = computed(() => cardWidth.value === 0 || cardWidth.value >= 200);
const ptzRoom = computed(() => cardWidth.value >= 340);
const showSpinner = computed(() => live.value && !hasVideo.value && status.value !== 'error');
const showLiveDot = computed(() => live.value && hasVideo.value);
const controlsClass = computed(() => (controlsVisible.value ? 'opacity-100' : 'opacity-0 pointer-events-none'));
const snapshotIntervalMs = computed(() => Math.max(2, props.snapshotInterval ?? 10) * 1000);

const availableRoles = computed(() => {
  const roles = (props.attributes.sources ?? []).map((source) => source.role).filter((role): role is string => !!role);
  return roles.filter((role) => role in RESOLUTION_LABELS);
});

const modeLabel = computed(() => {
  if (requestedMode.value === 'auto') return 'AUTO';
  return activeMode.value === 'mse' ? 'MSE' : 'WebRTC';
});

const snapshotAge = computed(() => {
  if (live.value || !snapshotAt.value) return '';
  const seconds = Math.max(0, Math.floor((nowTick.value - snapshotAt.value) / 1000));
  if (seconds < 1) return props.lang?.startsWith('de') ? 'Jetzt' : 'now';
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h`;
});

async function refreshSnapshot(): Promise<void> {
  const h = hass?.value;
  const entryId = props.attributes.entry_id;
  const name = props.attributes.camera_name;
  if (!h || !entryId || !name) return;

  snapshotLoading.value = true;
  const path = `/api/cameraui/snapshot/${entryId}/${encodeURIComponent(name)}?t=${Date.now()}`;
  try {
    const signed = await h.callWS<{ path: string }>({ type: 'auth/sign_path', path, expires: 60 });
    snapshotSrc.value = h.hassUrl(signed.path);
  } catch {
    snapshotLoading.value = false;
  }
}

const snapshotLoop = useIntervalFn(refreshSnapshot, snapshotIntervalMs, { immediate: false });

// touch has no hover, so controls are a reactive layer: any pointer activity reveals them, a timer hides them
const { start: armHideControls, stop: cancelHideControls } = useTimeoutFn(() => (controlsVisible.value = false), 3000, {
  immediate: false,
});

function revealControls(): void {
  controlsVisible.value = true;
  armHideControls();
}

function onPointerLeave(event: PointerEvent): void {
  if (event.pointerType === 'mouse') {
    cancelHideControls();
    controlsVisible.value = false;
  }
}

function onSnapshotLoad(): void {
  snapshotAt.value = Date.now();
  snapshotLoading.value = false;
}

function onSnapshotError(): void {
  snapshotSrc.value = undefined;
  snapshotAt.value = 0;
  snapshotLoading.value = false;
}

function goLive(): void {
  live.value = true;
}

function togglePlay(): void {
  live.value = !live.value;
}

async function toggleFullscreen(): Promise<void> {
  if (document.fullscreenElement) {
    await document.exitFullscreen();
    return;
  }
  const video = stream.videoElement.value;
  if (video) {
    video.controls = true;
    await video.requestFullscreen().catch(() => (video.controls = false));
  } else {
    await wrapperEl.value?.requestFullscreen();
  }
}

function cycleResolution(): void {
  const roles = availableRoles.value;
  if (roles.length < 2) return;
  const index = roles.indexOf(activeResolution.value);
  const next = roles[(index + 1) % roles.length] as StreamingRole;
  stream.setResolution(next);
}

function cycleMode(): void {
  const order: VideoStreamingMode[] = ['auto', 'webrtc', 'mse'];
  const next = order[(order.indexOf(requestedMode.value) + 1) % order.length];
  requestedMode.value = next;
  stream.setMode(next);
}

function toggleMute(): void {
  stream.setMuted(!muted.value);
}

function stopMic(): void {
  if (!micActive.value) return;
  micActive.value = false;
  userMediaStream?.getTracks().forEach((track) => track.stop());
  userMediaStream = undefined;
  stream.setMicrophone(null);
}

async function toggleMic(): Promise<void> {
  if (micActive.value) {
    stopMic();
    return;
  }
  if (!hasIntercom.value) return;
  try {
    userMediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    await stream.setMicrophone(userMediaStream.getAudioTracks()[0] ?? null);
    micActive.value = true;
  } catch {
    userMediaStream?.getTracks().forEach((track) => track.stop());
    userMediaStream = undefined;
  }
}

function onFullscreenChange(): void {
  isFullscreen.value = !!document.fullscreenElement;
  if (!document.fullscreenElement) {
    const video = stream.videoElement.value;
    if (video) video.controls = false;
  }
}

watchEffect(() => {
  stream.containerElement.value = containerEl.value ?? undefined;
});

watch(
  live,
  (on) => {
    if (on) {
      stream.start();
      snapshotLoop.pause();
    } else {
      stopMic();
      stream.stop();
      snapshotAt.value = 0;
      refreshSnapshot();
      snapshotLoop.resume();
    }
  },
  { immediate: true },
);

useEventListener(document, 'fullscreenchange', onFullscreenChange);
onBeforeUnmount(stopMic);
</script>
