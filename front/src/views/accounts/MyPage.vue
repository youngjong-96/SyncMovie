<template>
  <div class="mypage-container container text-white">
    <div v-if="store.userProfile" class="row justify-content-center">
      <div class="col-lg-9">
        
        <!-- 1. Profile Header & Stats Dashboard -->
        <div class="profile-card rounded-4 p-4 p-md-5 mb-5 position-relative overflow-hidden">
          <div class="position-relative z-1 text-center">
            <div class="profile-avatar mb-3 mx-auto">
              <i class="bi bi-person-circle text-white"></i>
            </div>
            <h2 class="fw-bold mb-1">{{ store.userProfile.nickname }}</h2>
            <p class="text-white-50 small mb-4">
              <i class="bi bi-calendar-check me-1"></i>
              가입일: {{ new Date(store.userProfile.date_joined).toLocaleDateString() }}
            </p>

            <!-- Stats Row -->
            <div class="row g-3 justify-content-center mt-4 px-md-5">
              <div class="col-6 col-md-4">
                <div 
                  class="stat-item p-3 rounded-3 text-center cursor-pointer" 
                  :class="{ 'active': activeTab === 'movies' }"
                  @click="activeTab = 'movies'"
                >
                  <div class="stat-number text-danger">{{ store.userProfile.like_movies ? store.userProfile.like_movies.length : 0 }}</div>
                  <div class="stat-label">좋아요한 영화</div>
                </div>
              </div>
              <div class="col-6 col-md-4">
                <div 
                  class="stat-item p-3 rounded-3 text-center cursor-pointer"
                  :class="{ 'active': activeTab === 'reviews' }"
                  @click="activeTab = 'reviews'"
                >
                  <div class="stat-number text-warning">{{ store.userProfile.reviews ? store.userProfile.reviews.length : 0 }}</div>
                  <div class="stat-label">작성한 리뷰</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Tabs Navigation -->
        <div class="d-flex justify-content-center mb-4">
          <div class="nav nav-pills custom-tabs p-1 rounded-pill" role="tablist">
            <button 
              class="nav-link rounded-pill px-4" 
              :class="{ active: activeTab === 'movies' }" 
              @click="activeTab = 'movies'"
            >
              <i class="bi bi-heart-fill me-2"></i>좋아요한 영화
            </button>
            <button 
              class="nav-link rounded-pill px-4" 
              :class="{ active: activeTab === 'reviews' }" 
              @click="activeTab = 'reviews'"
            >
              <i class="bi bi-pencil-square me-2"></i>작성한 리뷰
            </button>
          </div>
        </div>

        <!-- 3. Content Area -->
        <div class="tab-content min-vh-50">
          
          <!-- Movies Tab -->
          <div v-if="activeTab === 'movies'" class="fade-in">
            <div v-if="store.userProfile.like_movies && store.userProfile.like_movies.length > 0">
              <div class="row row-cols-2 row-cols-md-3 row-cols-lg-4 g-4">
                <div v-for="movie in paginatedMovies" :key="movie.id" class="col">
                  <router-link :to="{ name: 'movieDetail', params: { id: movie.id }}" class="text-decoration-none">
                    <div class="movie-card-wrapper position-relative rounded overflow-hidden shadow-sm">
                      <img :src="movie.poster_path" class="w-100 d-block" :alt="movie.title">
                      <div class="movie-overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center opacity-0">
                         <span class="badge bg-danger fs-6">상세보기</span>
                      </div>
                    </div>
                    <div class="mt-2 text-center text-truncate small text-white-50">{{ movie.title }}</div>
                  </router-link>
                </div>
              </div>

              <!-- Movies Pagination -->
              <nav v-if="totalMoviePages > 1" aria-label="Movie pagination" class="mt-5">
                <ul class="pagination justify-content-center">
                  <li class="page-item" :class="{ disabled: currentMoviePage === 1 }">
                    <button class="page-link bg-dark text-white border-secondary" @click="changeMoviePage(currentMoviePage - 1)">
                      <i class="bi bi-chevron-left"></i>
                    </button>
                  </li>
                  <li v-for="page in totalMoviePages" :key="page" class="page-item" :class="{ active: currentMoviePage === page }">
                    <button class="page-link bg-dark text-white border-secondary" @click="changeMoviePage(page)">{{ page }}</button>
                  </li>
                  <li class="page-item" :class="{ disabled: currentMoviePage === totalMoviePages }">
                    <button class="page-link bg-dark text-white border-secondary" @click="changeMoviePage(currentMoviePage + 1)">
                      <i class="bi bi-chevron-right"></i>
                    </button>
                  </li>
                </ul>
              </nav>

            </div>
            <div v-else class="empty-state text-center py-5 rounded-4 border border-secondary border-dashed border-opacity-25">
              <i class="bi bi-film display-1 text-secondary opacity-50 mb-3 d-block"></i>
              <p class="text-secondary mb-0">아직 좋아요를 누른 영화가 없습니다.</p>
              <router-link :to="{ name: 'movies' }" class="btn btn-outline-danger btn-sm mt-3">영화 둘러보기</router-link>
            </div>
          </div>

          <!-- Reviews Tab -->
          <div v-if="activeTab === 'reviews'" class="fade-in">
            <div v-if="store.userProfile.reviews && store.userProfile.reviews.length > 0">
              <div class="review-list">
                <div v-for="review in paginatedReviews" :key="review.id" class="review-card card bg-dark text-white border-secondary mb-3 shadow-sm">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                      <router-link :to="{ name: 'movieDetail', params: { id: review.movie_id }}" class="text-decoration-none d-flex align-items-center group-link">
                        <span class="badge bg-danger me-2">MOVIE</span>
                        <h5 class="card-title text-white mb-0 me-2 hover-underline">{{ review.movie_title }}</h5>
                      </router-link>
                      <div class="rating">
                        <i class="bi bi-star-fill text-warning me-1"></i>
                        <span class="fw-bold">{{ review.rank }}</span>
                      </div>
                    </div>
                    
                    <div class="review-content bg-secondary bg-opacity-10 p-3 rounded-3 mb-3">
                      <i class="bi bi-quote text-secondary fs-4 d-block mb-1"></i>
                      <p class="card-text text-light-gray ps-2">{{ review.content }}</p>
                    </div>

                    <div class="text-end text-secondary small">
                      <i class="bi bi-clock me-1"></i>
                      {{ new Date(review.created_at).toLocaleDateString() }} 작성됨
                    </div>
                  </div>
                </div>
              </div>

              <!-- Reviews Pagination -->
              <nav v-if="totalReviewPages > 1" aria-label="Review pagination" class="mt-4">
                <ul class="pagination justify-content-center">
                  <li class="page-item" :class="{ disabled: currentReviewPage === 1 }">
                    <button class="page-link bg-dark text-white border-secondary" @click="changeReviewPage(currentReviewPage - 1)">
                      <i class="bi bi-chevron-left"></i>
                    </button>
                  </li>
                  <li v-for="page in totalReviewPages" :key="page" class="page-item" :class="{ active: currentReviewPage === page }">
                    <button class="page-link bg-dark text-white border-secondary" @click="changeReviewPage(page)">{{ page }}</button>
                  </li>
                  <li class="page-item" :class="{ disabled: currentReviewPage === totalReviewPages }">
                    <button class="page-link bg-dark text-white border-secondary" @click="changeReviewPage(currentReviewPage + 1)">
                      <i class="bi bi-chevron-right"></i>
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
            <div v-else class="empty-state text-center py-5 rounded-4 border border-secondary border-dashed border-opacity-25">
              <i class="bi bi-pencil-square display-1 text-secondary opacity-50 mb-3 d-block"></i>
              <p class="text-secondary mb-0">아직 작성한 리뷰가 없습니다.</p>
            </div>
          </div>

        </div>

      </div>
    </div>
    
    <!-- Loading Spinner -->
    <div v-else class="d-flex justify-content-center align-items-center vh-100">
      <div class="spinner-grow text-danger" style="width: 3rem; height: 3rem;" role="status">
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

// UI State
const activeTab = ref('movies'); // 'movies' or 'reviews'

// Reviews Pagination Config
const currentReviewPage = ref(1);
const reviewsPerPage = 5;

// Movies Pagination Config
const currentMoviePage = ref(1);
const moviesPerPage = 8;

// Data Fetching
const fetchProfile = () => {
  const userId = route.params.userId;
  store.getUserProfile(userId);
  // 초기화
  activeTab.value = 'movies';
  currentReviewPage.value = 1;
  currentMoviePage.value = 1;
};

onMounted(() => {
  fetchProfile();
});

watch(() => route.params.userId, () => {
  fetchProfile();
});

// --- Reviews Pagination Logic ---
const paginatedReviews = computed(() => {
  if (!store.userProfile || !store.userProfile.reviews) return [];
  const start = (currentReviewPage.value - 1) * reviewsPerPage;
  const end = start + reviewsPerPage;
  return store.userProfile.reviews.slice(start, end);
});

const totalReviewPages = computed(() => {
  if (!store.userProfile || !store.userProfile.reviews) return 0;
  return Math.ceil(store.userProfile.reviews.length / reviewsPerPage);
});

const changeReviewPage = (page) => {
  if (page >= 1 && page <= totalReviewPages.value) {
    currentReviewPage.value = page;
    window.scrollTo({ top: 300, behavior: 'smooth' });
  }
};

// --- Movies Pagination Logic ---
const paginatedMovies = computed(() => {
  if (!store.userProfile || !store.userProfile.like_movies) return [];
  const start = (currentMoviePage.value - 1) * moviesPerPage;
  const end = start + moviesPerPage;
  return store.userProfile.like_movies.slice(start, end);
});

const totalMoviePages = computed(() => {
  if (!store.userProfile || !store.userProfile.like_movies) return 0;
  return Math.ceil(store.userProfile.like_movies.length / moviesPerPage);
});

const changeMoviePage = (page) => {
  if (page >= 1 && page <= totalMoviePages.value) {
    currentMoviePage.value = page;
    window.scrollTo({ top: 300, behavior: 'smooth' });
  }
};
</script>

<style scoped>
.mypage-container {
  padding-top: 100px;
  min-height: 100vh;
  padding-bottom: 50px;
}

/* Profile Card Styles */
.profile-card {
  background: linear-gradient(145deg, #1a1a1a 0%, #0d0d0d 100%);
  border: 1px solid #333;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.profile-avatar i {
  font-size: 5rem;
  color: #e0e0e0;
  background: #333;
  border-radius: 50%;
  padding: 0px; 
}

/* Stats Styles */
.stat-item {
  background-color: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}

.stat-item:hover, .stat-item.active {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 700;
  font-family: 'Bebas Neue', sans-serif;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.85rem;
  color: #aaa;
}

/* Tab Navigation Styles */
.custom-tabs {
  background-color: #1a1a1a;
  border: 1px solid #333;
}

.custom-tabs .nav-link {
  color: #888;
  font-weight: 500;
  transition: all 0.3s ease;
}

.custom-tabs .nav-link:hover {
  color: #fff;
}

.custom-tabs .nav-link.active {
  background-color: #dc3545;
  color: white;
}

/* Movie Card Hover Effect */
.movie-card-wrapper {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.movie-card-wrapper:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
  z-index: 2;
}

.movie-overlay {
  background: rgba(0, 0, 0, 0.7);
  transition: opacity 0.3s ease;
}

.movie-card-wrapper:hover .movie-overlay {
  opacity: 1 !important;
}

/* Review Card Styles */
.review-card {
  transition: border-color 0.2s;
}
.review-card:hover {
  border-color: #555 !important;
}
.hover-underline:hover {
  text-decoration: underline;
  text-decoration-color: #dc3545;
  text-underline-offset: 4px;
}
.cursor-pointer {
  cursor: pointer;
}

/* Pagination Customization */
.page-link {
  box-shadow: none;
}
.page-item.active .page-link {
  background-color: #dc3545;
  border-color: #dc3545;
}

/* Animations */
.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>