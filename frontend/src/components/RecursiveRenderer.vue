<template>
  <div v-if="isEmptyData(data)" > - </div>
  <div v-else>
    <table class="w-full bg-gray-100">
      <thead class="bg-gray-300">
        <tr v-if="showkey">
            <th class="p-2 border">Key</th>
            <th class="p-2 border">Value</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(val, key) in data" :key="key">
          <td v-if="showkey" class="p-2 border align-top">{{ key }}</td>
          <td class="p-2 border">
            <template v-if="isTableStructure(val)">
              <table class="w-full text-sm bg-white border">
                <thead class="bg-gray-200">
                  <tr>
                    <th
                      v-for="(col, idx) in Object.keys(val[Object.keys(val)[0]])"
                      :key="idx"
                      class="p-1 border capitalize"
                    >
                      {{ col.replaceAll('_', ' ') }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(entry, index) in val" :key="index">
                    <td v-for="(col, idx) in Object.keys(entry)" :key="idx" class="p-1 border">
                      <div v-if="isSimpleVal(entry[col])">
                        {{ entry[col] }}
                      </div>
                      <div v-else>
                        <RecursiveRenderer :data="entry[col]" />
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </template>

            <template v-else-if="typeof val === 'object' && val !== null">
              <RecursiveRenderer :data="val" />
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
import RecursiveRenderer from './RecursiveRenderer.vue';

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
  showkey : Boolean
});

const isEmptyData = (data) => {
  if (Array.isArray(data)) {
    return data.length === 0;
  }
  return typeof data === 'object' && data !== null && Object.keys(data).length === 0;
};

const isSimpleVal = (val) => {
  return (typeof val != 'object');
}

const hasSimpleVals = (val) => {
  if (typeof val !== 'object' || val === null) return false;
  for (const value of Object.values(val)) {
    for (const v of Object.values(value)) {
      if (["string", "number", "boolean"].includes(typeof v)) {
        return true;
      }
    }
  }
  return false;
};

const isTableStructure = (data) => {
  if (typeof data !== 'object' || data === null) return false;
  let entries = [];
  if (Array.isArray(data)) {
    entries = data;
  } else {
    entries = Object.values(data);
  }
  if (entries.length === 0 || entries[0] === null) return false;
  if(entries.length === 1) return true;

  const keys = Object.keys(entries[0]);
  return entries.every(entry =>
    typeof entry === 'object' &&
    entry !== null &&
    JSON.stringify(Object.keys(entry).sort()) === JSON.stringify(keys.sort())
  );
};
</script>

<style scoped>
th, td {
  border: 1px solid #ccc;
  text-align: center;
}
</style>