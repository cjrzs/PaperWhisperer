import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import PaperView from '../views/PaperView.vue'
import HistoryView from '../views/HistoryView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryView
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

