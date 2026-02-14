/**
 * useScrollLock Composable
 *
 * Vue 3 Composable for managing scroll lock in components.
 * Automatically cleans up on component unmount.
 */

import { watch, onUnmounted, type Ref, type ComputedRef } from 'vue'
import { scrollLock } from '../utils/scrollLock'

export interface UseScrollLockOptions {
  /**
   * Whether to lock scroll immediately when composable is created
   * @default false
   */
  immediate?: boolean
}

type WatchSource<T> = Ref<T> | ComputedRef<T> | (() => T)

/**
 * Reactively lock scroll when a condition changes
 *
 * @param source - Ref, computed ref, or function that determines if scroll should be locked
 * @param options - Options
 *
 * @example
 * ```ts
 * const dialogVisible = ref(false)
 * useScrollLock(computed(() => dialogVisible.value))
 * ```
 */
export function useScrollLock(
  source: WatchSource<boolean>,
  options?: UseScrollLockOptions
): void {
  const checkLock = () => {
    const locked = typeof source === 'function' ? source() : (source as Ref<boolean>).value
    if (locked) {
      scrollLock.lock()
    } else {
      scrollLock.unlock()
    }
  }

  // Watch for changes
  watch(source, checkLock, { immediate: options?.immediate })

  // Clean up on unmount
  onUnmounted(() => {
    const locked = typeof source === 'function' ? source() : (source as Ref<boolean>).value
    if (locked) {
      scrollLock.unlock()
    }
  })
}

/**
 * Simple API for manual scroll lock control
 *
 * @returns Object with lock and unlock methods
 *
 * @example
 * ```ts
 * const { lock, unlock } = useScrollLockManual()
 * onMounted(() => lock())
 * onUnmounted(() => unlock())
 * ```
 */
export function useScrollLockManual() {
  return {
    lock: () => scrollLock.lock(),
    unlock: () => scrollLock.unlock(),
    getLockCount: () => scrollLock.getLockCount(),
    forceUnlock: () => scrollLock.forceUnlock()
  }
}

/**
 * Auto-lock scroll based on element visibility
 * Useful for custom modals not using Element Plus
 *
 * @param selector - CSS selector for the element to watch
 *
 * @example
 * ```ts
 * // In component setup
 * const cleanup = useScrollLockBySelector('.my-custom-modal')
 * onUnmounted(cleanup)
 * ```
 */
export function useScrollLockBySelector(selector: string) {
  const { lock, unlock } = useScrollLockManual()

  const checkVisibility = () => {
    const element = document.querySelector(selector)
    if (element) {
      lock()
    } else {
      unlock()
    }
  }

  // Set up observer
  const observer = new MutationObserver(checkVisibility)
  observer.observe(document.body, {
    childList: true,
    subtree: true
  })

  // Initial check
  checkVisibility()

  // Return cleanup function
  const cleanup = () => {
    observer.disconnect()
    unlock()
  }

  onUnmounted(cleanup)

  return cleanup
}
