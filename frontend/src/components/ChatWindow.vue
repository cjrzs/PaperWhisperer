<template>
  <div class="chat-window">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body p-0 h-[600px] flex flex-col">
        <!-- Header -->
        <div class="p-4 border-b border-base-300 flex justify-between items-center">
          <h2 class="card-title">与论文对话</h2>
          <button v-if="chatStore.currentSessionId" class="btn btn-ghost btn-sm" @click="clearChat">
            清空对话
          </button>
        </div>

        <!-- Messages -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
          <div v-if="messages.length === 0" class="text-center p-12 opacity-60">
            <div class="text-6xl mb-4">💬</div>
            <p>问我任何关于这篇论文的问题</p>
            <div class="mt-6 text-left max-w-md mx-auto">
              <p class="text-sm font-bold mb-2">示例问题：</p>
              <ul class="text-sm space-y-1 opacity-70">
                <li>• 这篇论文的主要贡献是什么？</li>
                <li>• 作者使用了什么研究方法？</li>
                <li>• 实验结果如何？</li>
                <li>• 这项研究有什么局限性？</li>
              </ul>
            </div>
          </div>

          <div v-for="(message, index) in messages" :key="index" class="chat"
            :class="message.role === 'user' ? 'chat-end' : 'chat-start'">
            <div class="chat-bubble" :class="message.role === 'user' ? 'chat-bubble-primary' : 'chat-bubble-ai'">
              <!-- 用户消息直接显示文本 -->
              <div v-if="message.role === 'user'" class="whitespace-pre-wrap">{{ message.content }}</div>
              <!-- AI 消息使用 Markdown 渲染 -->
              <MarkdownRenderer v-else :content="message.content" class="chat-markdown" />

              <!-- Sources -->
              <div v-if="message.sources && message.sources.length > 0"
                class="mt-3 pt-3 border-t border-base-content/20">
                <details class="text-xs opacity-70">
                  <summary class="cursor-pointer">来源 ({{ message.sources.length }})</summary>
                  <div class="mt-2 space-y-1">
                    <div v-for="(source, i) in message.sources" :key="i" class="text-xs">
                      <span class="font-bold">{{ source.metadata.section_title }}:</span>
                      {{ source.text.substring(0, 100) }}...
                    </div>
                  </div>
                </details>
              </div>
            </div>
            <div class="chat-footer opacity-50 text-xs mt-1">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>

          <div v-if="loading" class="chat chat-start">
            <div class="chat-bubble">
              <span class="loading loading-dots loading-sm"></span>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="p-4 border-t border-base-300">
          <div class="join w-full">
            <input v-model="inputMessage" type="text" placeholder="输入你的问题..."
              class="input input-bordered join-item flex-1" :disabled="loading" @keypress.enter="sendMessage" />
            <button class="btn btn-primary join-item" @click="sendMessage" :disabled="!inputMessage.trim() || loading">
              发送
            </button>
          </div>
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

<style scoped>
/* AI 聊天气泡样式 */
.chat-bubble-ai {
  @apply bg-base-200;
}

/* 聊天中的 Markdown 样式调整 */
.chat-markdown :deep(.markdown-content) {
  @apply text-sm;
}

.chat-markdown :deep(.markdown-content p) {
  @apply my-2;
}

.chat-markdown :deep(.markdown-content h1),
.chat-markdown :deep(.markdown-content h2),
.chat-markdown :deep(.markdown-content h3) {
  @apply mt-3 mb-2;
}

.chat-markdown :deep(.markdown-content ul),
.chat-markdown :deep(.markdown-content ol) {
  @apply my-2 pl-4;
}

.chat-markdown :deep(.markdown-content pre) {
  @apply my-2 p-2 text-xs;
}

.chat-markdown :deep(.markdown-content code) {
  @apply text-xs;
}
</style>
