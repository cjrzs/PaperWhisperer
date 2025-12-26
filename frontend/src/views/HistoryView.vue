<template>
  <div class="history-view container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <div>
        <h1 class="font-heading text-3xl md:text-4xl font-bold text-base-content">论文历史</h1>
        <p class="text-base-content/60 mt-1">管理您已解析的论文</p>
      </div>
      <button @click="router.push('/')" class="btn btn-primary rounded-xl gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        上传新论文
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col justify-center items-center min-h-[400px] gap-4">
      <div class="loading loading-spinner loading-lg text-primary"></div>
      <p class="text-base-content/60">正在加载...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card-modern p-6 border-error/30">
      <div class="flex items-center gap-3 text-error">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="font-medium">{{ error }}</span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="papers.length === 0" class="text-center py-20">
      <div class="w-20 h-20 mx-auto mb-6 rounded-3xl bg-primary/10 flex items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </div>
      <h2 class="font-heading text-2xl font-bold mb-2 text-base-content">还没有解析过的论文</h2>
      <p class="text-base-content/60 mb-8">上传第一篇论文开始使用吧</p>
      <button @click="router.push('/')" class="btn btn-primary rounded-xl gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        上传论文
      </button>
    </div>

    <!-- Papers List -->
    <div v-else class="space-y-6">
      <!-- Stats Card -->
      <div class="card-modern p-5">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-base-content/60">已解析论文</p>
            <p class="text-2xl font-bold text-primary">{{ total }}</p>
          </div>
        </div>
      </div>

      <!-- Papers Grid -->
      <div class="grid gap-4">
        <div 
          v-for="paper in papers" 
          :key="paper.paper_id"
          class="card-modern p-5 cursor-pointer hover:border-primary/30 transition-all duration-200 group"
          @click="viewPaper(paper.paper_id)"
        >
          <div class="flex justify-between items-start gap-4">
            <div class="flex-1 min-w-0">
              <h2 class="font-heading text-lg font-bold text-base-content group-hover:text-primary transition-colors mb-2 line-clamp-2">
                {{ paper.title }}
              </h2>
              
              <div v-if="paper.authors && paper.authors.length > 0" class="flex items-center gap-2 text-sm text-base-content/60 mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span class="truncate">{{ paper.authors.join(', ') }}</span>
              </div>
              
              <p v-if="paper.abstract" class="text-sm text-base-content/70 line-clamp-2 leading-relaxed mb-4">
                {{ paper.abstract }}
              </p>
              
              <div class="flex items-center gap-4 text-xs text-base-content/50">
                <span class="flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ formatDate(paper.created_at) }}
                </span>
              </div>
            </div>

            <!-- Actions Dropdown -->
            <div class="dropdown dropdown-end">
              <label tabindex="0" class="btn btn-ghost btn-sm btn-square rounded-xl opacity-0 group-hover:opacity-100 transition-opacity" @click.stop>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                </svg>
              </label>
              <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow-lg bg-base-100 rounded-xl w-48 border border-base-300/50">
                <li>
                  <a @click.stop="viewPaper(paper.paper_id)" class="rounded-lg gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    查看详情
                  </a>
                </li>
                <li>
                  <a @click.stop="confirmDelete(paper)" class="rounded-lg gap-2 text-error hover:bg-error/10">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    删除
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <dialog ref="deleteDialog" class="modal">
      <div class="modal-box rounded-2xl max-w-sm">
        <div class="text-center">
          <div class="w-14 h-14 mx-auto mb-4 rounded-2xl bg-error/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </div>
          <h3 class="font-heading font-bold text-lg mb-2">确认删除</h3>
          <p class="text-sm text-base-content/70 mb-6">
            确定要删除「{{ paperToDelete?.title }}」吗？此操作不可恢复。
          </p>
        </div>
        <div class="flex gap-3">
          <button class="btn btn-ghost flex-1 rounded-xl" @click="cancelDelete">取消</button>
          <button class="btn btn-error flex-1 rounded-xl" @click="deletePaper" :disabled="deleting">
            <span v-if="deleting" class="loading loading-spinner loading-sm"></span>
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop bg-base-content/20 backdrop-blur-sm">
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
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
