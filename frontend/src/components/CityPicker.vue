<script setup lang="ts">
defineProps<{
  /** Sorted city names for the selected county. */
  cities: string[]
  county: string | null
  selected: string | null
}>()

const emit = defineEmits<{ select: [city: string | null] }>()

function onChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  emit('select', value === '' ? null : value)
}
</script>

<template>
  <div class="city-picker">
    <label v-if="county === 'Budapest'" for="city-picker-select">Kerület</label>
    <label v-else for="city-picker-select">Város</label>
    <select
      id="city-picker-select"
      :value="selected ?? ''"
      :disabled="cities.length === 0"
      @change="onChange"
    >
      <option v-if="cities.length === 0 && county === 'Budapest'" value="">Nincs elérhető kerület</option>
      <option v-else-if="cities.length === 0 && county !== 'Budapest'" value="">Nincs elérhető város</option>
      <option v-else-if="cities.length !== 0 && county === 'Budapest'" value="">Válassz kerületet</option>
      <option v-else value="">Válassz várost</option>
      <option v-for="city in cities" :key="city" :value="city">
        {{ city }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.city-picker {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin: 1.75rem 0;
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
