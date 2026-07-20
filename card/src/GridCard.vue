<template>
  <ha-card class="overflow-hidden">
    <div v-if="!cells.length" class="p-4 text-[color:var(--secondary-text-color,#727272)]">No cameras configured</div>
    <div v-else class="grid gap-px bg-black" :style="{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }">
      <CardPlayer
        v-for="cell in cells"
        :key="cell.entity"
        :attributes="cell.attributes"
        :entity="cell.entity"
        :title="cell.title"
        :source="config?.source"
        :mode="config?.mode"
        :autostart="config?.autostart"
        :lang="hass?.language"
      />
    </div>
  </ha-card>
</template>

<script setup lang="ts">
import CardPlayer from './CardPlayer.vue';
import { GRID_CONFIG_KEY, HASS_KEY } from './types.js';

import type { HaCameraAttributes } from './types.js';

const hass = inject(HASS_KEY);
const config = inject(GRID_CONFIG_KEY);

const cells = computed(() => {
  const h = hass?.value;
  return (config?.value?.cameras ?? [])
    .map((entity) => {
      const state = h?.states[entity];
      if (!state) return undefined;
      const attributes = state.attributes as HaCameraAttributes;
      return { entity, attributes, title: attributes.friendly_name ?? attributes.camera_name ?? entity };
    })
    .filter((cell): cell is { entity: string; attributes: HaCameraAttributes; title: string } => cell !== undefined);
});

const columns = computed(() => {
  const configured = config?.value?.columns;
  if (configured && configured > 0) return configured;
  const count = cells.value.length;
  if (count <= 1) return 1;
  if (count <= 4) return 2;
  return 3;
});
</script>
