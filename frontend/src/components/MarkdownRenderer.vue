<template>
    <div class="markdown-content" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
    content: {
        type: String,
        default: ''
    }
})

// 配置 marked
marked.setOptions({
    gfm: true,           // 支持 GitHub Flavored Markdown
    breaks: true,        // 支持换行符转换为 <br>
})

// 渲染 Markdown 内容
const renderedContent = computed(() => {
    if (!props.content) return ''
    return marked.parse(props.content)
})
</script>

<style lang="postcss">
.markdown-content {
    @apply max-w-none;
}

.markdown-content h1 {
    @apply text-2xl font-bold mt-6 mb-4;
}

.markdown-content h2 {
    @apply text-xl font-bold mt-5 mb-3;
}

.markdown-content h3 {
    @apply text-lg font-bold mt-4 mb-2;
}

.markdown-content h4 {
    @apply text-base font-bold mt-3 mb-2;
}

.markdown-content p {
    @apply my-3 leading-relaxed;
}

.markdown-content ul,
.markdown-content ol {
    @apply my-3 pl-6;
}

.markdown-content li {
    @apply my-1;
}

.markdown-content ul>li {
    @apply list-disc;
}

.markdown-content ol>li {
    @apply list-decimal;
}

/* 嵌套列表样式 */
.markdown-content ul ul,
.markdown-content ol ul {
    @apply my-1 pl-4;
}

.markdown-content ul ul>li {
    list-style-type: circle;
}

.markdown-content ul ul ul>li {
    list-style-type: square;
}

.markdown-content code {
    @apply bg-base-300 px-1.5 py-0.5 rounded text-sm font-mono;
}

.markdown-content pre {
    @apply bg-base-300 p-4 rounded-lg overflow-x-auto my-4;
}

.markdown-content pre code {
    @apply bg-transparent p-0;
}

.markdown-content blockquote {
    @apply border-l-4 border-primary pl-4 my-4 italic opacity-80;
}

.markdown-content table {
    @apply w-full border-collapse my-4;
}

.markdown-content th,
.markdown-content td {
    @apply border border-base-300 px-3 py-2 text-left;
}

.markdown-content th {
    @apply bg-base-200 font-bold;
}

.markdown-content a {
    @apply text-primary hover:underline;
}

.markdown-content hr {
    @apply my-6 border-base-300;
}

.markdown-content img {
    @apply max-w-full h-auto rounded-lg my-4;
}

.markdown-content strong {
    @apply font-bold;
}

.markdown-content em {
    @apply italic;
}

/* 数学公式样式 */
.markdown-content .math {
    @apply overflow-x-auto;
}
</style>
