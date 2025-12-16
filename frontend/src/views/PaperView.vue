<template>
  <div class="paper-view">
    <!-- Loading State -->
    <div v-if="paperStore.loading" class="flex justify-center items-center min-h-[400px]">
      <div class="loading loading-spinner loading-lg"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="paperStore.error" class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{{ paperStore.error }}</span>
    </div>

    <!-- Paper Content -->
    <div v-else-if="paperStore.hasPaper" class="space-y-4">
      <!-- 返回按钮 -->
      <div class="mb-4">
        <button @click="router.push('/history')" class="btn btn-ghost btn-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回历史列表
        </button>
      </div>
      
      <!-- Paper Header -->
      <div class="card bg-base-200 shadow-xl">
        <div class="card-body">
          <h1 class="card-title text-3xl">{{ paperStore.paperMetadata.title }}</h1>
          <div v-if="paperStore.paperMetadata.authors" class="text-sm opacity-70">
            作者: {{ paperStore.paperMetadata.authors.join(', ') }}
          </div>
          <div v-if="paperStore.paperMetadata.abstract" class="mt-4">
            <h3 class="font-bold mb-2">摘要</h3>
            <MarkdownRenderer :content="paperStore.paperMetadata.abstract" class="text-sm" />
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs tabs-boxed bg-base-200">
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'original' }"
          @click="activeTab = 'original'"
        >
          原文
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'translation' }"
          @click="activeTab = 'translation'"
        >
          翻译
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'summary' }"
          @click="activeTab = 'summary'"
        >
          摘要
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'chat' }"
          @click="activeTab = 'chat'"
        >
          对话
        </a>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <div v-show="activeTab === 'original'" class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <PaperStructure :sections="paperStore.currentPaper.sections" />
          </div>
        </div>

        <div v-show="activeTab === 'translation'">
          <TranslationView :paper-id="paperId" />
        </div>

        <div v-show="activeTab === 'summary'">
          <SummaryPanel :paper-id="paperId" />
        </div>

        <div v-show="activeTab === 'chat'">
          <ChatWindow :paper-id="paperId" />
        </div>
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

onMounted(async () => {
  await paperStore.loadPaper(paperId.value)
})
</script>

