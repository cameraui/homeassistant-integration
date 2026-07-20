<template>
  <div class="pointer-events-none absolute inset-0 z-10">
    <div
      v-if="hasZoom"
      ref="zoomEl"
      class="cui-ptz-track pointer-events-auto absolute bottom-16 left-3 h-28 w-10"
      @pointerdown="startZoom"
    >
      <span class="cui-ptz-mark top-1.5">+</span>
      <span class="cui-ptz-mark bottom-1.5">&minus;</span>
      <div class="cui-ptz-knob" :style="{ transform: `translate(-50%, calc(-50% + ${zoomKnob}px))` }" />
    </div>

    <div
      v-if="hasPanTilt"
      ref="padEl"
      class="cui-ptz-pad pointer-events-auto absolute bottom-16 right-3 h-24 w-24"
      @pointerdown="startPad"
    >
      <div class="cui-ptz-knob" :style="{ transform: `translate(calc(-50% + ${padKnob.x}px), calc(-50% + ${padKnob.y}px))` }">
        <IconHome v-if="hasHome" class="cui-ptz-knob-icon" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { HASS_KEY } from './types.js';

import IconHome from '~icons/mdi/home-outline';

const props = defineProps<{
  entity: string;
  caps: string[];
}>();

const hass = inject(HASS_KEY);

const PAD_RADIUS = 36;
const ZOOM_RANGE = 44;
const TAP_THRESHOLD = 6;
const THROTTLE_MS = 200;
const CHANGE_THRESHOLD = 0.05;

const padEl = ref<HTMLElement>();
const zoomEl = ref<HTMLElement>();
const padKnob = reactive({ x: 0, y: 0 });
const zoomKnob = ref(0);

const hasPan = computed(() => props.caps.includes('pan'));
const hasTilt = computed(() => props.caps.includes('tilt'));
const hasZoom = computed(() => props.caps.includes('zoom'));
const hasHome = computed(() => props.caps.includes('home'));
const hasPanTilt = computed(() => hasPan.value || hasTilt.value);

let lastSent = 0;
let lastVel = { pan: 0, tilt: 0, zoom: 0 };
let dragging = false;

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}

function callPtz(data: Record<string, unknown>): void {
  void hass?.value?.callService('cameraui', 'ptz', data, { entity_id: props.entity });
}

function sendVelocity(pan: number, tilt: number, zoom: number): void {
  const now = Date.now();
  const changed =
    Math.abs(pan - lastVel.pan) > CHANGE_THRESHOLD || Math.abs(tilt - lastVel.tilt) > CHANGE_THRESHOLD || Math.abs(zoom - lastVel.zoom) > CHANGE_THRESHOLD;
  if (!changed || now - lastSent < THROTTLE_MS) return;
  lastSent = now;
  lastVel = { pan, tilt, zoom };
  callPtz({ action: 'continuous', pan, tilt, zoom });
}

function stop(): void {
  if (!dragging) return;
  dragging = false;
  lastVel = { pan: 0, tilt: 0, zoom: 0 };
  callPtz({ action: 'stop' });
}

function startPad(event: PointerEvent): void {
  const el = padEl.value;
  if (!el) return;
  el.setPointerCapture(event.pointerId);
  const rect = el.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;
  let moved = false;

  const move = (moveEvent: PointerEvent): void => {
    let dx = moveEvent.clientX - cx;
    let dy = moveEvent.clientY - cy;
    if (!moved && Math.hypot(dx, dy) < TAP_THRESHOLD) return;
    moved = true;
    dragging = true;
    const dist = Math.hypot(dx, dy);
    if (dist > PAD_RADIUS) {
      dx = (dx / dist) * PAD_RADIUS;
      dy = (dy / dist) * PAD_RADIUS;
    }
    padKnob.x = dx;
    padKnob.y = dy;
    sendVelocity(hasPan.value ? round2(dx / PAD_RADIUS) : 0, hasTilt.value ? round2(-dy / PAD_RADIUS) : 0, 0);
  };

  const end = (): void => {
    el.removeEventListener('pointermove', move);
    el.removeEventListener('pointerup', end);
    el.removeEventListener('pointercancel', end);
    padKnob.x = 0;
    padKnob.y = 0;
    if (moved) stop();
    else if (hasHome.value) callPtz({ action: 'home' });
  };

  el.addEventListener('pointermove', move);
  el.addEventListener('pointerup', end);
  el.addEventListener('pointercancel', end);
}

function startZoom(event: PointerEvent): void {
  const el = zoomEl.value;
  if (!el) return;
  el.setPointerCapture(event.pointerId);
  const rect = el.getBoundingClientRect();
  const cy = rect.top + rect.height / 2;

  const move = (moveEvent: PointerEvent): void => {
    dragging = true;
    const dy = Math.max(-ZOOM_RANGE, Math.min(ZOOM_RANGE, moveEvent.clientY - cy));
    zoomKnob.value = dy;
    sendVelocity(0, 0, round2(-dy / ZOOM_RANGE));
  };

  const end = (): void => {
    el.removeEventListener('pointermove', move);
    el.removeEventListener('pointerup', end);
    el.removeEventListener('pointercancel', end);
    zoomKnob.value = 0;
    stop();
  };

  el.addEventListener('pointermove', move);
  el.addEventListener('pointerup', end);
  el.addEventListener('pointercancel', end);
}

onBeforeUnmount(stop);
</script>
