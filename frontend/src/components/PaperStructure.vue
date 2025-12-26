<template>
  <div class="paper-structure">
    <div v-if="!sections || sections.length === 0" class="text-center py-16">
      <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-base-200 flex items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-base-content/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <p class="text-base-content/50">暂无章节信息</p>
    </div>
    
    <div v-else class="space-y-4">
      <div 
        v-for="section in sections" 
        :key="section.section_id"
        class="section-item"
      >
        <!-- Section Header -->
        <button 
          class="w-full text-left flex items-center gap-3 p-3 rounded-xl transition-colors hover:bg-base-200/50 group"
          :class="{
            'pl-3': section.level === 1,
            'pl-8': section.level === 2,
            'pl-12': section.level === 3,
          }"
          @click="toggleSection(section.section_id)"
        >
          <span 
            class="shrink-0 w-6 h-6 rounded-lg flex items-center justify-center transition-colors"
            :class="expandedSections[section.section_id] ? 'bg-primary/10 text-primary' : 'bg-base-200 text-base-content/50 group-hover:bg-base-300'"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              class="h-4 w-4 transition-transform duration-200"
              :class="{ 'rotate-90': expandedSections[section.section_id] }"
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </span>
          <h3 
            class="font-heading font-semibold text-base-content group-hover:text-primary transition-colors"
            :class="{
              'text-xl': section.level === 1,
              'text-lg': section.level === 2,
              'text-base': section.level === 3,
            }"
          >
            {{ section.title }}
          </h3>
        </button>
        
        <!-- Section Content -->
        <transition name="slide-up">
          <div 
            v-show="expandedSections[section.section_id]"
            class="mt-2 rounded-xl bg-base-200/30 border border-base-300/30 p-5"
            :class="{
              'ml-3': section.level === 1,
              'ml-8': section.level === 2,
              'ml-12': section.level === 3,
            }"
          >
            <MarkdownRenderer :content="section.content" class="text-sm" />
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps({
  sections: {
    type: Array,
    default: () => []
  }
})

const expandedSections = ref({})

function toggleSection(sectionId) {
  expandedSections.value[sectionId] = !expandedSections.value[sectionId]
}

onMounted(() => {
  // 默认展开所有一级章节
  props.sections?.forEach(section => {
    if (section.level === 1) {
      expandedSections.value[section.section_id] = true
    }
  })
})
</script>
