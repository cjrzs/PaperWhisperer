<template>
  <div class="history-view container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-bold">论文历史</h1>
      <button @click="router.push('/')" class="btn btn-primary">
        上传新论文
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center min-h-[400px]">
      <div class="loading loading-spinner loading-lg"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{{ error }}</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="papers.length === 0" class="text-center py-16">
      <div class="text-6xl mb-4">📚</div>
      <h2 class="text-2xl font-bold mb-2">还没有解析过的论文</h2>
      <p class="text-base-content/70 mb-6">上传第一篇论文开始使用吧</p>
      <button @click="router.push('/')" class="btn btn-primary">
        上传论文
      </button>
    </div>

    <!-- Papers Grid -->
    <div v-else class="space-y-4">
      <!-- 统计信息 -->
      <div class="stats shadow w-full">
        <div class="stat">
          <div class="stat-figure text-primary">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <div class="stat-title">已解析论文</div>
          <div class="stat-value text-primary">{{ total }}</div>
          <div class="stat-desc">总计</div>
        </div>
      </div>

      <!-- 论文列表 -->
      <div class="grid gap-4">
        <div 
          v-for="paper in papers" 
          :key="paper.paper_id"
          class="card bg-base-200 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer"
          @click="viewPaper(paper.paper_id)"
        >
          <div class="card-body">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h2 class="card-title text-xl mb-2">
                  {{ paper.title }}
                </h2>
                
                <div v-if="paper.authors && paper.authors.length > 0" class="text-sm opacity-70 mb-3">
                  <span class="font-semibold">作者：</span>
                  {{ paper.authors.join(', ') }}
                </div>
                
                <p v-if="paper.abstract" class="text-sm line-clamp-3 opacity-80">
                  {{ paper.abstract }}
                </p>
                
                <div class="flex items-center gap-4 mt-4 text-xs opacity-60">
                  <span>
                    解析时间: {{ formatDate(paper.created_at) }}
                  </span>
                  <span>
                    最后修改: {{ formatDate(paper.modified_at) }}
                  </span>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="dropdown dropdown-end">
                <label tabindex="0" class="btn btn-ghost btn-sm btn-circle" @click.stop>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                  </svg>
                </label>
                <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                  <li><a @click.stop="viewPaper(paper.paper_id)">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    查看详情
                  </a></li>
                  <li><a @click.stop="confirmDelete(paper)" class="text-error">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    删除
                  </a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <dialog ref="deleteDialog" class="modal">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">确认删除</h3>
        <p class="py-4">确定要删除论文「{{ paperToDelete?.title }}」吗？此操作不可恢复。</p>
        <div class="modal-action">
          <button class="btn" @click="cancelDelete">取消</button>
          <button class="btn btn-error" @click="deletePaper" :disabled="deleting">
            <span v-if="deleting" class="loading loading-spinner loading-sm"></span>
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button @click="cancelDelete">close</button>
      </form>
    </dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'

const router = useRouter()

const papers = ref([])
const total = ref(0)
const loading = ref(false)
const error = ref(null)
const deleting = ref(false)
const deleteDialog = ref(null)
const paperToDelete = ref(null)

// 加载论文列表
async function loadPapers() {
  loading.value = true
  error.value = null
  try {
    const data = await api.listPapers()
    papers.value = data.papers
    total.value = data.total
  } catch (e) {
    error.value = e.message || '加载论文列表失败'
    console.error('加载论文列表失败:', e)
  } finally {
    loading.value = false
  }
}

// 查看论文详情
function viewPaper(paperId) {
  router.push(`/paper/${paperId}`)
}

// 格式化日期
function formatDate(timestamp) {
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now - date
  
  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  // 小于1小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)} 分钟前`
  }
  // 小于1天
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)} 小时前`
  }
  // 小于7天
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)} 天前`
  }
  
  // 否则显示具体日期
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 确认删除
function confirmDelete(paper) {
  paperToDelete.value = paper
  deleteDialog.value?.showModal()
}

// 取消删除
function cancelDelete() {
  deleteDialog.value?.close()
  paperToDelete.value = null
}

// 删除论文
async function deletePaper() {
  if (!paperToDelete.value) return
  
  deleting.value = true
  try {
    await api.deletePaper(paperToDelete.value.paper_id)
    // 从列表中移除
    papers.value = papers.value.filter(p => p.paper_id !== paperToDelete.value.paper_id)
    total.value = papers.value.length
    // 关闭对话框
    deleteDialog.value?.close()
    paperToDelete.value = null
  } catch (e) {
    error.value = e.message || '删除论文失败'
    console.error('删除论文失败:', e)
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadPapers()
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

