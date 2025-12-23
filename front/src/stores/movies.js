import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useMovieStore = defineStore('movie', () => {
  const movies = ref([])
  const genreMovies = ref({}) // 장르별 영화 저장
  const currentMovie = ref(null)
  const currentReviews = ref([]) // Added for reviews
  const trailerId = ref(null) // Added for trailer
  const authStore = useAuthStore()
  

  const API_URL = authStore.API_URL
  const TMDB_API_KEY = import.meta.env.VITE_TMDB_API_KEY
  const YOUTUBE_API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY


  const getMovies = async () => {
    try {
      const response = await axios({
        method: 'get',
        url: `${API_URL}/api/v1/movies/`
      })
      movies.value = response.data
    } catch (error) {
      console.error('Error fetching movies:', error)
    }
  }

  const getMoviesByGenre = async (genreName) => {
    try {
      const response = await axios({
        method: 'get',
        url: `${API_URL}/api/v1/movies/`,
        params: { genre: genreName }
      })
      // 장르 이름을 키로 사용하여 저장
      genreMovies.value[genreName] = response.data
      return response.data
    } catch (error) {
      console.error(`Error fetching movies for genre ${genreName}:`, error)
      return []
    }
  }

  const getMovieDetail = async (movieId) => {
    try {
      const headers = {}
      if (authStore.token) {
        headers.Authorization = `Token ${authStore.token}`
      }
      const response = await axios({
        method: 'get',
        url: `${API_URL}/api/v1/movies/${movieId}/`,
        headers
      })
      currentMovie.value = response.data
    } catch (error) {
      console.error('Error fetching movie detail:', error)
    }
  }

  const likeMovie = async (movieId) => {
    try {
      const response = await axios({
        method: 'post',
        url: `${API_URL}/api/v1/movies/${movieId}/likes/`,
        headers: {
          Authorization: `Token ${authStore.token}`
        }
      })
      // Update the local state
      // movieId from route params is a string, so we convert it or use loose equality
      if (currentMovie.value && currentMovie.value.id === Number(movieId)) {
        currentMovie.value.is_liked = response.data.is_liked
      }
    } catch (error) {
        console.error('Error liking movie:', error)
        throw error
    }
  }

  // New actions for reviews
  const getReviews = async (movieId) => {
    try {
      const response = await axios({
        method: 'get',
        url: `${API_URL}/api/v1/movies/${movieId}/reviews/`,
        headers: {
            Authorization: `Token ${authStore.token}`
        }
      })
      currentReviews.value = response.data
    } catch (error) {
      console.error('Error fetching reviews:', error)
    }
  }

  const createReview = async (movieId, payload) => {
    try {
      await axios({
        method: 'post',
        url: `${API_URL}/api/v1/movies/${movieId}/reviews/`,
        data: payload,
        headers: {
          Authorization: `Token ${authStore.token}`
        }
      })
      // Refresh reviews after creation
      await getReviews(movieId)
    } catch (error) {
      console.error('Error creating review:', error)
      throw error
    }
  }

  const deleteReview = async (movieId, reviewId) => {
    try {
      await axios({
        method: 'delete',
        url: `${API_URL}/api/v1/movies/${movieId}/reviews/${reviewId}/`,
        headers: {
          Authorization: `Token ${authStore.token}`
        }
      })
      // 로컬 상태 업데이트: 삭제된 리뷰 제거
      currentReviews.value = currentReviews.value.filter(review => review.id !== reviewId)
    } catch (error) {
      console.error('Error deleting review:', error)
      throw error
    }
  }

  const getMovieTrailer = async (tmdbId, movieTitle) => {
    trailerId.value = null
    try {
      // 1. Try TMDB API
      const tmdbResponse = await axios.get(`https://api.themoviedb.org/3/movie/${tmdbId}/videos`, {
        params: {
          api_key: TMDB_API_KEY,
          language: 'ko-KR'
        }
      })
      
      const videos = tmdbResponse.data.results
      let trailer = videos.find(v => v.site === 'YouTube' && v.type === 'Trailer')
      
      // If no Korean trailer, try English
      if (!trailer) {
         const tmdbResponseEn = await axios.get(`https://api.themoviedb.org/3/movie/${tmdbId}/videos`, {
            params: {
              api_key: TMDB_API_KEY,
              language: 'en-US'
            }
          })
          trailer = tmdbResponseEn.data.results.find(v => v.site === 'YouTube' && v.type === 'Trailer')
      }

      if (trailer) {
        trailerId.value = trailer.key
        return
      }

      // 2. Fallback to YouTube Search API
      console.log('TMDB trailer not found, searching YouTube...')
      const query = `${movieTitle} 예고편` // 공식 예고편
      const youtubeResponse = await axios.get('https://www.googleapis.com/youtube/v3/search', {
        params: {
          part: 'snippet',
          q: query,
          type: 'video',
          key: YOUTUBE_API_KEY,
          maxResults: 1
        }
      })

      if (youtubeResponse.data.items.length > 0) {
        trailerId.value = youtubeResponse.data.items[0].id.videoId
      }

    } catch (error) {
      console.error('Error fetching trailer:', error)
    }
  }

  return { 
    movies, 
    genreMovies, 
    currentMovie, 
    currentReviews,
    trailerId, 
    getMovies, 
    getMoviesByGenre, 
    getMovieDetail,
    likeMovie,
    getReviews,
    createReview,
    deleteReview,
    getMovieTrailer 
  }
})