import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoggedIn = ref(!!token.value)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
    isLoggedIn.value = true
  }

  function logout() {
    token.value = null
    localStorage.removeItem('token')
    isLoggedIn.value = false
  }

  return { token, isLoggedIn, setToken, logout }
})
