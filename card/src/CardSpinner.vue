<template>
  <svg class="cui-spin" viewBox="25 25 50 50" :style="{ width: `${size}px`, height: `${size}px` }">
    <circle class="cui-spin-circle" cx="50" cy="50" r="20" fill="none" stroke-width="5" stroke-miterlimit="10" />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 30 });
</script>
