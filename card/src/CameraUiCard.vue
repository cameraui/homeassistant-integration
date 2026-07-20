<template>
  <ha-card class="overflow-hidden">
    <CardPlayer
      v-if="!problem"
      :attributes="attributes"
      :entity="config?.entity"
      :poster="poster"
      :title="title"
      :source="config?.source"
      :mode="config?.mode"
      :autostart="config?.autostart"
      :snapshot-interval="config?.snapshot_interval"
      :lang="hass?.language"
    />
    <div v-else class="flex items-center gap-2 p-4 text-[color:var(--error-color,#db4437)]">
      <IconAlert class="h-5 w-5 shrink-0" />
      <span>{{ problem }}</span>
    </div>
  </ha-card>
</template>

<script setup lang="ts">
import CardPlayer from './CardPlayer.vue';
import { CONFIG_KEY, HASS_KEY } from './types.js';

import IconAlert from '~icons/mdi/alert-circle-outline';

import type { HaCameraAttributes } from './types.js';

const hass = inject(HASS_KEY)!;
const config = inject(CONFIG_KEY)!;

const stateObj = computed(() => {
  const entity = config.value?.entity;
  return entity ? hass.value?.states[entity] : undefined;
});

const attributes = computed(() => (stateObj.value?.attributes ?? {}) as HaCameraAttributes);

const problem = computed(() => {
  if (!config.value?.entity) return 'No entity configured';
  if (!stateObj.value) return `Entity not found: ${config.value.entity}`;
  if (!attributes.value.camera_name || !attributes.value.entry_id || !attributes.value.sources?.length) {
    return 'Not a camera.ui camera entity';
  }
  return '';
});

const title = computed(() => config.value?.title ?? attributes.value.friendly_name ?? attributes.value.camera_name);
const poster = computed(() => attributes.value.entity_picture);
</script>
