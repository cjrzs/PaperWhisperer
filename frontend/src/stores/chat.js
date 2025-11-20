import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/client'

export const useChatStore = defineStore('chat', () => {
  // State
  const sessions = ref({}) // { sessionId: { paperId, messages } }
  const currentSessionId = ref(null)

  // Actions
  async function createSession(paperId) {
    const data = await api.createChatSession(paperId)
    const sessionId = data.session_id
    
    sessions.value[sessionId] = {
      paperId,
      messages: []
    }
    
    currentSessionId.value = sessionId
    return sessionId
  }

  async function sendMessage(paperId, message, sessionId = null) {
    const sid = sessionId || currentSessionId.value

    // 添加用户消息
    if (!sessions.value[sid]) {
      sessions.value[sid] = { paperId, messages: [] }
    }

    sessions.value[sid].messages.push({
      role: 'user',
      content: message,
      timestamp: new Date()
    })

    // 发送到后端
    const response = await api.chatWithPaper(paperId, {
      message,
      session_id: sid,
      stream: false
    })

    // 添加助手回复
    sessions.value[sid].messages.push({
      role: 'assistant',
      content: response.message.content,
      sources: response.sources,
      timestamp: new Date()
    })

    currentSessionId.value = sid
    return response
  }

  function getSessionMessages(sessionId) {
    return sessions.value[sessionId]?.messages || []
  }

  function clearSession(sessionId) {
    if (sessionId && sessions.value[sessionId]) {
      delete sessions.value[sessionId]
    }
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null
    }
  }

  return {
    sessions,
    currentSessionId,
    createSession,
    sendMessage,
    getSessionMessages,
    clearSession
  }
})

