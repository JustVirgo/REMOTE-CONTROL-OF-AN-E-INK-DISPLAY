<template>
  <div>
    <NavBar />
    <div v-if="!initialized" class="flex items-center justify-center min-h-screen">
      <!-- Show a loading spinner or message while we fetch/resize -->
      <span>Loading…</span>
    </div>
    <div  v-else class="pt-20 flex px-8 gap-4 w-full min-h-screen bg-gray-100">
      <!-- Sidebar: Add Widget Buttons -->
      <div class="w-1/4 bg-gray-300 p-4 rounded shadow">
        <h2 class="text-lg font-bold mb-2">Add Widget</h2>
        <button class="w-full bg-white py-2 my-2 rounded shadow" @click="setWidgetType('StaticText')">Static text</button>
        <button class="w-full bg-white py-2 my-2 rounded shadow" @click="setWidgetType('ValueText')">Value from source</button>
        <button class="w-full bg-white py-2 my-2 rounded shadow" @click="setWidgetType('Image')">Image</button>
        <button class="w-full bg-white py-2 my-2 rounded shadow" @click="setWidgetType('ProgressBar')">Progress bar</button>

        <h2 class="text-lg font-bold mt-6 mb-2">Widgets in Display</h2>
        <div class="overflow-y-auto max-h-128 border border-gray-400 rounded bg-white px-2 py-1">
          <ul class="space-y-1">
            <template v-for="(widget, index) in widgets" :key="'list-' + index">
              <li
                v-if="!widget.deleted"
                @click="selectedWidgetIndex = index"
                :class="[
                  'flex justify-between items-center p-2 rounded',
                  selectedWidgetIndex === index ? 'bg-yellow-200' : 'hover:bg-gray-100'
                ]"
              >
                <span>{{ widget.type }}</span>
                <div class="space-x-2">
                  <i class="fas fa-pencil text-yellow-600 cursor-pointer p-2" @click.stop="editWidget(index), selectedWidgetIndex = index" />
                  <i class="fas fa-trash text-red-600 p-2 cursor-pointer" @click.stop="deleteWidget(index)" />
                </div>
              </li>
            </template>
          </ul>
        </div>
      </div>

      
      <!-- Widget Inputs Panel -->
      <div v-if="newWidget" class="w-1/4 bg-gray-200 p-4 shadow rounded">
        <h2 class="text-lg font-semibold mb-2">Configure {{ newWidget.type }}</h2>

        <WidgetInput :widget="newWidget" @image-change="onImageChange" />


        <div class="mt-4 flex">
          <Button class="w-full px-3 py-1" :color='editingIndex || editingIndex == 0 ? "yellow" : "green"' @click="confirmAddWidget">
            {{ editingIndex || editingIndex == 0 ? "Edit Widget" :"Add Widget"}}
          </Button>
        </div>

        <div class="mt-2 flex">
          <Button class="w-full" color="red" @click="cancelAddWidget">
            Cancel
          </Button>
        </div>
      </div>
      


      <!-- Display Editor -->
      <div class="flex-1 flex flex-col items-center" >
        <h2 class="text-xl font-bold mb-4">{{ screen.name }} ({{ screen.resolutionX }} × {{ screen.resolutionY }})</h2>
         <!-- Icons -->
      <div class="flex space-x-2">
        <!-- Rotate -->
        <span class="icon-wrapper" @click="toggleOrientation">
          <i class="fas fa-sync-alt"></i>
          <span class="tooltip">Rotate 90°</span>
        </span>

        <!-- Flip X -->
        <span
          class="icon-wrapper"
          :class="{ 'active': screen.flipX }"
          @click="toggleFlipX"
        >
          <i class="fas fa-arrows-alt-h"></i>
          <span class="tooltip">Flip horizontally</span>
        </span>

        <!-- Flip Y -->
        <span
          class="icon-wrapper"
          :class="{ 'active': screen.flipY }"
          @click="toggleFlipY"
        >
          <i class="fas fa-arrows-alt-v"></i>
          <span class="tooltip">Flip vertically</span>
        </span>

         <!-- Blocking Mode Toggle -->
        <span
          class="icon-wrapper"
          :class="{ 'active': blockingMode }"
          @click="toggleBlocking"
        >
          <i class="fas" :class="blockingMode ? 'fa-lock' : 'fa-unlock'"></i>
          <span class="tooltip">
            {{ blockingMode ? 'Blocking ON' : 'Blocking OFF' }}
          </span>
        </span>
      </div>

      <div
        ref="displayArea"
        class="relative"
        :style="{
          width:  (screen.isRotated ? gridHeight : gridWidth) * gridSize + 'px',
          height: (screen.isRotated ? gridWidth  : gridHeight) * gridSize + 'px'
        }"
        @dragover.prevent="dragOver"
        @drop.prevent="endDrag"
        
      >
        <!-- Rotated grid background: no pointer events, z-index 0 -->
      <div
        class="absolute top-0 left-0 pointer-events-none"
        :style="{
        width:  (screen.isRotated ? gridHeight : gridWidth) * gridSize + 'px',
        height: (screen.isRotated ? gridWidth  : gridHeight) * gridSize + 'px',
          backgroundColor:  '#fff',
          transformOrigin:  'center center',
          zIndex:           0
        }"
      >
        <div class="grid-container" style="width:100%; height:100%" ></div>
      </div>


        <!-- Widgets layer (always pointer-enabled), z-index 10 -->
        <div  class="absolute top-0 left-0 w-full h-full" style="z-index:10;">
          <div v-for="(widget, index) in widgets" :key="index">
            <div
              v-if="!widget.deleted"
              class="cursor-grab border flex items-center box-border"
              :style="widgetRenderStyle(widget, index)"
              draggable="true"
              @dragstart="startDrag($event, index)"
              @dragend="endDrag"
              @click="selectedWidgetIndex = index"
            >
          <!-- make this flex full-height so children can stretch -->
          <div class="flex w-full h-full">
            
            <!-- StaticText -->
            <template v-if="widget.type === 'StaticText'">
              <div class="whitespace-nowrap overflow-hidden w-full flex items-center">
                {{ widget.text }}
              </div>
            </template>
            
            <!-- ValueText: single-line, ellipsis for objects -->
            <template v-else-if="widget.type === 'ValueText'">
              <div class="whitespace-nowrap overflow-hidden w-full flex items-center">
                <template v-if="typeof widget.value === 'object' && widget.value !== null">
                  <WidgetDataRenderer
                    :data="{ val: widget.value }"
                    :fontSize="widget.fontSize"
                    :fontFamily="widget.fontFamily" 
                    :showKeys="false"
                    class="inline-block text-ellipsis"
                    style="width: 100%;"
                  />
                </template>
                <template v-else>
                  <div v-if="widget.value !== null">
                    {{ widget.value + (widget.unit ?? '') }}
                  </div>
                  <div v-else class="text-gray-500">No data</div>
                </template>
              </div>
            </template>
            
            <!-- ProgressBar -->
            <template v-else-if="widget.type === 'ProgressBar'">
              <div class="w-full h-full overflow-hidden">
                <div
                  class="h-full items-center"
                  :style="{
                    width: getProgressBarFill(widget) + '%',
                    backgroundColor: widget.color || '#00AAFF'
                  }"
                ></div>
              </div>
            </template>
            
            <!-- Image -->
            <template v-else-if="widget.type === 'Image' && widget.preview">
              <img
                :src="widget.preview"
                :style="{ width: widget.width + 'px', height: widget.height + 'px' }"
                class="rounded"
              />
            </template>
          </div>
          </div>
        </div>
      </div>
        </div>
        <div class="flex space-x-6 pb-10 pt-5">

          <Button @click="getScreenImage" :disabled="loadingImage">
            <div v-if="loadingImage" class="loader border-4 border-white border-t-transparent rounded-full w-5 h-5 mr-2 animate-spin"></div>
            <span>{{ loadingImage ? 'Rendering…' : 'Render Preview' }}</span>
          </Button>

          <Button color="green" @click="saveWidgets(false, true)">
            Save
          </Button>


          <Button color="green" @click="saveWidgets(true, true)">
            Save & Exit
          </Button>

          <Button color="red" @click='router.push("/managescreens")'>
            Exit without saving
          </Button>
        </div>
        <div v-if="imageUrl" class="mb-6">
            <h3 class="font-semibold mb-2">Rendered Preview:</h3>
            <img ref="renderedArea" :src="imageUrl" :alt="`Screen ${screen.name}`" class="border" />
        </div>
      </div>
    </div>
  </div>
  <!-- Hidden preview element to measure widget content size -->
  <div
  ref="previewBox"
  class="invisible"
  style="position: absolute; left: -9999px; top: -9999px; white-space: normal; display: inline-block;"
></div>

</template>

<script setup>
import { ref, nextTick, createApp, onBeforeMount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import NavBar from '@/components/NavBar.vue';
import WidgetInput from '@/components/WidgetInput.vue';
import WidgetDataRenderer from '../components/WidgetDataRenderer.vue';
import Button from '../components/Button.vue';
import axios from 'axios';


const route = useRoute();
const router = useRouter();
const screenId = route.params.id;

const gridSize = 10;
const gridWidth = ref(0);
const gridHeight = ref(0);
const screen = ref({});
const widgets = ref([]);
const newWidget = ref(null);
const draggedWidgetIndex = ref(null);
const displayArea = ref(null)
const dragOffset = ref({ x: 0, y: 0 });
const previewBox = ref(null);
const initialized = ref(false); 
const editingIndex = ref(null)
const selectedWidgetIndex = ref(null);
const imageUrl = ref(null)
const blockingMode = ref(true)
const loadingImage = ref(false)
const renderedArea = ref(null);

const toggleBlocking = () => {
  blockingMode.value = !blockingMode.value
}


const getScreenImage = async () => {
  loadingImage.value = true
  imageUrl.value     = null
  try {
    await saveWidgets(false, false)
    // ask the backend to render & return the PNG
    const resp = await axios.get(
      `/api/render-screen-image/${screenId}`,
      { responseType: 'blob' }
    )
    // blob -> objectURL
    imageUrl.value = URL.createObjectURL(resp.data)

    // scroll into view
    await nextTick()
    const offset = renderedArea.value.offsetTop
    window.scrollTo({ top: offset, behavior: 'smooth' });
  } catch (err) {
    console.error('Failed to fetch rendered image', err)
  } finally {
    loadingImage.value = false
  }
}



function toggleOrientation() {
  const wScreen = screen.value.resolutionX;
  const hScreen = screen.value.resolutionY;

  widgets.value.forEach(widget => {
    const w = getWidgetWidth(widget);
    const h = getWidgetHeight(widget);
    const x0 = widget.x;
    const y0 = widget.y;
    let newX, newY;

    if (!screen.value.isRotated) {
      // portrait -> landscape (rotate +90deg)
      newX = y0;
      newY = wScreen - x0 - w;
      // clamp within new bounds
      newX = Math.min(Math.max(newX, 0), hScreen - w);
      newY = Math.min(Math.max(newY, 0), wScreen - h);
    } else {
      // landscape -> portrait (rotate -90deg)
      newX = hScreen - y0 - h;
      newY = x0;
      newX = Math.min(Math.max(newX, 0), wScreen - w);
      newY = Math.min(Math.max(newY, 0), hScreen - h);
    }

    widget.x = newX;
    widget.y = newY;
  });

  screen.value.isRotated = !screen.value.isRotated;
}

function toggleFlipX() {
  screen.value.flipX = !screen.value.flipX
}

function toggleFlipY() {
  screen.value.flipY = !screen.value.flipY
}



onBeforeMount(async () => {
  const res = await axios.get(`/api/get-screen/${screenId}`);
  screen.value = res.data;
  screen.value.isRotated = res.data.isRotated || false;
  screen.value.flipX = res.data.flipX || false;
  screen.value.flipY = res.data.flipY || false;

  gridWidth.value = screen.value.resolutionX / gridSize;
  gridHeight.value = screen.value.resolutionY / gridSize;
  widgets.value = res.data.widgets || [];

  await loadAllWidgetValues();
  initialized.value = true;
});

const setWidgetType = (type) => {
  editingIndex.value = null;
  newWidget.value = { type, x: 0, y: 0, fontSize: 16};

  if (type === 'ProgressBar') {
    newWidget.value.min = 0;
    newWidget.value.scale = 100;
    newWidget.value.color = '#000000';
    newWidget.value.width = screen.value.resolutionX;
    newWidget.value.height = 20;

    // make sure we have something to render immediately
    newWidget.value.value = newWidget.value.min;
  } else if (type === 'ValueText') {
    newWidget.value.decimals = 0;
    newWidget.value.unit = '';
  }
};

const confirmAddWidget = async () => {
  if (!(newWidget.value.text || newWidget.value.fieldName || newWidget.value.width || newWidget.value.height)) {
    alert("Fill out the fields")
    return;
  }
  const widget = { ...newWidget.value };

  
  if (widget.type === 'ValueText' || widget.type === 'ProgressBar') {
    await fetchWidgetValue(widget);
  }
  console.log(widget);

  await resizeWidgetToContent(widget);

  if (editingIndex.value !== null) {
    widgets.value[editingIndex.value] = widget;
  } else {
    widget.deleted = false;
    widgets.value.push(widget);
  }

  newWidget.value = null;
  editingIndex.value = null;
};


const cancelAddWidget = () => {
  newWidget.value = null;
  editingIndex.value = null;
};

const deleteWidget = (index) => {
  const widget = widgets.value[index];

  if (widget.type === "Image") {
    widget.deleted = true;
  } else {
    widgets.value.splice(index, 1);
  }

  newWidget.value = null;
};


const editWidget = (index) => {
  newWidget.value = { ...widgets.value[index] };
  newWidget.value._originalFilename = widgets.value[index].filename; // track old file
  editingIndex.value = index;
};


const startDrag = (event, index) => {
  draggedWidgetIndex.value = index;
  selectedWidgetIndex.value = index;

  const rect = event.target.getBoundingClientRect();

  dragOffset.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  };

  event.dataTransfer.effectAllowed = 'move';
  const transparentImg = new Image();
  transparentImg.src = 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=';
  event.dataTransfer.setDragImage(transparentImg, 0, 0);
  document.body.style.cursor = 'grabbing';
};

const isOverlapping = (x, y, width, height, excludeIndex = -1) => {
  return widgets.value.some((w, i) => {
    if(w.deleted) return false;
    if (i === excludeIndex) return false;

    const wX = w.x;
    const wY = w.y;
    const wW = getWidgetWidth(w);
    const wH = getWidgetHeight(w);

    return (
      x < wX + wW &&
      x + width > wX &&
      y < wY + wH &&
      y + height > wY
    );
  });
};

const getProgressBarFill = (widget) => {
  if (typeof widget.value !== 'number') return 0;
  const min = typeof widget.min === 'number' ? widget.min : 0;
  const max = typeof widget.scale === 'number' ? widget.scale : 100;

  if (max <= min) return 0;
  const clamped = Math.max(min, Math.min(widget.value, max));
  const test = ((clamped - min) / (max - min)) * 100; 
  return test;
};


const onImageChange = (event, widget) => {
  const file = event.target.files[0];
  if (!file) return;
  
  widget.file = file;
  widget.preview = URL.createObjectURL(file);
  widget._imageChanged = true; // mark for cleanup

  const img = new Image();
  img.onload = () => {
    widget.width = img.width;
    widget.height = img.height;
  };
  img.src = widget.preview;
};


function dragOver(event) {
  event.preventDefault();
  if (draggedWidgetIndex.value === null) return;

  // Find pointer delta from the *center* of the rotated display
  const rect = displayArea.value.getBoundingClientRect();
  const cx   = rect.left + rect.width  / 2;
  const cy   = rect.top  + rect.height / 2;
  const dx   = event.clientX - cx;
  const dy   = event.clientY - cy;

  // Figure out our *real* display size (swapped in landscape)
  const realW = screen.value.isRotated
    ? screen.value.resolutionY
    : screen.value.resolutionX;
  const realH = screen.value.isRotated
    ? screen.value.resolutionX
    : screen.value.resolutionY;

  //  Translate back into un-rotated, top-left-origin coords
  //    (and subtract the dragOffset so the widget “sticks” to your cursor)
  const localX = dx + realW / 2 - dragOffset.value.x;
  const localY = dy + realH / 2 - dragOffset.value.y;

  // Snap to grid
  const gridX = Math.round(localX / gridSize);
  const gridY = Math.round(localY / gridSize);
  const px    = gridX * gridSize;
  const py    = gridY * gridSize;

  // Clamp so you can’t drag out of bounds
  const w    = getWidgetWidth(widgets.value[draggedWidgetIndex.value]);
  const h    = getWidgetHeight(widgets.value[draggedWidgetIndex.value]);
  const clampedX = Math.min(Math.max(px, 0), realW - w);
  const clampedY = Math.min(Math.max(py, 0), realH - h);


  if(blockingMode.value){
    if (!isOverlapping(clampedX, clampedY, w, h, draggedWidgetIndex.value)) {
      widgets.value[draggedWidgetIndex.value].x = clampedX;
      widgets.value[draggedWidgetIndex.value].y = clampedY;
    }
  } else {
    widgets.value[draggedWidgetIndex.value].x = clampedX;
    widgets.value[draggedWidgetIndex.value].y = clampedY;
  }
}


const endDrag = () => {
  draggedWidgetIndex.value = null;
  document.body.style.cursor = 'default';
};

const getWidgetWidth = (widget) => {
  if (widget.width) return widget.width;
  console.error("Widget doesn't have Width")
  return 0; // fallback default
};

const getWidgetHeight = (widget) => {
  if (widget.height) return widget.height;
  console.error("Widget doesn't have Height")
  return 0; // fallback default
};

const widgetStyle = (widget) => {
  return {
    top: widget.y + 'px',
    left: widget.x + 'px',
    width: getWidgetWidth(widget) + 'px',
    height: getWidgetHeight(widget) + 'px',
    position: 'absolute'
  };
};

function widgetRenderStyle(widget, index) {
  return {
    ...widgetStyle(widget),
    backgroundColor: widget.background || 'transparent',
    fontSize:        (widget.fontSize || 14) + 'px',
    fontFamily:      widget.fontFamily,
    fontStyle:       widget.isItalic ? 'italic' : 'normal',
    fontVariationSettings: widget.isBold
      ? "'wght' 700"
      : "'wght' 400",
    borderWidth:     '2px',
    borderColor:     selectedWidgetIndex.value === index ? '#facc15' : '#ccc',
    borderStyle:     'solid',
    boxSizing:       'border-box',
    zIndex:          selectedWidgetIndex.value === index ? 20 : 10
  }
}

const saveWidgets = async (exit, show_mess) => {
  const updatedWidgets = [];

  for (const widget of widgets.value) {
    // Handle deleted image widgets
    if (widget.deleted && widget.type === 'Image') {
      try {
        await axios.delete(`/api/delete-uploaded-image/${widget.filename}`);
        continue; // Skip adding it to updatedWidgets
      } catch (err) {
        console.warn(`Failed to delete image: ${widget.filename}`, err);
      }
    }

    // Upload newly added/replaced images
    if (widget.type === 'Image' && widget.file) {
      await uploadImage(widget.file);
      widget.filename = widget.file.name;

      const res = await axios.post(`/api/get-uploaded-image/${widget.filename}`, {}, {
        responseType: 'blob'
      });
      const blobUrl = URL.createObjectURL(res.data);
      widget.preview = blobUrl;

      delete widget.file;
      delete widget._imageChanged;
      delete widget._originalFilename;
    }

    // Handle deletions—but only for images *without* a pending file
    if (widget.deleted && widget.type === 'Image' && !widget.file) {
      await axios.delete(`/api/delete-uploaded-image/${widget.filename}`);
      continue;
    }

    // Add widget to the final list
    updatedWidgets.push(widget);
  }

  // Update widgets with cleaned list
  widgets.value = updatedWidgets;

  for (const widget of widgets.value) {
    widget.height = Number(widget.height);
    widget.width  = Number(widget.width);
  }

  console.log(screen.value);
  
  await axios.put(`/api/update-screen/${screenId}`, screen.value);

  // Save to backend
  await axios.post(`/api/update-screen-widgets/${screenId}`, {
    widgets: widgets.value
  });

  if(show_mess){
    alert("Widgets saved!");
  }

  if(exit){
    router.push("/managescreens");
  }
};

function getNestedValue(obj, path) {
  return path.split('%').reduce((acc, key) => acc?.[key], obj);
}

const fetchWidgetValue = async (widget) => {
  if (!['ValueText', 'ProgressBar'].includes(widget.type) || !widget.sourceUid || !widget.fieldName) return;

  try {
    const res = await axios.get(`/api/get-saved-datasource/${widget.sourceUid}`);
    const raw = res.data[0]?.data;
    const value = getNestedValue(raw, widget.fieldName);
    if(value === null) {
      console.warn(`Widget ${widget.type} (${widget.fieldName}) has no value`);
      widget.value = '---';
      return
    }
    widget.value = value;
  } catch (err) {
    console.error('Failed to fetch value for widget:', widget, err);
    widget.value = widget.type === 'ValueText' ? '—' : 0;
  }
};


const loadAllWidgetValues = async () => {
  for (const widget of widgets.value) {
    if (widget.type === 'ValueText') {
      await fetchWidgetValue(widget);
    } else if (widget.type === 'Image' && widget.filename) {
      const res = await axios.post(`/api/get-uploaded-image/${widget.filename}`, {}, {
        responseType: 'blob'
      });
      const blobUrl = URL.createObjectURL(res.data);
      widget.preview = blobUrl;
    }
    await nextTick(); // wait for DOM to update before measuring
    await resizeWidgetToContent(widget);
  }
};

const resizeWidgetToContent = async (widget) => {
  if (!previewBox.value || !widget) return;
  const el = previewBox.value;
  el.innerHTML = '';

  // Create the container with the right font settings
  const container = document.createElement('div');
  container.style.fontSize = (widget.fontSize || 14) + 'px';
  container.style.fontFamily = widget.fontFamily;
  container.style.fontStyle = widget.isItalic ? 'italic' : 'normal';
  // Variable-font weight axis for bold vs. regular
  container.style.fontVariationSettings = widget.isBold
    ? "'wght' 700"
    : "'wght' 400";
  container.style.display = 'inline-block';
  el.appendChild(container);

  // Populate content
  if (widget.type === 'StaticText') {
    container.textContent = widget.text || '';
  } else if (widget.type === 'ValueText') {
    if (typeof widget.value === 'object' && widget.value !== null) {
      const app = createApp(WidgetDataRenderer, {
        data: { val: widget.value },
        fontSize: Number(widget.fontSize),
        fontFamily: widget.fontFamily,
        showKeys: false
      });
      app.mount(container);
    } else {
      if (widget.decimals && typeof widget.value === 'number') {
        widget.value = parseFloat(widget.value).toFixed(widget.decimals);
      } else if (typeof widget.value === 'number') {
        widget.value = parseFloat(widget.value).toFixed(0);
      } else if(widget.vlaue === null) {
        widget.value = 'No data';
      }
      container.textContent = (widget.value ?? '') + (widget.unit ?? '');
    }
  } else if (widget.type === 'Image' && widget.preview) {
    const img = document.createElement('img');
    img.src = widget.preview;
    container.appendChild(img);
    return;
  } else if (widget.type === 'ProgressBar') {
    container.style.width = widget.width + 'px';
    container.style.height = widget.height + 'px';
    return;
  }

  // Wait for the exact font style/weight to be ready
  const fontSpec = `${widget.fontSize || 14}px '${widget.fontFamily}'`;
  try {
    await document.fonts.load(fontSpec);
  } catch (e) {
    console.warn('Font load timeout:', e);
  }

  // Measure and apply
  await nextTick();
  const rect = container.getBoundingClientRect();
  widget.width  = Math.ceil(rect.width) + 3;
  widget.height = Math.ceil(rect.height);
  el.innerHTML = '';
};


const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('image', file);

  try {
    const response = await axios.post('/api/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    console.log('Uploaded:', response.data.url); // URL of uploaded image
    return response.data.url;
  } catch (error) {
    console.error('Upload failed', error);
  }
};


</script>

<style lang="css">
.grid-container {
  background-size: 10px 10px;
  background-image: linear-gradient(to right, #ddd 1px, transparent 1px),
    linear-gradient(to bottom, #ddd 1px, transparent 1px);
  position: relative;
}
#previewBox {
  box-sizing: content-box;
  padding: 0;
  margin: 0;
  border: none;
  line-height: normal;
  font-family: Arial, sans-serif;
}

.icon-wrapper {
  position: relative;
  display: inline-block;
  cursor: pointer;
  padding: 4px;
}
.icon-wrapper.active i {
  color: #00cc44; /* green when active */
}
.icon-wrapper .tooltip {
  visibility: hidden;
  background: #333;
  color: #fff;
  text-align: center;
  padding: 4px 8px;
  border-radius: 4px;
  position: absolute;
  bottom: 100%; 
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  z-index: 10;
}
.icon-wrapper:hover .tooltip {
  visibility: visible;
  opacity: 1;
}

.loader {
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
