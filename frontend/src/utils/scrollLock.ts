/**
 * Scroll Lock Manager
 *
 * Centralized scroll locking service for modal dialogs, dropdowns, and other overlays.
 * Uses reference counting to support nested overlays.
 *
 * Features:
 * - Reference counting for nested dialogs
 * - Preserves scroll position
 * - Works reliably on mobile browsers (iOS Safari, Android Chrome)
 * - Uses data attributes for CSS hooks
 */

interface ScrollLockState {
  lockCount: number
  scrollPosition: number
  htmlOverflow: string
  bodyStyles: Map<string, string>
}

class ScrollLockManager {
  private state: ScrollLockState = {
    lockCount: 0,
    scrollPosition: 0,
    htmlOverflow: '',
    bodyStyles: new Map()
  }

  private isLocked(): boolean {
    return this.state.lockCount > 0
  }

  /**
   * Lock scroll on the document body
   */
  lock(): void {
    this.state.lockCount++

    // Only apply locks on first lock
    if (this.state.lockCount === 1) {
      this.applyLock()
    }
  }

  /**
   * Unlock scroll on the document body
   */
  unlock(): void {
    this.state.lockCount = Math.max(0, this.state.lockCount - 1)

    // Only remove locks when count reaches zero
    if (this.state.lockCount === 0 && this.isLocked()) {
      this.removeLock()
    }
  }

  /**
   * Apply scroll lock styles
   */
  private applyLock(): void {
    // Save current scroll position
    this.state.scrollPosition = window.scrollY || document.documentElement.scrollTop
    this.state.htmlOverflow = document.documentElement.style.overflow

    // Save body inline styles
    const bodyStyle = document.body.style
    const stylesToSave = ['overflow', 'position', 'width', 'height', 'top', 'left', 'margin', 'padding']
    stylesToSave.forEach(prop => {
      this.state.bodyStyles.set(prop, bodyStyle.getPropertyValue(prop))
    })

    // Set data attributes for CSS hooks
    document.body.dataset.scrollLock = 'true'
    document.documentElement.dataset.scrollLock = 'true'

    // Apply CSS variable for scroll offset (used by some CSS approaches)
    document.body.style.setProperty('--scroll-lock-offset', `-${this.state.scrollPosition}px`)

    // Apply lock styles
    bodyStyle.setProperty('overflow', 'hidden', 'important')
    bodyStyle.setProperty('position', 'fixed', 'important')
    bodyStyle.setProperty('width', '100vw', 'important')
    bodyStyle.setProperty('width', '100dvw', 'important')
    bodyStyle.setProperty('height', '100vh', 'important')
    bodyStyle.setProperty('height', '100dvh', 'important')
    bodyStyle.setProperty('top', `-${this.state.scrollPosition}px`, 'important')
    bodyStyle.setProperty('left', '0', 'important')
    bodyStyle.setProperty('margin', '0', 'important')
    bodyStyle.setProperty('padding', '0', 'important')
    bodyStyle.setProperty('touch-action', 'none', 'important')
    bodyStyle.setProperty('overscroll-behavior', 'none', 'important')

    // Lock html element as well
    document.documentElement.style.setProperty('overflow', 'hidden', 'important')
    document.documentElement.style.setProperty('touch-action', 'none', 'important')
    document.documentElement.style.setProperty('overscroll-behavior', 'none', 'important')

    // Store mobile state
    const isMobile = window.innerWidth < 768
    document.body.dataset.mobile = isMobile ? 'true' : 'false'
  }

  /**
   * Remove scroll lock styles and restore scroll position
   */
  private removeLock(): void {
    // Remove data attributes
    delete document.body.dataset.scrollLock
    delete document.documentElement.dataset.scrollLock

    // Restore body inline styles
    const bodyStyle = document.body.style
    bodyStyle.removeProperty('overflow')
    bodyStyle.removeProperty('position')
    bodyStyle.removeProperty('width')
    bodyStyle.removeProperty('height')
    bodyStyle.removeProperty('top')
    bodyStyle.removeProperty('left')
    bodyStyle.removeProperty('margin')
    bodyStyle.removeProperty('padding')
    bodyStyle.removeProperty('touch-action')
    bodyStyle.removeProperty('overscroll-behavior')
    bodyStyle.removeProperty('--scroll-lock-offset')

    // Restore html element styles
    document.documentElement.style.overflow = this.state.htmlOverflow || ''
    document.documentElement.style.removeProperty('touch-action')
    document.documentElement.style.removeProperty('overscroll-behavior')

    // Restore scroll position (use requestAnimationFrame for smoother result)
    requestAnimationFrame(() => {
      window.scrollTo(0, this.state.scrollPosition)
    })

    // Reset scroll position
    this.state.scrollPosition = 0
  }

  /**
   * Get current lock count
   */
  getLockCount(): number {
    return this.state.lockCount
  }

  /**
   * Force unlock (emergency reset)
   */
  forceUnlock(): void {
    this.state.lockCount = 0
    this.removeLock()
  }
}

// Singleton instance
export const scrollLock = new ScrollLockManager()

/**
 * Utility to lock scroll when a specific element is visible
 */
export function lockWhenElementVisible(selector: string): () => void {
  const checkLock = () => {
    const element = document.querySelector(selector)
    if (element) {
      scrollLock.lock()
    } else {
      scrollLock.unlock()
    }
  }

  // Initial check
  checkLock()

  // Set up observer
  const observer = new MutationObserver(checkLock)
  observer.observe(document.body, {
    childList: true,
    subtree: true
  })

  // Return cleanup function
  return () => {
    observer.disconnect()
    scrollLock.forceUnlock()
  }
}

/**
 * Auto-lock for Element Plus dialogs
 * Observes for dialog overlays and locks scroll accordingly
 */
export function setupElementPlusScrollLock(): () => void {
  let dialogCount = 0

  const updateLock = () => {
    const currentDialogs = document.querySelectorAll('.el-overlay, .el-dialog__wrapper, .el-message-box__wrapper').length
    const currentPopovers = document.querySelectorAll('.el-select-dropdown, .el-picker__popper, .el-popper').length

    const total = currentDialogs + currentPopovers

    if (total > 0 && dialogCount === 0) {
      scrollLock.lock()
    } else if (total === 0 && dialogCount > 0) {
      scrollLock.unlock()
    }

    dialogCount = total
  }

  // Watch for changes
  const observer = new MutationObserver(updateLock)
  observer.observe(document.body, {
    childList: true,
    subtree: true
  })

  // Initial check
  updateLock()

  // Update on resize (to update mobile state)
  const handleResize = () => {
    const isMobile = window.innerWidth < 768
    document.body.dataset.mobile = isMobile ? 'true' : 'false'
  }
  window.addEventListener('resize', handleResize)
  handleResize()

  // Return cleanup function
  return () => {
    observer.disconnect()
    window.removeEventListener('resize', handleResize)
    scrollLock.forceUnlock()
  }
}
