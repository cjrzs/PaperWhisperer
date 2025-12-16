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
    let sid = sessionId || currentSessionId.value

    // 如果没有 session_id，先创建一个
    if (!sid) {
      sid = await createSession(paperId)
    }

    // 确保 currentSessionId 已设置
    currentSessionId.value = sid

    // 添加用户消息
    if (!sessions.value[sid]) {
      sessions.value[sid] = { paperId, messages: [] }
    }

    // 添加用户消息 - 直接更新 sessions.value 以确保响应式
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

    // 调试：打印响应
    console.log('收到响应:', response)

    // 添加助手回复
    // 确保获取正确的内容字段
    const content = response.message?.content || response.content || response.answer || '无响应'
    console.log('提取的内容:', content)
    
    // 添加助手消息 - 直接更新 sessions.value 以确保响应式
    sessions.value[sid].messages.push({
      role: 'assistant',
      content: typeof content === 'string' ? content : JSON.stringify(content),
      sources: response.sources || [],
      timestamp: new Date()
    })
    
    console.log('当前消息列表:', sessions.value[sid].messages)
    console.log('当前 sessionId:', sid)
    console.log('currentSessionId:', currentSessionId.value)

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

