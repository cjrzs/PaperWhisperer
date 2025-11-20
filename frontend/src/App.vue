<template>
  <div class="min-h-screen bg-base-100">
    <!-- Header -->
    <header class="navbar bg-primary text-primary-content shadow-lg">
      <div class="container mx-auto">
        <div class="flex-1">
          <router-link to="/" class="btn btn-ghost text-xl">
            📄 PaperWhisperer
          </router-link>
        </div>
        <div class="flex-none">
          <div class="dropdown dropdown-end">
            <label tabindex="0" class="btn btn-ghost btn-circle">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
              </svg>
            </label>
            <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52 text-base-content">
              <li><router-link to="/">首页</router-link></li>
              <li><a href="/docs" target="_blank">API 文档</a></li>
              <li><a href="https://github.com/yourusername/paperwhisperer" target="_blank">GitHub</a></li>
            </ul>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto p-4">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Footer -->
    <footer class="footer footer-center p-10 bg-base-200 text-base-content mt-20">
      <div>
        <p class="font-bold">
          PaperWhisperer v1.0.0
        </p>
        <p>智能论文助手 - 让学术研究更轻松</p>
        <p class="text-sm opacity-60">Powered by FastAPI + Vue3 + Milvus</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

