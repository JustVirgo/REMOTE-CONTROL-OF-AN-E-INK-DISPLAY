<template>
  <div>
    <NavBar />
    <div class="pt-20 flex flex-col items-center min-h-screen">
      <div class="bg-gray-300 p-4 rounded w-95/100">
        <label class="block mb-2 font-semibold">Create new data source:</label>
        <select v-model="selectedSource" @change="onSourceSelect" class="w-full p-2 rounded">
          <option value="" disabled selected>Select source...</option>
          <option v-for="(value, key) in sets" :key="key" :value="key">{{ key }}</option>
        </select>

        <!-- Input Form -->
        <div v-if="selectedSource && showInputs" class="mt-4">
          <h3 class="font-bold mb-2">{{ selectedSource }} inputs:</h3>
          <div v-for="(inputDef, name) in sets[selectedSource].inputs" :key="name" class="mb-4">
            <div class="flex items-center w-full mb-2">
              <!-- left: field name -->
              <span class="font-semibold pr-2"><a class="text-gray-500" v-if="!inputDef[1]"> Include</a> {{ name }}:</span>

              <!-- optional toggle -->
              <label
                v-if="!inputDef[1]"
                class="flex items-center space-x-2 text-sm text-gray-500"
              >
                <input
                  type="checkbox"
                  v-model="optionalToggles[name]"
                  class="switch-toggle"
                />
              </label>
            </div>

            <div v-if="inputDef[1] || optionalToggles[name]">
              <!-- String -->
              <input
                v-if="inputDef[0] === 'string'"
                v-model="inputValues[name]"
                type="text"
                class="w-full p-2 rounded"
              />
              
              <!-- List String -->
              <div v-else-if="inputDef[0] === 'list-string'" class="space-y-2">
                <div v-for="(item, index) in inputValues[name]" :key="index" class="flex gap-2">
                  <input
                    v-model="inputValues[name][index]"
                    type="text"
                    class="w-full p-2 rounded"
                  />
                  <button @click="inputValues[name].splice(index, 1)" class="bg-red-500 text-white px-2 py-1 rounded fa fa-x"></button>
                </div>
                <Button color="blue" @click="inputValues[name].push('')">
                  <i class="fa fa-plus" ></i> Add Item
                </Button>
              </div>


              <!-- Int -->
              <input
                v-else-if="inputDef[0] === 'int'"
                v-model.number="inputValues[name]"
                type="number"
                step="1"
                class="w-full p-2 rounded"
              />

              <!-- Float -->
              <input
                v-else-if="inputDef[0] === 'float'"
                v-model.number="inputValues[name]"
                type="number"
                step="any"
                class="w-full p-2 rounded"
              />

              <!-- Switch -->
              <div v-else-if="inputDef[0] === 'switch'" class="flex items-center space-x-2 bg-white p-2 rounded">
                <label>{{ inputValues[name] ? inputDef[3]?.to : inputDef[3]?.from }}</label>
                <input
                  type="checkbox"
                  v-model="inputValues[name]"
                  class="switch-toggle"
                />
              </div>

              <!-- Picker -->
              <select
                v-else-if="inputDef[0] === 'picker'"
                v-model="inputValues[name]"
                class="w-full p-2 rounded"
              >
                <option v-for="opt in inputDef[3]?.options || []" :key="opt" :value="opt">
                  {{ opt }}
                </option>
              </select>

              <!-- Whisper -->
              <template v-else-if="inputDef[0] === 'whisper'">
              <div
                @focusin="focusedWhisper = name"
                @focusout="focusedWhisper = ''; whisperSuggestions[name] = [];"
                class="relative"
              >
                <input
                  v-model="inputValues[name]"
                  @input="onWhisperInput(name, inputDef[3])"
                  type="text"
                  class="w-full p-2 rounded"
                  placeholder="Start typing..."
                  @focus="focusedWhisper = name, onWhisperInput(name, inputDef[3])"
                />
                <ul
                  v-if="focusedWhisper === name && whisperSuggestions[name]?.length && inputValues[name]"
                  class="absolute bg-white mt-1 rounded shadow w-full z-10"
                >
                  <li
                    v-for="suggestion in whisperSuggestions[name]"
                    :key="suggestion"
                    @mousedown.prevent="selectWhisperSuggestion(name, suggestion)"
                    class="px-2 py-1 hover:bg-gray-200 cursor-pointer"
                  >
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </template>

              <!-- Fallback -->
              <input
                v-else
                v-model="inputValues[name]"
                class="w-full p-2 rounded"
                placeholder="Unknown input type"
              />
            </div>
          </div>


          <div class="flex space-x-2 mt-2">
            <Button color="green" tooltip="Save datasource" @click="saveSource" :disabled="loadingNew">
              <span v-if="!loadingNew" class="fa fa-check"></span>
              <div v-else class="loader border-4 border-white border-t-transparent rounded-full w-5 h-5 animate-spin"></div>
            </Button>
            <Button color="red" tooltip="Cancel inputs" @click="cancelInputs">
              <i  class="fa fa-x"></i>
            </Button>
          </div>
        </div>

        <!-- Loaded Data Source Tables -->
        <div v-if="savedSources.length === 0" class="mt-8 text-center text-gray-500">No saved data sources.</div>
        <div v-else class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6 w-full ">
          <div v-for="source in savedSources" :key="source.uid" class="bg-white p-4 rounded shadow overflow-x-auto">
            <!-- Local Loading Spinner -->
            
          <div class="flex space-x-2">
            <Button color="red" tooltip="Delete" @click="deleteDatasource(source.uid)">
              <i  class="fa fa-trash"></i>
            </Button>

            <Button tooltip="Refresh" @click="updateSource(source.uid)">
              <i  class="fa fa-refresh"></i>
            </Button>
            

            <Button color="yellow" tooltip="Edit" @click="editDatasource(source)">
              <i  class="fa fa-pencil"></i>
            </Button>
          </div>
            
            <div v-if="loadingByUid[source.uid]" class="flex justify-center items-center mb-2">
              <div class="loader border-4 border-blue-500 border-t-transparent rounded-full w-6 h-6 animate-spin"></div>
            </div>

            <h3 class="text-lg font-semibold mb-2">{{ source.source }} (ID: {{ source.uid }})</h3>

            <p class="font-semibold">Inputs:</p>
            <ul class="mb-2 pl-4 list-disc">
              <li v-for="(val, key) in source.inputs" :key="key">
                <strong>{{ key }}:</strong> {{ val }}
              </li>
            </ul>
            
            <p class="font-semibold">Data:</p>
              <RecursiveRenderer :data="source.data" :showkey="true" />

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted} from 'vue';
import NavBar from '@/components/NavBar.vue';
import RecursiveRenderer from '../components/RecursiveRenderer.vue';
import Button from '@/components/Button.vue';
import axios from 'axios';

const sets = ref({});
const selectedSource = ref('');
const inputValues = reactive({});
const showInputs = ref(false);
const savedSources = ref([]);
const optionalToggles = reactive({});
const editMode = ref(false);
const editingUid = ref(null);
const whisperSuggestions = reactive({});
const focusedWhisper = ref('');
const loadingByUid = reactive({});
const loadingNew = ref(false);



const onWhisperInput = async (key, filePath) => {
  const query = inputValues[key];

  if (!query || query.trim().length < 2) {
    whisperSuggestions[key] = [];
    return;
  }

  try {
    const response = await axios.get('/api/whisper', {
      params: { query, path: filePath }
    });
    whisperSuggestions[key] = response.data.options;
  } catch (err) {
    console.error('Whisper fetch failed', err);
  }
};

const selectWhisperSuggestion = (key, suggestion) => {
  inputValues[key] = suggestion;
  whisperSuggestions[key] = [];
  focusedWhisper.value = '';
};


const loadSavedSources = async () => {
  try {
    const response = await axios.get('/api/get-saved-datasources');
    savedSources.value = response.data;
    console.log(response.data)
  } catch (error) {
    console.error('Failed to load saved data sources:', error);
  } finally {
  }
};


//DATASET STRUCTURE 
// "input name": ["<type>", <required:boolean>, <defaultValue:optional>, <metaData:optional>]
  
onMounted(async () => {
  try {
    const response = await axios.get('/api/get-datasets');
    sets.value = response.data;

    await loadSavedSources(); // Load existing sources after datasets
  } catch (error) {
    console.error('Failed to fetch data sources:', error);
  }
});

const editDatasource = (source) => {
  selectedSource.value = source.source;
  showInputs.value = true;
  editMode.value = true;
  editingUid.value = source.uid;

  const inputs = sets.value[selectedSource.value]?.inputs || {};

  for (const key in inputs) {
    const def = inputs[key];
    const type = def[0];
    const required = def[1];
    const defaultVal = def.length >= 3 ? def[2] : (type === 'switch' ? false : '');

    const existingValue = source.inputs[key];

    if (type === 'list-string') {
      inputValues[key] = Array.isArray(existingValue)
        ? existingValue
        : Array.isArray(defaultVal)
          ? defaultVal
          : [];
    } else {
      inputValues[key] = existingValue !== undefined ? existingValue : defaultVal;
    }

    // Optional toggle (show non-required fields only if explicitly set)
    optionalToggles[key] = required || existingValue !== undefined;
  }

  // Scroll to top for better UX
  window.scrollTo({ top: 0, behavior: 'smooth' });
};


const onSourceSelect = () => {
  showInputs.value = true;

  const inputs = sets.value[selectedSource.value]?.inputs || {};

  for (const key in inputs) {
    const def = inputs[key];

    // 0 = type, 1 = required, 2 = default, 3 = extras
    const defaultVal = def.length >= 3 ? def[2] : (def[0] === 'switch' ? false : '');
    if (def[0] === 'list-string') {
      inputValues[key] = Array.isArray(defaultVal) ? defaultVal : [];
    } else {
      inputValues[key] = defaultVal;
    }

    inputValues[key] = defaultVal;
    optionalToggles[key] = !!def[1]; // If required, always show; else use switch
  }
};


const saveSource = async () => {
  const validKeys = Object.keys(sets.value[selectedSource.value]?.inputs || {});
  const filteredInputs = validKeys.reduce((acc, key) => {
    const def = sets.value[selectedSource.value].inputs[key];
    const required = def[1];
    if (required || optionalToggles[key]) {
      acc[key] = inputValues[key];
    }
    return acc;
  }, {});

  const missing = Object.entries(filteredInputs).some(([key, val]) =>
    val === undefined || val === null || val === ""
  );
  if (missing) {
    alert("Please fill in all required fields.");
    return;
  }


  loadingNew.value = true;
  try {
    if (editMode.value && editingUid.value !== null) {
      // EDIT MODE
      loadingByUid[editingUid.value] = true;
      await axios.post('/api/edit-datasource', {
        uid: editingUid.value,
        source: selectedSource.value,
        inputs: filteredInputs
      });
    } else {
      // CREATE NEW
      await axios.post('/api/save-datasource', {
        source: selectedSource.value,
        inputs: filteredInputs
      });
    }

    editMode.value = false;
    loadingByUid[editingUid.value] = false;
    editingUid.value = null;
  } catch (error) {
    console.error('Failed to save data source:', error);
  }

  selectedSource.value = "";
  loadSavedSources();
  loadingNew.value = false;
  showInputs.value = false;
};


const updateSource = async (uid) => {
  loadingByUid[uid] = true;
  try {
    await axios.get(`/api/refresh-datasource/${uid}`);
    await loadSavedSources();
  } catch (error) {
    console.error('Failed to reload data:', error);
  } finally {
    loadingByUid[uid] = false;
  }
};

const deleteDatasource = async (uid) => {
  loadingByUid[uid] = true;
  try {
    await axios.delete(`/api/delete-datasource/${uid}`);
    savedSources.value = savedSources.value.filter((item) => item.uid !== uid);
  } catch (error) {
    console.error("Failed to delete data source:", error);
  } finally {
    loadingByUid[uid] = false;
  }
};



const cancelInputs = () => {
  showInputs.value = false;
  selectedSource.value = '';
  editMode.value = false;
  editingUid.value = null;
};

</script>

<style scoped>
select, input {
  background-color: white;
}
table {
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ccc;
  text-align: center;
}

.switch-toggle {
  width: 40px;
  height: 20px;
  background-color: #ccc;
  appearance: none;
  border-radius: 9999px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.switch-toggle:checked {
  background-color: #22c55e;
}

.switch-toggle::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  height: 16px;
  width: 16px;
  border-radius: 9999px;
  background: white;
  transition: transform 0.2s ease-in-out;
}

.switch-toggle:checked::before {
  transform: translateX(20px);
}

.loader {
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

</style>
