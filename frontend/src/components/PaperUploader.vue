<template>
  <div class="paper-uploader">
    <!-- URL Input -->
    <div class="form-control w-full mb-6">
      <label class="label">
        <span class="label-text">论文 URL（如 arXiv 链接）</span>
      </label>
      <div class="join w-full">
        <input 
          v-model="url" 
          type="text" 
          placeholder="https://arxiv.org/pdf/..." 
          class="input input-bordered join-item flex-1"
          :disabled="uploading"
        />
        <button 
          class="btn btn-primary join-item" 
          @click="submitUrl"
          :disabled="!url || uploading"
        >
          解析
        </button>
      </div>
    </div>

    <div class="divider">或</div>

    <!-- File Upload -->
    <div class="form-control w-full">
      <label class="label">
        <span class="label-text">上传 PDF 文件</span>
      </label>
      <div 
        class="border-2 border-dashed border-base-300 rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer"
        :class="{ 'border-primary bg-primary/10': dragOver }"
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @drop.prevent="handleDrop"
        @click="$refs.fileInput.click()"
      >
        <input 
          ref="fileInput" 
          type="file" 
          accept=".pdf" 
          class="hidden"
          @change="handleFileSelect"
        />
        
        <div v-if="!uploading">
          <div class="text-4xl mb-3">📄</div>
          <p class="font-medium">点击或拖拽 PDF 文件到此处</p>
          <p class="text-sm opacity-60 mt-2">最大支持 50MB</p>
        </div>
        
        <div v-else class="space-y-3">
          <div class="loading loading-spinner loading-lg"></div>
          <p>{{ statusMessage }}</p>
          <progress 
            v-if="progress > 0" 
            class="progress progress-primary w-full" 
            :value="progress" 
            max="100"
          ></progress>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="alert alert-error mt-4">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{{ error }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/client'

const emit = defineEmits(['uploaded'])

const url = ref('')
const dragOver = ref(false)
const uploading = ref(false)
const progress = ref(0)
const statusMessage = ref('')
const error = ref(null)
const fileInput = ref(null)

async function submitUrl() {
  if (!url.value) return
  
  uploading.value = true
  error.value = null
  statusMessage.value = '正在提交解析任务...'
  
  try {
    const result = await api.parseUrl(url.value)
    await pollStatus(result.task_id)
  } catch (e) {
    error.value = e.message
    uploading.value = false
  }
}

function handleDrop(e) {
  dragOver.value = false
  const files = e.dataTransfer.files
  if (files.length > 0 && files[0].type === 'application/pdf') {
    uploadFile(files[0])
  }
}

function handleFileSelect(e) {
  const files = e.target.files
  if (files.length > 0) {
    uploadFile(files[0])
  }
}

async function uploadFile(file) {
  if (!file || file.type !== 'application/pdf') {
    error.value = '请选择 PDF 文件'
    return
  }
  
  if (file.size > 50 * 1024 * 1024) {
    error.value = '文件大小不能超过 50MB'
    return
  }
  
  uploading.value = true
  error.value = null
  statusMessage.value = '正在上传文件...'
  progress.value = 0
  
  try {
    const result = await api.uploadPaper(file)
    await pollStatus(result.task_id)
  } catch (e) {
    error.value = e.message
    uploading.value = false
  }
}

async function pollStatus(taskId) {
  const maxAttempts = 60 // 最多轮询 5 分钟
  let attempts = 0
  
  statusMessage.value = '正在解析论文...'
  
  const poll = async () => {
    try {
      const status = await api.getParseStatus(taskId)
      progress.value = status.progress || 0
      
      if (status.status === 'completed') {
        statusMessage.value = '解析完成！'
        uploading.value = false
        emit('uploaded', status.paper_id)
        return
      } else if (status.status === 'failed') {
        error.value = status.error || '解析失败'
        uploading.value = false
        return
      }
      
      attempts++
      if (attempts < maxAttempts) {
        setTimeout(poll, 3000)
      } else {
        error.value = '解析超时，请稍后重试'
        uploading.value = false
      }
    } catch (e) {
      error.value = e.message
      uploading.value = false
    }
  }
  
  poll()
}
</script>

