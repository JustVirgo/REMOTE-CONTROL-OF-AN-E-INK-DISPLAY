<template>
  <div>
    <!-- StaticText -->
    <div v-if="widget.type === 'StaticText'">
      <label class="block mb-1">Text:</label>
      <input v-model="widget.text" type="text" class="input" />

      <label class="block mb-1">Font Size (px):</label>
      <div class="relative">
        <input
          v-model.number="widget.fontSize"
          list="fontSizes"
          type="text"
          @input="sanitizePositive($event, 'fontSize')"
          class="input"
        />
        <datalist id="fontSizes">
          <option v-for="size in commonFontSizes" :key="size" :value="size">{{ size }}</option>
        </datalist>
      </div>

      <label class="block mb-1">Font Family:</label>
      <select v-model="widget.fontFamily" class="input">
        <option disabled value="">Select font</option>
        <option
          v-for="font in fontList.filter(f => !/italic/i.test(f.filename))"
          :key="font.filename"
          :value="font.family"
        >
          {{ font.family }}
        </option>
      </select>

      <div class="mt-2 flex items-center space-x-4">
        <label class="inline-flex items-center">
          <input type="checkbox" v-model="widget.isItalic" class="mr-1" />
          <span>Italic</span>
        </label>
        <label class="inline-flex items-center">
          <input type="checkbox" v-model="widget.isBold" class="mr-1" />
          <span>Bold</span>
        </label>
      </div>
    </div>

    <!-- Image -->
    <div v-else-if="widget.type === 'Image'">
      <label class="block mb-1">Upload Image:</label>
      <!-- Accept only images -->
      <input type="file" accept="image/*" @change="(event) => onImageChange(event, widget)" class="w-full h-10 mb-2 bg-white" />

      <!-- Show a preview if we have one -->
      <div v-if="widget.preview" class="my-2">
        <img
          :src="widget.preview"
          alt="Image Preview"
          class="max-w-full h-auto rounded border"
        />
      
      
        <label class="inline-flex items-center space-x-2">
          <input type="checkbox" @change='updateImageSize(widget, "width", widget.width)' v-model="widget.keepAspectRatio" />
          <span class="text-sm">Keep Aspect Ratio</span>
        </label>

        <label class="block mb-1">Width (px):</label>
        <input @input='updateImageSize(widget, "width", widget.width); sanitizePositive($event, "width")' v-model.number="widget.width" type="text" class="input" />

        <label class="block mb-1">Height (px):</label>
        <input @input='updateImageSize(widget, "height", widget.height); sanitizePositive($event, "height")' type="text" v-model.number="widget.height" class="input" />
      </div>
    </div>

    <!-- ValueText -->
    <div v-else-if="widget.type === 'ValueText'">
      <label class="block mb-1">Data Source:</label>
      <div v-if="dataSources.length === 0"> 
        <span class="text-red-500">No data sources available</span>
        <Button class="w-full" color="green" @click='router.push("/datasources")'><span>Create datasource</span></Button>
      </div>
      <select v-else v-model="widget.sourceUid" class="input">
        <option disabled value="">Select...</option>
        <option v-for="source in dataSources" :key="source.uid" :value="source.uid">
          {{ source.name }}
        </option>
      </select>

      <div v-if="selectedSource">
        <FieldBindingSelector
          v-model="widget.fieldName"
          :source-uid="widget.sourceUid"
          :data-sources="dataSources"
          :allowed-types="['number', 'string']"
        />
      </div>

      <label class="block mb-1">Font Family:</label>
      <select v-model="widget.fontFamily" class="input">
        <option disabled value="">Select font</option>
        <option
          v-for="font in fontList.filter(f => !/italic/i.test(f.filename))"
          :key="font.filename"
          :value="font.family"
        >
          {{ font.family }}
        </option>
      </select>

      <div class="mt-2 flex items-center space-x-4">
        <label class="inline-flex items-center">
          <input type="checkbox" v-model="widget.isItalic" class="mr-1" />
          <span>Italic</span>
        </label>
        <label class="inline-flex items-center">
          <input type="checkbox" v-model="widget.isBold" class="mr-1" />
          <span>Bold</span>
        </label>
      </div>
      

      <!-- Conditional Inputs -->
      <div v-if="selectedFieldType">
        <div v-if="selectedFieldType === 'number'">
          <label class="block mb-1">Decimals:</label>
          <input v-model.number="widget.decimals" type="text" @input="sanitizePositive($event, 'decimals')" class="input" />
        </div>
        
        <div v-if="selectedFieldType === 'number'">
          <label class="block mb-1">Unit:</label>
          <input v-model="widget.unit" type="text" class="input"/>
        </div>
      </div>
      
      <label class="block mb-1">Font Size (px):</label>
      <div class="relative">
        <input
          v-model.number="widget.fontSize"
          list="fontSizes"
          type="text"
          @input="sanitizePositive($event, 'fontSize')"
          class="input"
        />
        <datalist id="fontSizes">
          <option v-for="size in commonFontSizes" :key="size" :value="size">{{ size }}</option>
        </datalist>
      </div>

    </div>

    <!-- ProgressBar -->
    <div v-else-if="widget.type === 'ProgressBar'">
      <span class="text-yellow-500"><i class="fa fa-info-circle"></i> ProgressBar can be binded only to a number data source</span>
      <label class="block mb-1">Data Source:</label>
      <div v-if="dataSources.length === 0"> 
        <span class="text-red-500">No data sources available</span>
        <Button class="w-full" color="green" @click='router.push("/datasources")'><span>Create datasource</span></Button>
      </div>
      <div v-else>
        
        <select v-model="widget.sourceUid" class="input">
          <option disabled value="">Select...</option>
          <option v-for="source in dataSources" :key="source.uid" :value="source.uid">
            {{ source.name }}
          </option>
        </select>
      </div>

      <div v-if="selectedSource">
        <FieldBindingSelector
          v-model="widget.fieldName"
          :source-uid="widget.sourceUid"
          :data-sources="dataSources"
          :allowed-types="['number']"
        />
      </div>

      <!-- Min / Max / Color / Size -->
      <label class="block mb-1">Minimum Value (empty):</label>
      <input v-model.number="widget.min" type="number" class="input" />

      <label class="block mb-1">Maximum Value (full):</label>
      <input v-model.number="widget.scale" type="number" class="input" />

      <label class="block mb-1">Bar Color:</label>
      <input v-model="widget.color" type="color" class="input" />

      <label class="block mb-1">Width (px):</label>
      <input type="text" v-model.number="widget.width" @input="sanitizePositive($event, 'width')" class="input" />

      <label class="block mb-1">Height (px):</label>
      <input type="text" v-model.number="widget.height" @input="sanitizePositive($event, 'height')" class="input" />
      
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeMount } from 'vue';
import FieldBindingSelector from './FieldBindingSelector.vue';
import axios from 'axios';
import Button from './Button.vue';
import { useRouter } from 'vue-router';
const router = useRouter();



// Props & emits
const props = defineProps({ widget: Object });
const emit = defineEmits(['image-change']);
const commonFontSizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 72, 100];

function sanitizePositive(event, field) {
  const cleaned = event.target.value.replace(/[^0-9]/g, '');
  console.log('props widget', props.widget);
  console.log('props widget value', props.widget.value);
  console.log('props widget field', props.widget[field]);
  props.widget[field] = cleaned;
}

const fontList = ref([])
const dataSources = ref([])


const selectedSource = computed(() =>
  dataSources.value.find(s => s.uid === props.widget.sourceUid)
);

function getNested(obj, path) {
  return path.split('%').reduce((acc, k) => acc?.[k], obj);
}

const selectedValue = computed(() => {
  if (!selectedSource.value || !props.widget.fieldName) return null;
  return getNested(selectedSource.value.data, props.widget.fieldName);
});

const selectedFieldType = computed(() => {
  const v = selectedValue.value;
  return v == null ? '' : typeof v;
});

// Image change handler
const onImageChange = (event, widget) => {
  const file = event.target.files[0];
  if (!file) return;

  widget.file = file;
  widget.preview = URL.createObjectURL(file);
  widget._imageChanged = true;

  const img = new Image();
  img.onload = () => {
    widget.width = img.width;
    widget.height = img.height;

    widget._originalAspectRatio = calculateAspectRatio(img.width, img.height);
    widget.keepAspectRatio = true;
  };
  img.src = widget.preview;
};

const calculateAspectRatio = (width, height) => {
  return width / height;
};

const updateImageSize = (widget, changedProp, value) => {
  if(value == "") value = 0;
  if (widget.keepAspectRatio && widget._originalAspectRatio) {
    if (changedProp === 'width') {
      widget.width = value;
      widget.height = Math.round(value / widget._originalAspectRatio);
    } else if (changedProp === 'height') {
      widget.height = value;
      widget.width = Math.round(value * widget._originalAspectRatio);
    }
  } else {
    widget[changedProp] = value;
  }
};


// Load the data sources
onBeforeMount(async () => {
  const res = await axios.get('/api/get-saved-datasources');
  dataSources.value = res.data;

  const { data } = await axios.get("/api/fonts")
  fontList.value = [...new Set(data)];
  // default to first if not set:
  if (!props.widget.fontFamily && data.length) {
    props.widget.fontFamily = data[0].family
  }
});
</script>

<style scoped>
@reference "tailwindcss";

/* Hide number input spinners in WebKit (Chrome, Safari) */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Hide number input spinners in Firefox */
input[type="number"] {
  -moz-appearance: textfield;
}

.input {
  @apply w-full p-1.5 my-0.5 rounded bg-white text-base;
}
</style>
