<template>
  <div class="paper-structure">
    <div v-if="!sections || sections.length === 0" class="text-center p-8 opacity-60">
      暂无章节信息
    </div>
    
    <div v-else class="space-y-6">
      <div 
        v-for="section in sections" 
        :key="section.section_id"
        class="section-item"
      >
        <h3 
          class="font-bold mb-3 cursor-pointer hover:text-primary"
          :class="{
            'text-2xl': section.level === 1,
            'text-xl': section.level === 2,
            'text-lg': section.level === 3,
            'ml-4': section.level === 2,
            'ml-8': section.level === 3,
          }"
          @click="toggleSection(section.section_id)"
        >
          {{ section.title }}
        </h3>
        
        <div 
          v-show="expandedSections[section.section_id]"
          class="prose max-w-none"
          :class="{ 'ml-4': section.level >= 2, 'ml-8': section.level >= 3 }"
        >
          <div class="whitespace-pre-wrap text-sm">{{ section.content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

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

