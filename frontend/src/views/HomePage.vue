<template>
  <div class="min-h-[calc(100vh-4rem)]">
    <!-- Hero Section with Gradient Background -->
    <div class="relative overflow-hidden">
      <!-- Background Pattern -->
      <div class="absolute inset-0 opacity-30">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10"></div>
        <div class="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl"></div>
      </div>

      <div class="relative container mx-auto px-4 py-16 md:py-24">
        <!-- Header Actions -->
        <div class="flex justify-end mb-8">
          <button @click="router.push('/history')" class="btn btn-ghost btn-sm rounded-xl gap-2 font-medium">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            查看历史论文
          </button>
        </div>

        <!-- Hero Content -->
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="font-heading text-4xl md:text-5xl lg:text-6xl font-extrabold mb-6 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            智能论文助手
          </h1>
          <p class="text-lg md:text-xl text-base-content/70 mb-10 leading-relaxed">
            上传论文 PDF 或粘贴链接，让 AI 帮你深度解析、翻译和理解学术论文
          </p>
        </div>

        <!-- Upload Card -->
        <div class="max-w-2xl mx-auto">
          <div class="card-modern p-6 md:p-8">
            <PaperUploader @uploaded="handleUploaded" />
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="container mx-auto px-4 py-16">
      <h2 class="font-heading text-2xl md:text-3xl font-bold text-center mb-12">
        核心功能
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        <!-- Feature 1 -->
        <div class="card-modern p-6 text-center group hover:border-primary/30 transition-colors">
          <div class="w-14 h-14 mx-auto mb-4 rounded-2xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="font-heading font-bold text-lg mb-2">智能解析</h3>
          <p class="text-sm text-base-content/60 leading-relaxed">
            自动提取论文结构、章节和关键信息
          </p>
        </div>

        <!-- Feature 2 -->
        <div class="card-modern p-6 text-center group hover:border-secondary/30 transition-colors">
          <div class="w-14 h-14 mx-auto mb-4 rounded-2xl bg-secondary/10 flex items-center justify-center group-hover:bg-secondary/20 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
            </svg>
          </div>
          <h3 class="font-heading font-bold text-lg mb-2">高质量翻译</h3>
          <p class="text-sm text-base-content/60 leading-relaxed">
            专业学术翻译，保持术语准确性
          </p>
        </div>

        <!-- Feature 3 -->
        <div class="card-modern p-6 text-center group hover:border-accent/30 transition-colors">
          <div class="w-14 h-14 mx-auto mb-4 rounded-2xl bg-accent/10 flex items-center justify-center group-hover:bg-accent/20 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 class="font-heading font-bold text-lg mb-2">智能问答</h3>
          <p class="text-sm text-base-content/60 leading-relaxed">
            基于论文内容的深度对话交流
          </p>
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
