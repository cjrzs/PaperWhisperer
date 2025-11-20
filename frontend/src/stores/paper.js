import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/client'

export const usePaperStore = defineStore('paper', () => {
  // State
  const currentPaper = ref(null)
  const paperMetadata = ref(null)
  const translation = ref(null)
  const summary = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const hasPaper = computed(() => currentPaper.value !== null)
  const hasTranslation = computed(() => translation.value !== null)
  const hasSummary = computed(() => summary.value !== null)

  // Actions
  async function loadPaper(paperId) {
    loading.value = true
    error.value = null
    try {
      const data = await api.getPaper(paperId)
      currentPaper.value = data
      paperMetadata.value = data.metadata
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadTranslation(paperId) {
    try {
      const data = await api.getTranslation(paperId)
      translation.value = data
    } catch (e) {
      console.error('加载翻译失败:', e)
    }
  }

  async function loadSummary(paperId) {
    try {
      const data = await api.getSummary(paperId)
      summary.value = data
    } catch (e) {
      console.error('加载摘要失败:', e)
    }
  }

  async function requestTranslation(paperId) {
    const result = await api.translatePaper(paperId)
    return result
  }

  async function requestSummary(paperId) {
    const result = await api.generateSummary(paperId)
    return result
  }

  function clearPaper() {
    currentPaper.value = null
    paperMetadata.value = null
    translation.value = null
    summary.value = null
    error.value = null
  }

  return {
    currentPaper,
    paperMetadata,
    translation,
    summary,
    loading,
    error,
    hasPaper,
    hasTranslation,
    hasSummary,
    loadPaper,
    loadTranslation,
    loadSummary,
    requestTranslation,
    requestSummary,
    clearPaper
  }
})

