import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 600000, // 10 分钟超时（MinerU 解析可能需要较长时间）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
client.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
client.interceptors.response.use(
  response => {
    console.log('API 响应:', response.data)
    return response.data
  },
  error => {
    // 处理不同类型的错误信息
    let message = '请求失败'
    
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      // 如果 detail 是对象，尝试提取有用信息
      if (typeof detail === 'object') {
        message = detail.message || detail.error || JSON.stringify(detail)
      } else {
        message = detail
      }
    } else if (error.message) {
      message = error.message
    }
    
    return Promise.reject(new Error(message))
  }
)

// API 方法
const api = {
  // 上传和解析
  uploadPaper(file) {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  parseUrl(url) {
    return client.post('/parse_url', null, { params: { url } })
  },

  getParseStatus(taskId) {
    return client.get(`/parse_status/${taskId}`)
  },

  getPaper(paperId) {
    return client.get(`/paper/${paperId}`)
  },

  listPapers() {
    return client.get('/papers/list')
  },

  deletePaper(paperId) {
    return client.delete(`/paper/${paperId}`)
  },

  // 翻译
  translatePaper(paperId, sourceLang = '英文', targetLang = '中文') {
    return client.post(`/translate/${paperId}`, null, {
      params: { source_lang: sourceLang, target_lang: targetLang }
    })
  },

  getTranslationStatus(taskId) {
    return client.get(`/translate/status/${taskId}`)
  },

  getTranslation(paperId) {
    return client.get(`/translate/result/${paperId}`)
  },

  // 摘要
  generateSummary(paperId, summaryType = 'comprehensive') {
    return client.post(`/summary/${paperId}`, null, {
      params: { summary_type: summaryType }
    })
  },

  getSummary(paperId) {
    return client.get(`/summary/${paperId}`)
  },

  // 对话
  createChatSession(paperId) {
    return client.post(`/chat/new_session/${paperId}`)
  },

  chatWithPaper(paperId, data) {
    return client.post(`/chat/${paperId}`, data)
  },

  getChatHistory(sessionId) {
    return client.get(`/chat/history/${sessionId}`)
  },

  deleteSession(sessionId) {
    return client.delete(`/chat/session/${sessionId}`)
  }
}

export default api

