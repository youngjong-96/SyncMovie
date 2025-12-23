import { defineStore } from 'pinia'

export const useRecommendStore = defineStore('recommend', {
  state: () => ({
    selectedType: null,
    selectedMovies: [],
    recommendations: [],
    showRecommendations: false,
    seenUnselectedMovies: [],
  }),
  actions: {
    initType(type) {
      this.selectedType = type
      this.selectedMovies = []
      this.recommendations = []
      this.showRecommendations = false
      this.seenUnselectedMovies = []
    },
    resetAll() {
      this.selectedType = null
      this.selectedMovies = []
      this.recommendations = []
      this.showRecommendations = false
      this.seenUnselectedMovies = []
    }
  }
})