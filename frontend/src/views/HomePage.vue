<template>
  <div class="hero min-h-[60vh]">
    <div class="hero-content text-center">
      <div class="max-w-4xl">
        <div class="flex justify-end mb-4">
          <button @click="router.push('/history')" class="btn btn-ghost btn-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            论文历史
          </button>
        </div>
        <h1 class="text-5xl font-bold mb-6">欢迎使用 PaperWhisperer</h1>
        <p class="text-lg mb-8 opacity-80">
          上传论文 PDF 或粘贴论文链接，让 AI 帮你深度理解学术论文
        </p>
        
        <div class="card bg-base-200 shadow-xl p-8">
          <PaperUploader @uploaded="handleUploaded" />
        </div>

        <!-- 功能介绍 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div class="card bg-base-200 p-6">
            <div class="text-4xl mb-3">📖</div>
            <h3 class="font-bold mb-2">智能解析</h3>
            <p class="text-sm opacity-70">自动提取论文结构、章节和关键信息</p>
          </div>
          
          <div class="card bg-base-200 p-6">
            <div class="text-4xl mb-3">🌐</div>
            <h3 class="font-bold mb-2">高质量翻译</h3>
            <p class="text-sm opacity-70">专业学术翻译，保持术语准确性</p>
          </div>
          
          <div class="card bg-base-200 p-6">
            <div class="text-4xl mb-3">💬</div>
            <h3 class="font-bold mb-2">智能问答</h3>
            <p class="text-sm opacity-70">基于论文内容的深度对话</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import PaperUploader from '../components/PaperUploader.vue'

const router = useRouter()

function handleUploaded(paperId) {
  router.push(`/paper/${paperId}`)
}
</script>

