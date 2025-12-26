<template>
  <div class="paper-view container mx-auto px-4 py-6">
    <!-- Loading State -->
    <div v-if="paperStore.loading" class="flex flex-col justify-center items-center min-h-[400px] gap-4">
      <div class="loading loading-spinner loading-lg text-primary"></div>
      <p class="text-base-content/60">正在加载论文...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="paperStore.error" class="card-modern p-6 border-error/30">
      <div class="flex items-center gap-3 text-error">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="font-medium">{{ paperStore.error }}</span>
      </div>
    </div>

    <!-- Paper Content -->
    <div v-else-if="paperStore.hasPaper" class="space-y-6">
      <!-- Back Button -->
      <button @click="router.push('/history')" class="btn btn-ghost btn-sm rounded-xl gap-2 -ml-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回列表
      </button>
      
      <!-- Paper Header -->
      <div class="card-modern p-6 md:p-8">
        <h1 class="font-heading text-2xl md:text-3xl font-bold text-base-content mb-4">
          {{ paperStore.paperMetadata.title }}
        </h1>
        
        <div v-if="paperStore.paperMetadata.authors" class="flex items-center gap-2 text-base-content/60 mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span class="text-sm">{{ paperStore.paperMetadata.authors.join(', ') }}</span>
        </div>
        
        <div v-if="paperStore.paperMetadata.abstract" class="pt-4 border-t border-base-300/50">
          <h3 class="font-heading font-semibold text-base-content/80 mb-3 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
            </svg>
            摘要
          </h3>
          <MarkdownRenderer :content="paperStore.paperMetadata.abstract" class="text-base-content/80 text-sm leading-relaxed" />
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div class="flex gap-1 p-1 bg-base-200/50 rounded-2xl w-fit">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          class="px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200"
          :class="activeTab === tab.id 
            ? 'bg-base-100 text-primary shadow-sm' 
            : 'text-base-content/60 hover:text-base-content hover:bg-base-100/50'"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <transition name="fade" mode="out-in">
          <div v-if="activeTab === 'original'" key="original" class="card-modern p-6">
            <PaperStructure :sections="paperStore.currentPaper.sections" />
          </div>

          <div v-else-if="activeTab === 'translation'" key="translation">
            <TranslationView :paper-id="paperId" />
          </div>

          <div v-else-if="activeTab === 'summary'" key="summary">
            <SummaryPanel :paper-id="paperId" />
          </div>

          <div v-else-if="activeTab === 'chat'" key="chat">
            <ChatWindow :paper-id="paperId" />
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePaperStore } from '../stores/paper'
import PaperStructure from '../components/PaperStructure.vue'
import TranslationView from '../components/TranslationView.vue'
import SummaryPanel from '../components/SummaryPanel.vue'
import ChatWindow from '../components/ChatWindow.vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'

const route = useRoute()
const router = useRouter()
const paperStore = usePaperStore()

const paperId = ref(route.params.paperId)
const activeTab = ref('original')

const tabs = [
  { id: 'original', label: '原文' },
  { id: 'translation', label: '翻译' },
  { id: 'summary', label: '摘要' },
  { id: 'chat', label: '对话' }
]

onMounted(async () => {
  await paperStore.loadPaper(paperId.value)
})
</script>
