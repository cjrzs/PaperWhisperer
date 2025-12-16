<template>
  <div class="translation-view">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <!-- Actions -->
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title">论文翻译</h2>
          <div class="flex gap-2">
            <button 
              v-if="!paperStore.hasTranslation && !translating"
              class="btn btn-primary btn-sm"
              @click="startTranslation"
            >
              开始翻译
            </button>
            <div v-if="translating" class="flex items-center gap-2">
              <span class="loading loading-spinner loading-sm"></span>
              <span class="text-sm">翻译中...</span>
            </div>
          </div>
        </div>

        <!-- Translation Content -->
        <div v-if="paperStore.hasTranslation" class="space-y-6">
          <!-- View Mode Toggle -->
          <div class="tabs tabs-boxed">
            <a 
              class="tab" 
              :class="{ 'tab-active': viewMode === 'bilingual' }"
              @click="viewMode = 'bilingual'"
            >
              双语对照
            </a>
            <a 
              class="tab" 
              :class="{ 'tab-active': viewMode === 'translation' }"
              @click="viewMode = 'translation'"
            >
              仅译文
            </a>
            <a 
              class="tab" 
              :class="{ 'tab-active': viewMode === 'original' }"
              @click="viewMode = 'original'"
            >
              仅原文
            </a>
          </div>

          <!-- Segments -->
          <div class="space-y-4">
            <div 
              v-for="(segment, index) in paperStore.translation.segments" 
              :key="index"
              class="segment-item"
            >
              <div v-if="segment.section_title" class="font-bold text-lg mb-2">
                {{ segment.section_title }}
              </div>

              <div v-if="viewMode === 'bilingual'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 bg-base-200 rounded-lg">
                  <div class="text-xs opacity-60 mb-1">原文</div>
                  <MarkdownRenderer :content="segment.original" class="text-sm" />
                </div>
                <div class="p-4 bg-base-200 rounded-lg">
                  <div class="text-xs opacity-60 mb-1">译文</div>
                  <MarkdownRenderer :content="segment.translated" class="text-sm" />
                </div>
              </div>

              <div v-else-if="viewMode === 'translation'" class="p-4 bg-base-200 rounded-lg">
                <MarkdownRenderer :content="segment.translated" class="text-sm" />
              </div>

              <div v-else class="p-4 bg-base-200 rounded-lg">
                <MarkdownRenderer :content="segment.original" class="text-sm" />
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!translating" class="text-center p-12 opacity-60">
          <div class="text-6xl mb-4">🌐</div>
          <p>点击"开始翻译"按钮生成论文译文</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usePaperStore } from '../stores/paper'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps({
  paperId: {
    type: String,
    required: true
  }
})

const paperStore = usePaperStore()
const viewMode = ref('bilingual')
const translating = ref(false)

onMounted(async () => {
  await paperStore.loadTranslation(props.paperId)
})

async function startTranslation() {
  translating.value = true
  try {
    const result = await paperStore.requestTranslation(props.paperId)
    
    // 轮询翻译状态
    await pollTranslationStatus(result.task_id)
  } catch (e) {
    console.error('翻译失败:', e)
    alert('翻译失败: ' + e.message)
  } finally {
    translating.value = false
  }
}

async function pollTranslationStatus(taskId) {
  // 简化实现：等待一段时间后重新加载
  setTimeout(async () => {
    await paperStore.loadTranslation(props.paperId)
  }, 5000)
}
</script>

