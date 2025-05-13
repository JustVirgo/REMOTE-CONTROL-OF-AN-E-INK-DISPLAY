<template>
  <NavBar/>
  <div class="pt-20 sm:w-60/100 items-center w-95/100 mx-auto">
    <h2 class="text-2xl font-bold mb-4">Choose how to get codes</h2>

    <!-- Code Selection -->
    <label class="block mb-1 font-medium">Select display:</label>
    <div class="mb-4 flex items-center space-x-2">
      <!-- Dropdown -->
      <div class="w-5/6">
        <select v-model="selectedDisplay" class="w-full p-2 border rounded text-center">
          <option disabled value="">-- Choose a display --</option>
          <option
            v-for="display in displayOptions"
            :key="display.id"
            :value="display"
          >
            {{ display.name }}
          </option>
        </select>
      </div>

      <!-- Clear Button -->
      <div v-if="selectedDisplay" class="flex">
        <Button color="red" tooltip="Cancel display selection" @click="selectedDisplay = ''">
              <i class="fa fa-x"></i>
        </Button>
      </div>
    </div>

    
    

    <!-- ESP Flash UI -->
    <div v-if="selectedDisplay">
      <!-- COM Port Selection -->
      <div class="mb-4">
        <label class="block mb-1 font-medium">Select COM Port:</label>
        <Button color="blue" @click="getSerialPort">
          <span>Scan and Select COM Port</span>
        </Button>
        <div v-if="selectedPort" class="mt-2 text-green-600">
          Selected Port: {{ selectedPortInfo }}
        </div>
      </div>

      <div v-if="selectedPort" class="mb-6">
        <!-- Erase & Compile/Upload -->
        <div class="flex items-center space-x-4">
          <Button color="red" :disabled="isErasing" @click="eraseFlash">
            {{ isErasing ? 'Erasing...' : 'Erase Flash' }}
          </Button>


          <Button color="green" :disabled="!canUpload || isUploading" @click="uploadAndCompileCode">
            Compile and upload Code
          </Button>
          <div
            v-if="isErasing || isUploading"
            class="loader border-4 border-blue-500 border-t-transparent rounded-full w-6 h-6 animate-spin"
          ></div>
        </div>
        <!-- Messages under Erase/Upload -->
        <div class="mt-2 text-sm space-y-1">
          <p
            v-if="eraseStatus"
            :class="{
              'text-orange-400': eraseStatus === 'processing',
              'text-green-600' : eraseStatus === 'success',
              'text-red-600'   : eraseStatus === 'error'
            }"
          >
            {{ eraseMessage }}
          </p>
          <p
            v-if="uploadStatus"
            :class="{
              'text-orange-600': uploadStatus === 'processing',
              'text-green-600' : uploadStatus === 'success',
              'text-red-600'   : uploadStatus === 'error'
            }"
          >
            {{ uploadMessage }}
          </p>
        </div>
      </div>

      <!-- .bin File Flash -->
      <div v-if="selectedPort" class="mb-6">
        <label class="block mb-1 font-medium">Upload .bin File:</label>
        <div class="mb-4 flex items-center space-x-2">
          <input
            type="file"
            accept=".bin"
            @change="onBinSelected"
            class="w-5/6 p-2 border rounded"
            
          />
          
          <div v-if="binFileName" class="flex">
            <Button color="red" tooltip="Cancel file selection" @click="binFileName = '', binFile = ''">
                  <i class="fa fa-x"></i>
            </Button>
          </div>
        </div>
        <div v-if="binFileName" class="mt-1 text-sm">
            Selected: {{ binFileName }}
          </div>
        

        <div class="mt-4">
          <div class="flex items-center space-x-4">
            <Button color="purple" :disabled="!binFile || isUploading" @click="uploadBinary">
              Flash .bin
            </Button>
            <div
              v-if="isBinUploading"
              class="loader border-4 border-blue-500 border-t-transparent rounded-full w-6 h-6 animate-spin"
            ></div>
          </div>
          <!-- Message under .bin Flash -->
          <div class="mt-2 text-sm">
            <p
              v-if="uploadBinStatus"
              :class="{
                'text-orange-600': uploadBinStatus === 'processing',
                'text-green-600' : uploadBinStatus === 'success',
                'text-red-600'   : uploadBinStatus === 'error'
              }"
            >
              {{ uploadMessage }}
            </p>
          </div>
        </div>
      </div>
    </div>
    <!-- Universal Download -->
    <div>
      <span class="block mb-1 font-medium">Or:</span>
      <Button color="purple" @click="downloadUniversalCode">
          <span>Download the display code for Arduino IDE</span>
      </Button>
    </div>

  </div>
</template>


<script setup>
import { ref, computed, onMounted, onBeforeUnmount  } from 'vue'
import { ESPLoader, Transport } from 'esptool-js'  
import NavBar from "../components/NavBar.vue"
import Button from "../components/Button.vue"
import axios from "axios";

const selectedDisplay = ref('')
const selectedPort = ref(null)
const selectedPortInfo = ref('')
const uploadStatus = ref('')
const uploadBinStatus = ref('')
const uploadMessage = ref('')
const displayOptions = ref([])
const binFile = ref(null)
const binFileName = ref('')

const eraseStatus = ref('')
const eraseMessage = ref('')
const isErasing = computed(() => eraseStatus.value === 'processing')
const isUploading = computed(() => uploadStatus.value === 'processing')
const isBinUploading = computed(() => uploadBinStatus.value === 'processing')

const canUpload = computed(() => selectedDisplay.value && selectedPort.value)

const controller = new AbortController()

// File input handler
function onBinSelected(event) {
  const file = event.target.files[0]
  if (file) {
    binFile.value = file
    binFileName.value = file.name
  }
}


const fetchDisplays = async () => {
  try {
    const response = await axios.get("/api/get-displays");
    displayOptions.value = Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error("Error loading displays:", error);
  }
};


onMounted(async () => {
  try {
    await fetchDisplays();
  } catch (error) {
    console.error('Failed to fetch data sources:', error);
  }
});

async function downloadUniversalCode() {
  try {
    const resp = await axios.get('/api/download-universal', {
      responseType: 'blob'
    })

    // create a download link for the zip
    const url = URL.createObjectURL(
      new Blob([resp.data], { type: 'application/zip' })
    )
    const a = document.createElement('a')
    a.href = url
    a.download = 'Supported_Displays.zip'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error('[UPLOADING] Universal download failed', err)
  }
}

async function getSerialPort() {
  try {
    const port = await navigator.serial.requestPort()
    const info = port.getInfo()
    selectedPort.value = port
    selectedPortInfo.value = `USB Vendor: ${info.usbVendorId}, Product: ${info.usbProductId}`
    // Reset statuses
    uploadStatus.value = ''
    uploadMessage.value = ''
    eraseStatus.value = ''
    eraseMessage.value = ''
  } catch (err) {
    console.error('Port selection cancelled or failed', err)
    uploadStatus.value = 'error'
    uploadMessage.value = 'Failed to access serial port. Please try again.'
  }
}

async function eraseFlash() {
  eraseStatus.value  = 'processing'
  eraseMessage.value = 'Erasing flash...'
  const transport = new Transport(selectedPort.value, false)
  try {
    const loader = new ESPLoader({ transport, baudRate: 115200, chipFamily: 'esp8266' })
    await loader.connect()
    await loader.sync()
    await loader.runStub()
    await loader.sync()
    await loader.eraseFlash()
    eraseStatus.value  = 'success'
    eraseMessage.value = 'Flash erased successfully!'
  } catch (error) {
    console.error('Erase failed', error)
    eraseStatus.value  = 'error'
    eraseMessage.value = 'Erase failed. Please try again.'
  } finally {
    try {
      await transport.disconnect()
    } catch (e) {
      console.warn('Error closing transport', e)
    }
  }
}


// source https://github.com/espressif/esptool-js
async function uploadAndCompileCode() {
  uploadStatus.value  = 'processing'
  uploadMessage.value = 'Compiling sketch... This will take a long time please be patient and remain on this page.'
  uploadBinStatus.value = ''

  let transport, loader
  try {
    // Ask the backend to compile the Supported_Displays sketch with our selected display
    const payload = {
      sketch: 'Supported_Displays',                // the folder name under SKETCHES_DIR
      display: selectedDisplay.value,          // the display name from the dropdown
    }
    const resp = await axios.post(
      '/api/compile-sketch',
      payload,
      { responseType: 'arraybuffer' }
    )
    const firmware = new Uint8Array(resp.data)


    // 2) Start flashing
    uploadMessage.value = 'Uploading to device...'
    transport = new Transport(selectedPort.value, /* autoOpen= */ false)
    loader    = new ESPLoader({
      transport,
      baudRate:   115200,
      chipFamily: selectedDisplay.value.chip
    })

    // 3) Enter stub mode
    await loader.connect()
    await loader.sync()
    await loader.runStub()
    await loader.sync()

    // 4) Convert and write


    const bstr = loader.ui8ToBstr(firmware)
    await loader.writeFlash({
      fileArray: [
        { address: 0x00000, data: bstr }
      ],
      flashSize:   'keep',     // don’t alter existing layout
      eraseAll:     true,     
      compress:     true,      // gzip packets on the wire
      reportProgress: (i, written, total) => {
        uploadMessage.value = `Uploading… ${(written/total*100).toFixed(1)}%`
      }
    })

    // 5) Finalize & reboot
    await loader.after()

    uploadStatus.value  = 'success'
    uploadMessage.value = 'Flash & upload successful!'
  } catch (error) {
    if (error.name === 'CanceledError') {
      console.log('[UPLOADING] User navigated away; request canceled')
    }
    console.error('[UPLOADING] Compile or upload failed', error)
    uploadStatus.value  = 'error'
    uploadMessage.value = 'Upload failed: ' + (error.response?.data?.error || error.message)
  } finally {
    // 6) Always clean up
    try { if (transport) await transport.disconnect() } catch (e) {
      console.warn('[UPLOADING] Error closing transport', e)
    }
  }
}

async function uploadBinary() {
  if (!binFile.value) return

  uploadBinStatus.value  = 'processing'
  uploadMessage.value = 'Uploading binary…'
  isUploading.value  = true
  uploadStatus.value = ''

  // Make sure port isn’t already open
  try { await selectedPort.value.close() } catch {}

  let transport, loader
  try {
    // Read .bin into a Uint8Array
    const raw = await binFile.value.arrayBuffer()
    const firmware = new Uint8Array(raw)

    // Set up transport+loader
    transport = new Transport(selectedPort.value, /*autoOpen=*/false)
    loader    = new ESPLoader({
      transport,
      baudRate: 115200,
      chipFamily: selectedDisplay.value.chip
    })

    // Boot into stub
    await loader.connect()
    await loader.sync()
    await loader.runStub()
    await loader.sync()

    // Convert to loader byte-string and write
    const bstr = loader.ui8ToBstr(firmware)
    await loader.writeFlash({
      fileArray: [{ address: 0x10000, data: bstr }],
      flashSize: 'keep',
      eraseAll: false,
      compress: true,
      reportProgress: (i, written, total) => {
        uploadMessage.value = `Uploading… ${(written/total*100).toFixed(1)}%`
      }
    })

    // Finish & reboot
    await loader.after()

    uploadBinStatus.value  = 'success'
    uploadMessage.value = 'Flash & upload successful!'
  } catch (err) {
    console.error('[UPLOADING] Binary upload failed', err)
    uploadBinStatus.value  = 'error'
    uploadMessage.value = 'Upload failed: ' + err.message
  } finally {
    // Always disconnect
    try { if (transport) await transport.disconnect() } catch {}
    isUploading.value = false
  }
}

onBeforeUnmount(() => {
  controller.abort()
  if (selectedPort.value) {
    selectedPort.value.close().catch(() => {})
  }
})

</script>
