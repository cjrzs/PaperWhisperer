这是一个智能论文助手，他的主线功能是：
通过读取论文的 pdf 文件或者论文链接，来解析论文的内容，让 agent 深度理解论文，并与用户交流！

# 我希望能有如下功能

1. 非常重要的功能是 PDF 的读取与解析。这个我们可以使用 mineru 的现成接口来完成，关于接口的使用，请参考他们的文档：
   https://mineru.net/apiManage/docs 以及 mineru_test 两个文件！

2. 非常重要的功能是 论文翻译，注意不是简单的解析，而是提供完整的翻译，默认把英文翻译成中文，需要注意的是，不要使用机翻，需要考虑翻译的流畅性与准确性！

3. 非常重要的功能是 论文解析，提取出论文的关键部分，总结解析！

4. 根据论文内容进行对话！

# 你可以参考以下实现步骤：

🧱 一、项目整体结构
PaperWhisperer/
│
├── app/ # 主应用逻辑
│ ├── main.py # FastAPI 主入口
│ ├── config.py # 配置文件（模型路径、数据库配置等）
│ │
│ ├── routers/ # API 路由层（FastAPI 的路由）
│ │ ├── upload.py # 论文上传接口
│ │ ├── chat.py # 聊天接口（RAG 问答）
│ │ └── summary.py # 摘要生成接口
│ │
│ ├── services/ # 核心业务逻辑层
│ │ ├── pdf_parser.py # PDF 解析模块（文本提取+结构化）
│ │ ├── text_splitter.py # 分块模块
│ │ ├── embedding_builder.py # 向量生成与存储
│ │ ├── retriever.py # 向量检索（RAG 召回）
│ │ ├── llm_interface.py # 调用大模型（Qwen/OpenAI）
│ │ ├── summarizer.py # 分章节/全篇摘要生成
│ │ └── memory.py # 对话记忆（多轮上下文管理）
│ │
│ ├── utils/ # 工具包
│ │ ├── file_utils.py # 文件读写/缓存管理
│ │ ├── text_cleaner.py # 文本清洗、去页眉页脚
│ │ ├── logger.py # 日志模块
│ │ └── chunk_utils.py # 分块工具（带 token 重叠）
│ │
│ └── db/ # 数据层
│ ├── qdrant_client.py # 向量数据库封装
│ └── models/ # SQL/ORM 模型（如有）
│
├── frontend/ # 前端界面（可选）
│ ├── index.html
│ ├── src/
│ │ ├── components/
│ │ │ ├── ChatWindow.vue
│ │ │ └── PDFUploader.vue
│ │ ├── api.js
│ │ └── main.js
│ └── package.json
│
├── tests/ # 单元测试
│ ├── test_pdf_parser.py
│ ├── test_retriever.py
│ ├── test_chat_flow.py
│ └── ...
│
├── data/ # 数据缓存
│ ├── uploads/ # 用户上传的论文 PDF
│ ├── parsed/ # 解析后的中间 JSON 结果
│ ├── embeddings/ # 向量缓存
│ └── summaries/ # 自动生成的摘要文件
│
├── requirements.txt # Python 依赖
├── README.md # 项目说明文档
└── run.sh # 启动脚本（可选）

⚙️ 二、各模块职责说明
模块 功能
pdf_parser.py 提取论文标题、摘要、章节、公式，生成结构化 JSON
text_splitter.py 按 token 数拆分文本块（带重叠），保留章节标题
embedding_builder.py 调用 BCEEmbedding / OpenAI / Qwen embedding 生成向量，并写入 Qdrant
retriever.py 根据用户提问计算 embedding，相似度检索论文片段
llm_interface.py 与大语言模型通信的统一接口，支持 Qwen、GLM、OpenAI
summarizer.py 章节摘要 + 全文总结（map-reduce 风格）
memory.py 对话上下文记忆管理（短期 + 长期）
chat.py（路由） 用户提问 → 检索 → LLM 回答 → 返回结果
🧩 三、推荐技术栈
功能 推荐方案
后端框架 FastAPI
向量数据库 Qdrant（你之前就用过 👍）
Embedding 模型 BCEEmbedding / text-embedding-3-small / Qwen-embedding
LLM Qwen3 / OpenAI GPT / local vLLM
文本解析 PyMuPDF（轻量）、Grobid（结构更好）
前端 Vue3 + Tailwind（可选）
部署 Docker + Gunicorn + Uvicorn
🚀 四、启动流程（逻辑图）
📄 上传论文
↓
🧠 pdf_parser.py：提取章节 & 文本清洗
↓
✂️ text_splitter.py：分块
↓
🔢 embedding_builder.py：生成向量 + 入库
↓
💬 用户提问
↓
🔍 retriever.py：召回相关块
↓
🗣 llm_interface.py：整合上下文 + 调用模型生成回答
↓
✅ 输出回答 / 摘要 / 对比分析

🧰 五、建议的开发顺序

1️⃣ 第一步：完成 pdf_parser.py（把论文转成结构化 JSON）
2️⃣ 第二步：实现 text_splitter + embedding_builder（入库）
3️⃣ 第三步：写个简单的 retriever + llm_interface 流程（问答）
4️⃣ 最后：接上 FastAPI 路由 + 前端界面
