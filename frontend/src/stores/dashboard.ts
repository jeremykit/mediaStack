import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dashboardApi, type DashboardOverview, type DashboardStatistics, type DashboardActivity } from '@/api/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const overview = ref<DashboardOverview | null>(null)
  const statistics = ref<DashboardStatistics | null>(null)
  const activity = ref<DashboardActivity | null>(null)

  const loading = ref({
    overview: false,
    statistics: false,
    activity: false
  })

  const error = ref({
    overview: null as string | null,
    statistics: null as string | null,
    activity: null as string | null
  })

  // Actions
  async function fetchOverview() {
    loading.value.overview = true
    error.value.overview = null
    try {
      const response = await dashboardApi.getOverview()
      overview.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch overview'
      error.value.overview = message
      console.error('Dashboard fetchOverview error:', err)
    } finally {
      loading.value.overview = false
    }
  }

  async function fetchStatistics() {
    loading.value.statistics = true
    error.value.statistics = null
    try {
      const response = await dashboardApi.getStatistics()
      statistics.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch statistics'
      error.value.statistics = message
      console.error('Dashboard fetchStatistics error:', err)
    } finally {
      loading.value.statistics = false
    }
  }

  async function fetchActivity() {
    loading.value.activity = true
    error.value.activity = null
    try {
      const response = await dashboardApi.getActivity()
      activity.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch activity'
      error.value.activity = message
      console.error('Dashboard fetchActivity error:', err)
    } finally {
      loading.value.activity = false
    }
  }

  async function refreshAll() {
    await Promise.all([
      fetchOverview(),
      fetchStatistics(),
      fetchActivity()
    ])
  }

  return {
    overview,
    statistics,
    activity,
    loading,
    error,
    fetchOverview,
    fetchStatistics,
    fetchActivity,
    refreshAll
  }
})
