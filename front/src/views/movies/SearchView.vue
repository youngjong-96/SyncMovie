<template>
  <div class="container my-5 pt-4 text-white">
    <h4 class="mb-3">“{{ keyword }}” 검색 결과</h4>

    <div v-if="loading">불러오는 중...</div>
    <div v-else-if="movies.length === 0">검색 결과가 없습니다.</div>
    
    <div class="movie-grid" v-else>
      <div 
      class="movie-card"
      v-for="movie in movies"
      :key="movie.id"
      @click="goToDetail(movie.id)"
      >
        <img :src="movie.poster_path" :alt="movie.title">
          <p v-if="movie.vote_average != null" class="badge text-white ms-2 mt-2 fs-6">
            평점: ⭐ {{ (movie.vote_average).toFixed(1) }}
          </p>
          <p v-else class="mb-0 text-muted">평점 정보 없음</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'   // ✅ useRouter 추가
import axios from 'axios'

const route = useRoute()
const router = useRouter()                         // ✅ router 생성

const keyword = ref(route.query.q || '')
const movies = ref([])
const loading = ref(false)

const fetchSearchMovies = async () => {
  const q = keyword.value.trim()
  if (!q) {
    movies.value = []
    return
  }
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8000/api/v1/movies/search/', {
      params: { q },
    })
    // console.log('검색 응답:', res.data)
    movies.value = res.data
  } finally {
    loading.value = false
  }
}

// 상세 페이지 이동
const goToDetail = (movieId) => {
  router.push(`/movies/${movieId}`)
}

watch(
  () => route.query.q,
  (newQ) => {
    keyword.value = newQ || ''
    fetchSearchMovies()
  },
  { immediate: true }
)
</script>


<style>
.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.movie-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.movie-card:hover, .movie-card.selected {
  border-color: #007bff;
}

.movie-card img {
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: 4px;
}

.movie-card h3 {
  margin: 10px 0;
  font-size: 16px;
}

.movie-card p.badge {
  margin-bottom: 0;
}
</style>