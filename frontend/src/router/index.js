import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import PaperView from '../views/PaperView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/paper/:paperId',
    name: 'Paper',
    component: PaperView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

