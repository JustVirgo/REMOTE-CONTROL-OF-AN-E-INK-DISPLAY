<template>
    <div>
      <NavBar />
        <div class="pt-20 flex flex-col items-center min-h-screen">
          <div class="bg-gray-300 p-4 rounded w-95/100">
            <!-- Add New Screen Section -->
            <div class="bg-gray-100 p-4 rounded">
              <div class="flex justify-between items-center">
                <h2 class="text-xl font-semibold">
                  {{ editingId ? "Edit screen" : "Create new screen" }}
                </h2>
                
                <Button tooltip="Add screen" @click="addingScreen = !addingScreen">
                  <i :class="addingScreen ? 'fa fa-minus' : 'fa fa-plus'"></i>
                </Button>
              </div>

              <!-- Hidden form shown only when addingScreen is true -->
              <div v-if="addingScreen" class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="md:col-span-2">
                  <label class="block font-medium">For Display:</label>
                  <select
                    v-model="newScreen.displayId"
                    class="w-full p-2 rounded bg-white border"
                    @change="onDisplaySelected"
                  >
                    <option disabled value="">-- Select a display --</option>
                    <option
                      v-for="disp in displayOptions"
                      :key="disp.id"
                      :value="disp.id"
                    >
                      {{ disp.name }} ({{ disp.resolutionX }}×{{ disp.resolutionY }})
                    </option>
                  </select>
                </div>
                <div class="md:col-span-2 block text-xl font-semibold">
                  Customize:
                </div>
                <div>
                  <label class="block font-medium">Name:</label>
                  <input v-model="newScreen.name" class="w-full p-2 rounded bg-white" />
                </div>

                <div>
                  <label class="block font-medium">Resolution (px):</label>
                  <div class="flex space-x-2">
                    <input v-model="newScreen.resolutionX" type="text" @input="sanitizePositive($event, 'resolutionX')" class="w-1/2 p-2 rounded bg-white" placeholder="Width (px)" />
                    <input v-model="newScreen.resolutionY" type="text" @input="sanitizePositive($event, 'resolutionY')" class="w-1/2 p-2 rounded bg-white" placeholder="Height (px)" />
                  </div>
                </div>

                <div>
                  <label class="block font-medium">Refresh time (s)</label>
                  <input type="text" @input="sanitizePositive($event, 'refresh')" v-model="newScreen.refresh" class="w-full p-2 rounded bg-white" />
                </div>

                <!-- ID Field: only when editing an existing screen -->
                <div>
                  <label class="block">ID:</label>
                  <input
                    v-model.number="newScreen.id"
                    type="text" @input="sanitizePositive($event, 'id')"
                    class="w-full p-2 rounded bg-white"
                  />
                </div>

                <div class="flex space-x-4">
                  <Button color="green" tooltip="Add screen" @click="saveScreen">
                    <i  class="fa fa-check"></i>
                  </Button>
                  <Button color="red" tooltip="Cancel inputs" @click="cancelInputs">
                    <i  class="fa fa-x"></i>
                  </Button>
                </div>
              </div>
            </div>
            <!-- List of Existing Screens -->
          <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6" v-if="screens.length > 0">
            <div v-for="screen in screens" :key="screen.id" class="bg-white p-4 rounded shadow">
              <h3 class="text-lg font-semibold mb-2">{{ screen.name }} (ID:{{ screen.id }})</h3>

              <p><strong>Resolution:</strong> {{ screen.resolutionX }} x {{ screen.resolutionY }}</p>
              <p><strong>Refresh time (s):</strong> {{ screen.refresh }}</p>

              <div class="flex justify-end space-x-2 mt-4">
                <Button tooltip="Edit screen info" @click="editScreen(screen.id)">
                  <i  class="fa fa-pencil"></i>
                </Button>

                <Button color="yellow" tooltip="Edit contents" @click="router.push(`/editcontents/${screen.id}`)">
                  <i  class="fa fa-edit"></i>
                </Button>

                <Button color="red" tooltip="Delete" @click="deleteScreen(screen.id)">
                  <i  class="fa fa-trash"></i>
                </Button>
              </div>
            </div>
          </div>

            <!-- No Screens -->
          <div class="mt-8 text-center text-gray-500" v-else>
            No screens found. {{err}}
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { useRouter } from "vue-router";
import NavBar from "@/components/NavBar.vue";
import Button from "@/components/Button.vue";
import axios from "axios";

// Screens state
const screens = ref([]);
const addingScreen = ref(false);
const newScreen = ref({
  name: "",
  resolutionX: "",
  resolutionY: "",
  refresh: 300,
  id: null,
});
const editingId = ref(null); // If not null, we're editing this ID

const displayOptions  = ref([])

const router = useRouter();
const err = ref(null)

function sanitizePositive(event, field) {
  const cleaned = event.target.value.replace(/[^0-9]/g, '');
  newScreen.value[field] = cleaned;
}

// compute next free ID
const nextId = computed(() => {
  if (!screens.value.length) return 1;
  return Math.max(...screens.value.map(s => s.id)) + 1;
});

// Watch for changes in addingScreen to set the ID for new screens
watch(addingScreen, open => {
  if (open && editingId.value === null) {
    newScreen.value.id = nextId.value;
  }
});;

// When the user picks a display, fill name & resolution fields:
function onDisplaySelected(e) {
  const id = parseInt(e.target.value, 10)
  const disp = displayOptions.value.find(d => d.id === id)
  if (disp) {
    newScreen.value.name        = disp.name
    newScreen.value.resolutionX = disp.resolutionX
    newScreen.value.resolutionY = disp.resolutionY
  }
}

// Fetch screens from backend on load
const fetchScreens = async () => {
  try {
    const response = await axios.get("/api/get-screens"); 
    screens.value = Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error("Error loading screens:", error);
  }
};

async function fetchDisplays() {
  try {
    const { data } = await axios.get("/api/get-displays")
    displayOptions.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error("Error loading displays:", e)
  }
}

const saveScreen = async () => {
  if (
    !newScreen.value.name ||
    !newScreen.value.resolutionX ||
    !newScreen.value.resolutionY 
  ) {
    alert("Please fill in all required fields.");
    return;
  }


  // Prevent duplicate IDs
  if (screens.value.some(s => s.id === newScreen.value.id) && editingId.value !== newScreen.value.id) {
    alert(`ID ${newScreen.value.id} is already taken. Please pick a different one.`);
    return;
  }

  const payload = {
    id:   Number(newScreen.value.id),
    name: newScreen.value.name,
    resolutionX: newScreen.value.resolutionX,
    resolutionY: newScreen.value.resolutionY,
    refresh: newScreen.value.refresh
  };

  try {
    if (editingId.value) {
      // Request to update
      await axios.put(`/api/update-screen/${editingId.value}`, payload);

      // Replace item in local list
      const idx = screens.value.findIndex(d => d.id === editingId.value);
      if (idx !== -1) screens.value[idx] = { ...payload, id: editingId.value };

      screens.value[idx].id = Number(newScreen.value.id); // Ensure the ID is set correctly  

      editingId.value = null;
    } else {
      const response = await axios.post("/api/save-screen", payload);
      screens.value.push(response.data);
    }

    // Reset form
    newScreen.value = {
      name: "",
      resolutionX: "",
      resolutionY: "",
      refresh: 300,
      id: null,
    };
    addingScreen.value = false;

  } catch (error) {
    console.error("Error saving screen:", error);
  }
};


const cancelInputs = () => {
  addingScreen.value = false;
  newScreen.value = {
    name: "",
    resolutionX: "",
    resolutionY: "",
    refresh: 300
  };
};


// Delete a screen
const deleteScreen = async (screenId) => {
  try {
    await axios.delete(`/api/delete-screen/${screenId}`);
    
    // Remove the screen from the local state after successful deletion
    screens.value = screens.value.filter(screen => screen.id !== screenId);

    console.log(`Screen with ID ${screenId} deleted successfully.`);
  } catch (error) {
    console.error("Error deleting screen:", error);
  }
};

const editScreen = (screenId) => {
  const toEdit = screens.value.find(d => d.id === screenId);
  if (!toEdit) return;

  editingId.value = screenId;
  addingScreen.value = true;

  newScreen.value = {
    name: toEdit.name,
    resolutionX: toEdit.resolutionX,
    resolutionY: toEdit.resolutionY,
    refresh: toEdit.refresh,
    id: toEdit.id
  };

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
};


// Fetch screens when the component mounts
onMounted(async () => {

  try {
    await fetchScreens()
  } catch (e) {
    console.error("Error loading screens:", e)
  }
  try {
    await fetchDisplays()
  } catch (e) {
    console.error("Error loading displays:", e)
  }
})
</script>
