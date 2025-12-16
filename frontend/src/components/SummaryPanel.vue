<template>
  <div class="summary-panel">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <!-- Actions -->
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title">论文摘要</h2>
          <div class="flex gap-2">
            <button 
              v-if="!paperStore.hasSummary && !generating"
              class="btn btn-primary btn-sm"
              @click="generateSummary"
            >
              生成摘要
            </button>
            <div v-if="generating" class="flex items-center gap-2">
              <span class="loading loading-spinner loading-sm"></span>
              <span class="text-sm">生成中...</span>
            </div>
          </div>
        </div>

        <!-- Summary Content -->
        <div v-if="paperStore.hasSummary" class="space-y-6">
          <!-- Overall Summary -->
          <div class="card bg-base-200">
            <div class="card-body">
              <h3 class="card-title text-lg">综合摘要</h3>
              <MarkdownRenderer :content="paperStore.summary.overall_summary" />
            </div>
          </div>

          <!-- Key Points -->
          <div v-if="paperStore.summary.key_points && paperStore.summary.key_points.length > 0" class="card bg-base-200">
            <div class="card-body">
              <h3 class="card-title text-lg">关键要点</h3>
              <MarkdownRenderer :content="formatKeyPoints(paperStore.summary.key_points)" />
            </div>
          </div>

          <!-- Methodology -->
          <div v-if="paperStore.summary.methodology" class="card bg-base-200">
            <div class="card-body">
              <h3 class="card-title text-lg">研究方法</h3>
              <MarkdownRenderer :content="paperStore.summary.methodology" />
            </div>
          </div>

          <!-- Contributions -->
          <div v-if="paperStore.summary.contributions" class="card bg-base-200">
            <div class="card-body">
              <h3 class="card-title text-lg">主要贡献</h3>
              <MarkdownRenderer :content="paperStore.summary.contributions" />
            </div>
          </div>

          <!-- Section Summaries -->
          <div v-if="paperStore.summary.section_summaries && paperStore.summary.section_summaries.length > 0" class="card bg-base-200">
            <div class="card-body">
              <h3 class="card-title text-lg">章节摘要</h3>
              <div class="space-y-4">
                <div 
                  v-for="(section, index) in paperStore.summary.section_summaries" 
                  :key="index"
                  class="border-l-4 border-primary pl-4"
                >
                  <h4 class="font-bold mb-1">{{ section.section_title }}</h4>
                  <MarkdownRenderer :content="section.summary" class="text-sm" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!generating" class="text-center p-12 opacity-60">
          <div class="text-6xl mb-4">📋</div>
          <p>点击"生成摘要"按钮获取论文要点</p>
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

