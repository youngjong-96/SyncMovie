<template>
  <div class="mypage-container container text-white">
    <div v-if="store.userProfile" class="row justify-content-center">
      <div class="col-lg-8">
        <!-- Profile Header -->
        <div class="profile-header text-center mb-5">
          <div class="profile-icon mb-3">
             <i class="bi bi-person-circle display-1 text-secondary"></i>
          </div>
          <h2 class="fw-bold">{{ store.userProfile.nickname }}님</h2>
          <p class="text-light-gray">가입일: {{ new Date(store.userProfile.date_joined).toLocaleDateString() }}</p>
        </div>

        <!-- My Favorite Movies Section -->
        <div class="my-movies mb-5">
          <h3 class="section-title mb-4 border-bottom border-secondary pb-2">
            {{ store.userProfile.nickname }}님이 선택한 영화
            <span class="badge bg-danger ms-2">{{ store.userProfile.like_movies ? store.userProfile.like_movies.length : 0 }}</span>
          </h3>
          
          <div v-if="store.userProfile.like_movies && store.userProfile.like_movies.length > 0">
            <div class="row row-cols-2 row-cols-md-3 row-cols-lg-4 g-4">
              <div v-for="movie in store.userProfile.like_movies" :key="movie.id" class="col">
                <router-link :to="{ name: 'movieDetail', params: { id: movie.id }}" class="text-decoration-none">
                  <div class="card bg-dark text-white border-0 h-100 movie-card">
                    <img :src="movie.poster_path" class="card-img-top rounded" :alt="movie.title">
                  </div>
                </router-link>
              </div>
            </div>
          </div>
           <div v-else class="text-center text-light-gray py-4 border border-secondary rounded border-dashed">
            <p class="mb-0">아직 좋아요한 영화가 없습니다.</p>
          </div>
        </div>

        <!-- My Reviews Section -->
        <div class="my-reviews">
          <h3 class="section-title mb-4 border-bottom border-secondary pb-2">
            {{ store.userProfile.nickname }}님이 작성한 리뷰
            <span class="badge bg-secondary ms-2">{{ store.userProfile.reviews ? store.userProfile.reviews.length : 0 }}</span>
          </h3>
          
          <div v-if="store.userProfile.reviews && store.userProfile.reviews.length > 0">
            <div v-for="review in paginatedReviews" :key="review.id" class="review-card card bg-dark text-white border-secondary mb-3">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h5 class="card-title text-danger mb-0">
                    <router-link :to="{ name: 'movieDetail', params: { id: review.movie_id }}" class="text-decoration-none text-danger stretched-link">
                      {{ review.movie_title }}
                    </router-link>
                  </h5>
                  <span class="badge bg-warning text-dark">⭐ {{ review.rank }}</span>
                </div>
                <p class="card-text text-light-gray">{{ review.content }}</p>
                <div class="text-end text-secondary small">
                  {{ new Date(review.created_at).toLocaleDateString() }}
                </div>
              </div>
            </div>

            <!-- Pagination -->
            <nav v-if="totalPages > 1" aria-label="Review pagination" class="mt-4">
              <ul class="pagination justify-content-center">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <button class="page-link bg-dark text-white border-secondary" @click="changePage(currentPage - 1)">&laquo;</button>
                </li>
                <li v-for="page in totalPages" :key="page" class="page-item" :class="{ active: currentPage === page }">
                  <button class="page-link bg-dark text-white border-secondary" @click="changePage(page)">{{ page }}</button>
                </li>
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                  <button class="page-link bg-dark text-white border-secondary" @click="changePage(currentPage + 1)">&raquo;</button>
                </li>
              </ul>
            </nav>

          </div>
          <div v-else class="text-center text-light-gray py-5">
            <p>아직 작성한 리뷰가 없습니다.</p>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="d-flex justify-content-center align-items-center vh-100">
      <div class="spinner-border text-danger" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';

const store = useAuthStore();
const route = useRoute();
const currentPage = ref(1);
const itemsPerPage = 5;

// 프로필 데이터 가져오는 함수
const fetchProfile = () => {
  const userId = route.params.userId;
  store.getUserProfile(userId);
};

onMounted(() => {
  fetchProfile();
});

// 라우트 파라미터가 변경되면(예: 다른 사용자의 프로필로 이동) 데이터를 다시 가져옴
watch(() => route.params.userId, () => {
  fetchProfile();
});

const paginatedReviews = computed(() => {
  if (!store.userProfile || !store.userProfile.reviews) return [];
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return store.userProfile.reviews.slice(start, end);
});

const totalPages = computed(() => {
  if (!store.userProfile || !store.userProfile.reviews) return 0;
  return Math.ceil(store.userProfile.reviews.length / itemsPerPage);
});

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};
</script>

<style scoped>
.mypage-container {
  padding-top: 120px;
  min-height: 100vh;
}

.text-light-gray {
  color: #b3b3b3;
}

.section-title {
  font-family: 'Bebas Neue', sans-serif;
  letter-spacing: 1px;
}

.review-card {
  transition: transform 0.2s;
  position: relative; /* Needed for stretched-link */
}

.review-card:hover {
  transform: translateY(-2px);
  border-color: #666 !important;
}

.movie-card {
  transition: transform 0.2s;
}

.movie-card:hover {
  transform: scale(1.05);
  z-index: 10;
}

.border-dashed {
  border-style: dashed !important;
}

/* Pagination Styles */
.page-link {
    border-color: #444;
}
.page-link:hover {
    background-color: #333;
    border-color: #444;
    color: white;
}
.page-item.active .page-link {
    background-color: #dc3545; /* Bootstrap danger color to match theme */
    border-color: #dc3545;
}
.page-item.disabled .page-link {
    background-color: #222;
    border-color: #444;
    color: #666;
}
</style>
