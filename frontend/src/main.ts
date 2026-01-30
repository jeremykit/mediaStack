import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/fonts.css'
import './styles/admin-theme.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')

// Dialog scroll lock for mobile - Enhanced version
let dialogCount = 0
let scrollPosition = 0
let isLocked = false

const lockScroll = () => {
  dialogCount++
  if (dialogCount === 1 && !isLocked) {
    isLocked = true
    scrollPosition = window.scrollY || document.documentElement.scrollTop

    // Lock body scroll
    document.body.style.overflow = 'hidden'
    document.body.style.position = 'fixed'
    document.body.style.width = '100vw'
    document.body.style.maxWidth = '100vw'
    document.body.style.height = '100vh'
    document.body.style.maxHeight = '100vh'
    document.body.style.top = `-${scrollPosition}px`
    document.body.style.left = '0'
    document.body.style.right = '0'
    document.body.style.margin = '0'
    document.body.style.padding = '0'
    document.body.style.border = 'none'
    document.body.style.outline = 'none'
    document.body.classList.add('dialog-open')

    // Also lock html element for extra safety
    document.documentElement.style.overflow = 'hidden'

    // Prevent overscroll/bounce on iOS
    ;(document.body.style as any).overscrollBehavior = 'none'
    ;(document.body.style as any).touchAction = 'none'
    ;(document.body.style as any).webkitOverflowScrolling = 'touch'
  }
}

const unlockScroll = () => {
  dialogCount--
  if (dialogCount <= 0) {
    dialogCount = 0
    if (isLocked) {
      isLocked = false

      // Restore body scroll
      document.body.style.overflow = ''
      document.body.style.position = ''
      document.body.style.width = ''
      document.body.style.maxWidth = ''
      document.body.style.height = ''
      document.body.style.maxHeight = ''
      document.body.style.top = ''
      document.body.style.left = ''
      document.body.style.right = ''
      document.body.style.margin = ''
      document.body.style.padding = ''
      document.body.style.overscrollBehavior = ''
      ;(document.body.style as any).touchAction = ''
      ;(document.body.style as any).webkitOverflowScrolling = ''
      document.body.classList.remove('dialog-open')

      // Restore html overflow
      document.documentElement.style.overflow = ''

      // Restore scroll position
      window.scrollTo(0, scrollPosition)
      scrollPosition = 0
    }
  }
}

// Count existing dialogs before observing
const countExistingDialogs = () => {
  const overlays = document.querySelectorAll('.el-overlay, .el-dialog__wrapper')
  return overlays.length
}

// Watch for dialog open/close events
const observer = new MutationObserver((mutations) => {
  // Count current dialogs after mutations
  const currentDialogs = document.querySelectorAll('.el-overlay, .el-dialog__wrapper').length

  mutations.forEach((mutation) => {
    // Handle added nodes (dialog opening)
    mutation.addedNodes.forEach((node: Node) => {
      if (node.nodeType === 1) {
        const el = node as HTMLElement
        // Check for dialog overlay or wrapper
        if (el.classList && (el.classList.contains('el-overlay') || el.classList.contains('el-dialog__wrapper'))) {
          lockScroll()
        }
        // Also check nested elements
        const nestedDialog = el.querySelector?.('.el-overlay, .el-dialog__wrapper')
        if (nestedDialog) {
          lockScroll()
        }
      }
    })

    // Handle removed nodes (dialog closing)
    mutation.removedNodes.forEach((node: Node) => {
      if (node.nodeType === 1) {
        const el = node as HTMLElement
        if (el.classList && (el.classList.contains('el-overlay') || el.classList.contains('el-dialog__wrapper'))) {
          unlockScroll()
        }
      }
    })
  })

  // Safety check: if count doesn't match, reset
  if (dialogCount !== currentDialogs && currentDialogs === 0) {
    dialogCount = 0
    unlockScroll()
  }
})

// Initial check in case dialogs exist on page load
const initialCount = countExistingDialogs()
if (initialCount > 0) {
  dialogCount = initialCount
  lockScroll()
}

observer.observe(document.body, {
  childList: true,
  subtree: true
})
