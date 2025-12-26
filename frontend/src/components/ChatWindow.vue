<template>
  <div class="chat-window">
    <div class="card-modern overflow-hidden">
      <!-- Header -->
      <div class="px-5 py-4 border-b border-base-300/50 flex justify-between items-center bg-base-100">
        <h2 class="font-heading font-bold text-lg flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          与论文对话
        </h2>
        <button v-if="chatStore.currentSessionId" class="btn btn-ghost btn-sm rounded-xl gap-1" @click="clearChat">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          清空
        </button>
      </div>

      <!-- Messages -->
      <div ref="messagesContainer" class="h-[500px] overflow-y-auto p-5 space-y-4 bg-base-200/30">
        <!-- Empty State -->
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center">
          <div class="w-16 h-16 mb-4 rounded-2xl bg-primary/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <p class="font-medium text-base-content mb-4">问我任何关于这篇论文的问题</p>
          <div class="text-left max-w-sm">
            <p class="text-xs font-medium text-base-content/60 mb-2">示例问题：</p>
            <ul class="text-sm text-base-content/50 space-y-1">
              <li class="flex items-center gap-2">
                <span class="w-1 h-1 rounded-full bg-primary"></span>
                这篇论文的主要贡献是什么？
              </li>
              <li class="flex items-center gap-2">
                <span class="w-1 h-1 rounded-full bg-primary"></span>
                作者使用了什么研究方法？
              </li>
              <li class="flex items-center gap-2">
                <span class="w-1 h-1 rounded-full bg-primary"></span>
                实验结果如何？
              </li>
              <li class="flex items-center gap-2">
                <span class="w-1 h-1 rounded-full bg-primary"></span>
                这项研究有什么局限性？
              </li>
            </ul>
          </div>
        </div>

        <!-- Messages List -->
        <template v-for="(message, index) in messages" :key="index">
          <!-- User Message -->
          <div v-if="message.role === 'user'" class="flex justify-end">
            <div class="max-w-[80%]">
              <div class="bg-primary text-primary-content px-4 py-3 rounded-2xl rounded-br-md">
                <div class="whitespace-pre-wrap text-sm">{{ message.content }}</div>
              </div>
              <div class="text-xs text-base-content/40 mt-1 text-right">
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
          </div>

          <!-- AI Message -->
          <div v-else class="flex justify-start">
            <div class="max-w-[80%]">
              <div class="bg-base-100 border border-base-300/50 px-4 py-3 rounded-2xl rounded-bl-md shadow-sm">
                <MarkdownRenderer :content="message.content" class="text-sm" />

                <!-- Sources -->
                <div v-if="message.sources && message.sources.length > 0" class="mt-3 pt-3 border-t border-base-300/50">
                  <details class="text-xs">
                    <summary class="cursor-pointer text-base-content/60 hover:text-base-content font-medium">
                      来源 ({{ message.sources.length }})
                    </summary>
                    <div class="mt-2 space-y-2">
                      <div v-for="(source, i) in message.sources" :key="i" class="p-2 bg-base-200/50 rounded-lg">
                        <span class="font-medium text-primary">{{ source.metadata.section_title }}:</span>
                        <span class="text-base-content/70"> {{ source.text.substring(0, 100) }}...</span>
                      </div>
                    </div>
                  </details>
                </div>
              </div>
              <div class="text-xs text-base-content/40 mt-1">
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
          </div>
        </template>

        <!-- Loading Indicator -->
        <div v-if="loading" class="flex justify-start">
          <div class="bg-base-100 border border-base-300/50 px-4 py-3 rounded-2xl shadow-sm">
            <div class="flex items-center gap-2">
              <span class="loading loading-dots loading-sm text-primary"></span>
              <span class="text-sm text-base-content/60">正在思考...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="p-4 border-t border-base-300/50 bg-base-100">
        <div class="flex gap-2">
          <input 
            v-model="inputMessage" 
            type="text" 
            placeholder="输入你的问题..."
            class="input input-bordered flex-1 rounded-xl bg-base-100 focus:border-primary focus:ring-2 focus:ring-primary/20" 
            :disabled="loading" 
            @keypress.enter="sendMessage" 
          />
          <button 
            class="btn btn-primary rounded-xl px-5" 
            @click="sendMessage" 
            :disabled="!inputMessage.trim() || loading"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps({
  paperId: {
    type: String,
    required: true
  }
})

const chatStore = useChatStore()
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const messages = computed(() => {
  const sessionId = chatStore.currentSessionId
  const msgs = sessionId ? chatStore.getSessionMessages(sessionId) : []
  console.log('计算消息列表:', { sessionId, msgs, sessions: chatStore.sessions })
  return msgs
})

onMounted(async () => {
  if (!chatStore.currentSessionId) {
    await chatStore.createSession(props.paperId)
  }
})

watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

async function sendMessage() {
  if (!inputMessage.value.trim() || loading.value) return

  const message = inputMessage.value
  inputMessage.value = ''
  loading.value = true

  try {
    console.log('发送消息前:', {
      currentSessionId: chatStore.currentSessionId,
      sessions: chatStore.sessions
    })
    await chatStore.sendMessage(props.paperId, message)
    console.log('发送消息后:', {
      currentSessionId: chatStore.currentSessionId,
      sessions: chatStore.sessions
    })
  } catch (e) {
    console.error('发送消息失败:', e)
    // 确保错误消息是字符串
    const errorMsg = e?.message || (typeof e === 'string' ? e : '未知错误')
    alert('发送消息失败: ' + errorMsg)
  } finally {
    loading.value = false
  }
}

function clearChat() {
  if (confirm('确定要清空对话吗？')) {
    chatStore.clearSession(chatStore.currentSessionId)
    chatStore.createSession(props.paperId)
  }
}

function formatTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>
