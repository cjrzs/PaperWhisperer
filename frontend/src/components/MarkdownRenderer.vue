<template>
    <div class="markdown-content" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import katex from 'katex'
import 'katex/dist/katex.min.css'

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

// LaTeX 渲染函数
function renderLatex(latex, displayMode = false) {
    try {
        return katex.renderToString(latex, {
            displayMode,
            throwOnError: false,
            strict: false,
            trust: true
        })
    } catch (e) {
        console.warn('KaTeX 渲染失败:', e)
        return `<span class="katex-error">${latex}</span>`
    }
}

// 处理 LaTeX 表达式
// 使用占位符保护 LaTeX，避免 Markdown 解析干扰
function processLatex(content) {
    if (!content) return ''

    const placeholders = []
    let placeholderIndex = 0

    // 创建唯一占位符
    const createPlaceholder = (latex, displayMode) => {
        const id = `%%LATEX_PLACEHOLDER_${placeholderIndex++}%%`
        placeholders.push({ id, latex, displayMode })
        return id
    }

    // 1. 先处理块级公式 $$...$$ (贪婪匹配，跨行)
    let processed = content.replace(/\$\$([\s\S]+?)\$\$/g, (_, latex) => {
        return createPlaceholder(latex.trim(), true)
    })

    // 2. 处理 \[...\] 块级公式
    processed = processed.replace(/\\\[([\s\S]+?)\\\]/g, (_, latex) => {
        return createPlaceholder(latex.trim(), true)
    })

    // 3. 处理行内公式 $...$ (不跨行，避免匹配货币符号)
    processed = processed.replace(/\$([^\$\n]+?)\$/g, (_, latex) => {
        return createPlaceholder(latex.trim(), false)
    })

    // 4. 处理 \(...\) 行内公式
    processed = processed.replace(/\\\(([\s\S]+?)\\\)/g, (_, latex) => {
        return createPlaceholder(latex.trim(), false)
    })

    // 解析 Markdown
    let html = marked.parse(processed)

    // 还原并渲染 LaTeX
    placeholders.forEach(({ id, latex, displayMode }) => {
        const rendered = renderLatex(latex, displayMode)
        // 块级公式包装在 div 中，行内公式包装在 span 中
        const wrapper = displayMode
            ? `<div class="katex-display">${rendered}</div>`
            : `<span class="katex-inline">${rendered}</span>`
        html = html.replace(id, wrapper)
    })

    return html
}

// 渲染 Markdown 内容
const renderedContent = computed(() => {
    if (!props.content) return ''
    return processLatex(props.content)
})
</script>

<style lang="postcss">
.markdown-content {
    @apply max-w-none leading-relaxed;
}

.markdown-content h1 {
    @apply text-2xl font-bold mt-6 mb-4 text-base-content;
    font-family: 'Nunito', system-ui, sans-serif;
}

.markdown-content h2 {
    @apply text-xl font-bold mt-5 mb-3 text-base-content;
    font-family: 'Nunito', system-ui, sans-serif;
}

.markdown-content h3 {
    @apply text-lg font-bold mt-4 mb-2 text-base-content;
    font-family: 'Nunito', system-ui, sans-serif;
}

.markdown-content h4 {
    @apply text-base font-bold mt-3 mb-2 text-base-content;
    font-family: 'Nunito', system-ui, sans-serif;
}

.markdown-content p {
    @apply my-3 leading-relaxed text-base-content/90;
}

.markdown-content ul,
.markdown-content ol {
    @apply my-3 pl-6;
}

.markdown-content li {
    @apply my-1.5 text-base-content/90;
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
    @apply bg-primary/10 text-primary px-1.5 py-0.5 rounded-md text-sm font-mono;
}

.markdown-content pre {
    @apply bg-base-200 p-4 rounded-xl overflow-x-auto my-4 border border-base-300/50;
}

.markdown-content pre code {
    @apply bg-transparent text-base-content p-0;
}

.markdown-content blockquote {
    @apply border-l-4 border-primary/40 pl-4 my-4 italic text-base-content/70 bg-primary/5 py-3 pr-4 rounded-r-xl;
}

.markdown-content table {
    @apply w-full border-collapse my-4 text-sm;
}

.markdown-content th,
.markdown-content td {
    @apply border border-base-300/50 px-4 py-2.5 text-left;
}

.markdown-content th {
    @apply bg-base-200/50 font-semibold text-base-content;
}

.markdown-content td {
    @apply text-base-content/80;
}

.markdown-content a {
    @apply text-primary hover:text-primary/80 underline underline-offset-2 decoration-primary/30 hover:decoration-primary/60 transition-colors;
}

.markdown-content hr {
    @apply my-8 border-base-300/50;
}

.markdown-content img {
    @apply max-w-full h-auto rounded-xl my-4 shadow-sm;
}

.markdown-content strong {
    @apply font-bold text-base-content;
}

.markdown-content em {
    @apply italic;
}

/* 数学公式样式 - KaTeX */
.markdown-content .katex-display {
    @apply overflow-x-auto py-4 my-4;
    text-align: center;
}

.markdown-content .katex-display>.katex {
    @apply text-lg;
}

.markdown-content .katex-inline {
    @apply inline-block align-middle;
}

.markdown-content .katex-inline>.katex {
    @apply text-base;
}

/* KaTeX 颜色适配主题 */
.markdown-content .katex {
    color: inherit;
}

.markdown-content .katex-error {
    @apply text-error bg-error/10 px-2 py-1 rounded font-mono text-sm;
}

/* 确保 KaTeX 公式在深色模式下正确显示 */
.markdown-content .katex .mord,
.markdown-content .katex .mop,
.markdown-content .katex .mbin,
.markdown-content .katex .mrel,
.markdown-content .katex .mopen,
.markdown-content .katex .mclose,
.markdown-content .katex .mpunct,
.markdown-content .katex .minner {
    color: inherit;
}

/* 任务列表 */
.markdown-content input[type="checkbox"] {
    @apply mr-2 rounded border-base-300;
}
</style>
