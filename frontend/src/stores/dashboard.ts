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

  // Actions
  async function fetchOverview() {
    loading.value.overview = true
    try {
      const response = await dashboardApi.getOverview()
      overview.value = response.data
    } finally {
      loading.value.overview = false
    }
  }

  async function fetchStatistics() {
    loading.value.statistics = true
    try {
      const response = await dashboardApi.getStatistics()
      statistics.value = response.data
    } finally {
      loading.value.statistics = false
    }
  }

  async function fetchActivity() {
    loading.value.activity = true
    try {
      const response = await dashboardApi.getActivity()
      activity.value = response.data
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
    fetchOverview,
    fetchStatistics,
    fetchActivity,
    refreshAll
  }
})
