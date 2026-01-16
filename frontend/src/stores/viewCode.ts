import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface ViewCodeState {
  code: string
  categoryIds: number[]
  expiresAt: string | null
}

export const useViewCodeStore = defineStore('viewCode', () => {
  const STORAGE_KEY = 'mediastack_view_code'

  // Load from localStorage
  const loadFromStorage = (): ViewCodeState | null => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        return JSON.parse(stored)
      }
    } catch (e) {
      console.error('Failed to load view code from storage', e)
    }
    return null
  }

  const storedState = loadFromStorage()
  const code = ref(storedState?.code || '')
  const categoryIds = ref<number[]>(storedState?.categoryIds || [])
  const expiresAt = ref<string | null>(storedState?.expiresAt || null)

  const isValid = computed(() => {
    if (!code.value) return false
    if (expiresAt.value) {
      const expiry = new Date(expiresAt.value)
      if (expiry < new Date()) return false
    }
    return true
  })

  const setViewCode = (newCode: string, newCategoryIds: number[], newExpiresAt: string | null) => {
    code.value = newCode
    categoryIds.value = newCategoryIds
    expiresAt.value = newExpiresAt

    // Save to localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      code: newCode,
      categoryIds: newCategoryIds,
      expiresAt: newExpiresAt
    }))
  }

  const clearViewCode = () => {
    code.value = ''
    categoryIds.value = []
    expiresAt.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  return {
    code,
    categoryIds,
    expiresAt,
    isValid,
    setViewCode,
    clearViewCode
  }
})
