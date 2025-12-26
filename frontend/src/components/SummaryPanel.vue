<template>
  <div class="summary-panel">
    <div class="card-modern overflow-hidden">
      <!-- Header -->
      <div class="px-5 py-4 border-b border-base-300/50 flex justify-between items-center bg-base-100">
        <h2 class="font-heading font-bold text-lg flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          论文摘要
        </h2>
        <div class="flex gap-2">
          <button 
            v-if="!paperStore.hasSummary && !generating"
            class="btn btn-primary btn-sm rounded-xl gap-1"
            @click="generateSummary"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            生成摘要
          </button>
          <div v-if="generating" class="flex items-center gap-2 text-sm text-base-content/60">
            <span class="loading loading-spinner loading-sm text-primary"></span>
            生成中...
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="p-5 bg-base-200/30">
        <!-- Summary Content -->
        <div v-if="paperStore.hasSummary" class="space-y-4">
          <!-- Overall Summary -->
          <div class="bg-base-100 rounded-xl p-5 border border-base-300/50">
            <h3 class="font-heading font-semibold text-base mb-3 flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-primary"></span>
              综合摘要
            </h3>
            <MarkdownRenderer :content="paperStore.summary.overall_summary" class="text-sm text-base-content/80" />
          </div>

          <!-- Key Points -->
          <div v-if="paperStore.summary.key_points && paperStore.summary.key_points.length > 0" class="bg-base-100 rounded-xl p-5 border border-base-300/50">
            <h3 class="font-heading font-semibold text-base mb-3 flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-secondary"></span>
              关键要点
            </h3>
            <MarkdownRenderer :content="formatKeyPoints(paperStore.summary.key_points)" class="text-sm text-base-content/80" />
          </div>

          <!-- Methodology -->
          <div v-if="paperStore.summary.methodology" class="bg-base-100 rounded-xl p-5 border border-base-300/50">
            <h3 class="font-heading font-semibold text-base mb-3 flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-accent"></span>
              研究方法
            </h3>
            <MarkdownRenderer :content="paperStore.summary.methodology" class="text-sm text-base-content/80" />
          </div>

          <!-- Contributions -->
          <div v-if="paperStore.summary.contributions" class="bg-base-100 rounded-xl p-5 border border-base-300/50">
            <h3 class="font-heading font-semibold text-base mb-3 flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-success"></span>
              主要贡献
            </h3>
            <MarkdownRenderer :content="paperStore.summary.contributions" class="text-sm text-base-content/80" />
          </div>

          <!-- Section Summaries -->
          <div v-if="paperStore.summary.section_summaries && paperStore.summary.section_summaries.length > 0" class="bg-base-100 rounded-xl p-5 border border-base-300/50">
            <h3 class="font-heading font-semibold text-base mb-4 flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-warning"></span>
              章节摘要
            </h3>
            <div class="space-y-4">
              <div 
                v-for="(section, index) in paperStore.summary.section_summaries" 
                :key="index"
                class="pl-4 border-l-2 border-primary/30"
              >
                <h4 class="font-medium text-sm mb-2">{{ section.section_title }}</h4>
                <MarkdownRenderer :content="section.summary" class="text-sm text-base-content/70" />
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="!generating" class="text-center py-16">
          <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-primary/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p class="text-base-content/60">点击"生成摘要"按钮获取论文要点</p>
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
const generating = ref(false)

// 将关键要点数组格式化为 Markdown 列表
function formatKeyPoints(points) {
  if (!points || points.length === 0) return ''
  return points.map(point => `- ${point}`).join('\n')
}

onMounted(async () => {
  await paperStore.loadSummary(props.paperId)
})

async function generateSummary() {
  generating.value = true
  try {
    const result = await paperStore.requestSummary(props.paperId)
    
    // 轮询摘要状态
    await pollSummaryStatus(result.task_id)
  } catch (e) {
    console.error('生成摘要失败:', e)
    alert('生成摘要失败: ' + e.message)
  } finally {
    generating.value = false
  }
}

async function pollSummaryStatus(taskId) {
  // 简化实现：等待一段时间后重新加载
  setTimeout(async () => {
    await paperStore.loadSummary(props.paperId)
  }, 10000)
}
</script>
