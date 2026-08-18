<script setup lang="ts">
import { formatMonth } from '@/utils/formatMonth'

defineProps<{
  /** Available months, newest first, as `YYYY-MM-DD`. */
  months: string[]
  selected: string
}>()

const emit = defineEmits<{ select: [month: string] }>()

function onChange(event: Event) {
  emit('select', (event.target as HTMLSelectElement).value)
}
</script>

<template>
  <div class="month-picker">
    <label for="month-picker-select">Hónap</label>
    <select
      id="month-picker-select"
      :value="selected"
      :disabled="months.length === 0"
      @change="onChange"
    >
      <option v-if="months.length === 0" value="">Nincs elérhető hónap</option>
      <option v-for="month in months" :key="month" :value="month">
        {{ formatMonth(month) }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.month-picker {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin: 0 0 1.75rem;
}

label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b6b6b;
}

select {
  font: inherit;
  font-size: 0.95rem;
  padding: 0.45rem 0.7rem;
  border: 1px solid #ddd6cd;
  border-radius: 0.4rem;
  background: #fff;
  color: inherit;
  cursor: pointer;
}

select:disabled {
  cursor: default;
  color: #9a9a9a;
  background: #f5f2ee;
}

select:focus-visible {
  outline: 2px solid #e8590c;
  outline-offset: 1px;
}
</style>
