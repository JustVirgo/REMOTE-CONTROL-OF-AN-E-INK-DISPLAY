<template>
    <div v-if="isEmptyData(data)"> - </div>
    <div v-else>
      <table class="w-full" :style="tableStyle">
        <thead>
          <tr v-if="showKeys">
            <th class="p-1" :style="cellStyle">Key</th>
            <th class="p-1" :style="cellStyle">Value</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(val, key) in data" :key="key">
            <td v-if="showKeys" class="align-top" :style="cellStyle">{{ key }}</td>
            <td class="p-1" :style="cellStyle">
              <template v-if="isTableStructure(val)">
                <table class="w-full text-sm" :style="tableStyle">
                  <thead>
                    <tr>
                      <th
                        v-for="(col, idx) in Object.keys(val[Object.keys(val)[0]])"
                        :key="idx"
                        class="capitalize pr-1"
                        :style="headerCellStyle"
                      >
                        {{ col.replaceAll('_', ' ') }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(entry, index) in val" :key="index">
                      <td
                        v-for="(col, idx) in Object.keys(entry)"
                        :key="idx"
                        class="p-0.5"
                        :style="cellStyle"
                      >
                        <div v-if="isSimpleVal(entry[col])">
                          {{ entry[col] }}
                        </div>
                        <div v-else>
                          <WidgetDataRenderer :data="entry[col]" :fontSize="fontSize" :fontFamily="fontFamily" :showKeys="false" />
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </template>
  
              <template v-else-if="typeof val === 'object' && val !== null">
                <WidgetDataRenderer :data="val" :fontSize="fontSize" :fontFamily="fontFamily" :showKeys="false" />
              </template>
  
              <template v-else>
                {{ Array.isArray(val) ? val.join(', ') : val }}
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import WidgetDataRenderer from './WidgetDataRenderer.vue'; // self-recursive
  
  const props = defineProps({
    data: { type: Object, required: true },
    fontSize: { type: [String, Number], default: 14 },
    fontFamily: { type: String, default: 'Arial' },
    showKeys: { type: Boolean, default: true }
  });
  
  const isEmptyData = (data) => {
    if (Array.isArray(data)) return data.length === 0;
    if( data === null) return true;
    return typeof data === 'object' && data !== null && Object.keys(data).length === 0;
  };
  
  const isSimpleVal = (val) => typeof val !== 'object';
  
  const isTableStructure = (data) => {
    if (typeof data !== 'object' || data === null) return false;
    const entries = Array.isArray(data) ? data : Object.values(data);
    if (!entries.length || entries[0] === null) return false;
    if (entries.length === 1) return true;
  
    const keys = Object.keys(entries[0]);
    return entries.every(entry =>
      typeof entry === 'object' &&
      entry !== null &&
      JSON.stringify(Object.keys(entry).sort()) === JSON.stringify(keys.sort())
    );
  };
  
  const normalizeFontSize = computed(() => {
  const size = Number(props.fontSize);
  return isNaN(size) ? '16px' : `${size}px`; // fallback to 16px if invalid
});

  const tableStyle = computed(() => ({
    backgroundColor: 'transparent',
    borderCollapse: 'collapse',
    fontSize: normalizeFontSize.value,
    fontFamily: props.fontFamily,
  }));
  
  const cellStyle = computed(() => ({
    backgroundColor: 'transparent',
    fontSize: normalizeFontSize.value,
    fontFamily: props.fontFamily,
  }));

  const headerCellStyle = computed(() => ({
    ...cellStyle.value,
    fontWeight: '700',                             // tells non-variable browsers
    fontVariationSettings: "'wght' 700",           // picks the bold axis
  }));
  </script>

  
  <style scoped>
  table {
    border: none;
  }
  th, td {
    border: none;
    text-align: center;
    vertical-align: top;
  }
  </style>
  