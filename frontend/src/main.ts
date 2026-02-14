import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/fonts.css'
import './styles/admin-theme.css'
import App from './App.vue'
import router from './router'
import { setupElementPlusScrollLock } from './utils/scrollLock'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  zIndex: 2000
})
app.mount('#app')

// ============================================================
// SCROLL LOCK SYSTEM - Enhanced for Mobile
// ============================================================
// Sets up automatic scroll locking for all Element Plus overlays
// including: Dialog, MessageBox, Select, DatePicker, etc.
const cleanupScrollLock = setupElementPlusScrollLock()

// Cleanup on page unload (for HMR)
if (import.meta.hot) {
  import.meta.hot.dispose(() => {
    cleanupScrollLock()
  })
}
