<template>
    <div>
      <label class="block mb-1">Field:</label>
      <select v-model="fieldPath[0]" @change="onFieldChange(0)" class="input mb-1">
        <option disabled value="">Select...</option>
        <option
          v-for="([key, val]) in filteredRootFields"
          :key="key"
          :value="key"
        >
          {{ key }} ({{ typeof val }})
        </option>
      </select>
      <label v-if="(fieldPath[0] && canDrillDeeper) || fieldPath.length > 1" class="block text-gray-500">(subfields are optional)</label>
      <div
      v-for="(field, i) in fieldPath.slice(1)"
      :key="'sub-' + i"
      >
        <select
          v-model="fieldPath[i + 1]"
          @change="onFieldChange(i + 1)"
          class="input mb-1"
        >
          <option disabled value="">Select...</option>
          <option
            v-for="([key, val]) in filteredSubFields(i + 1)"
            :key="key"
            :value="key"
          >
            {{ key }} ({{ typeof val }})
          </option>
        </select>
      </div>
  
      <div v-if="fieldPath[0] && canDrillDeeper" class="mt-2">
        <select v-model="nextField" @change="addToPath" class="input mb-2">
          <option disabled value="">Select subfield…</option>
          <option
            v-for="([key, val]) in filteredSubFields(fieldPath.length)"
            :key="key"
            :value="key"
          >
            {{ key }} ({{ typeof val }})
          </option>
        </select>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  
  const props = defineProps({
    modelValue: String,
    sourceUid: [String, Number],
    dataSources: Array,
    allowedTypes: {
      type: Array,
      default: () => ['number']
    }
  });
  const emit = defineEmits(['update:modelValue']);
  
  const fieldPath = ref(
    props.modelValue ? props.modelValue.split('%') : []
  );
  const nextField = ref('');
  
  // update parent the instant
  function updateParent() {
    emit('update:modelValue', fieldPath.value.join('%'));
  }
  
  const selectedSource = computed(() =>
    props.dataSources.find(s => s.uid == props.sourceUid)
  );
  
  // root-level entries always show objects plus any allowed primitive
  const filteredRootFields = computed(() => {
    const d = selectedSource.value?.data || {};
    return Object.entries(d)
      .filter(([k,v]) =>
        typeof v === 'object' ||
        props.allowedTypes.includes(typeof v)
      );
  });
  
  const selectedValue = computed(() => {
    let cur = selectedSource.value?.data;
    for (const key of fieldPath.value) {
      if (cur && typeof cur === 'object') cur = cur[key];
      else return null;
    }
    return cur;
  });
  
  const canDrillDeeper = computed(() =>
    selectedValue.value &&
    typeof selectedValue.value === 'object' &&
    !Array.isArray(selectedValue.value)
  );
  
  function filteredSubFields(depth) {
    let cur = selectedSource.value?.data;
    for (let i = 0; i < depth; i++) {
      cur = cur?.[fieldPath.value[i]];
    }
    if (cur && typeof cur === 'object') {
      return Object.entries(cur)
        .filter(([k,v]) =>
          typeof v === 'object' ||
          props.allowedTypes.includes(typeof v)
        );
    }
    return [];
  }
  
  function onFieldChange(idx) {
    fieldPath.value = fieldPath.value.slice(0, idx + 1);
    nextField.value = '';
    updateParent();
  }
  
  function addToPath() {
    if (!nextField.value) return;
    fieldPath.value.push(nextField.value);
    nextField.value = '';
    updateParent();
  }
  </script>
  
  <style scoped>
  @reference "tailwindcss";
  .input {
    @apply w-full p-1.5 my-0.5 rounded bg-white text-base;
  }
  </style>
  