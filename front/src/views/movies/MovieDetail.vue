<template>
  <div v-if="movie" class="movie-detail-container">
    <!-- Backdrop with overlay -->
    <div class="backdrop" :style="{ backgroundImage: `url(${movie.poster_path})` }">
      <div class="backdrop-overlay"></div>
    </div>

    <div class="content-wrapper container">
      <div class="row">
        <!-- Poster Column -->
        <div class="col-md-4 col-lg-3 mb-4 mb-md-0">
          <div class="poster-wrapper">
            <img :src="movie.poster_path" :alt="movie.title" class="img-fluid rounded shadow-lg poster-img">
          </div>
        </div>

        <!-- Info Column -->
        <div class="col-md-8 col-lg-9 text-white">
          <div class="d-flex align-items-center gap-3 mb-2">
             <h1 class="movie-title mb-0">{{ movie.title }}</h1>
             <button class="btn btn-link p-0 border-0 text-danger fs-2 heart-btn" @click="toggleLike">
                <i :class="movie.is_liked ? 'bi bi-heart-fill' : 'bi bi-heart'"></i>
             </button>
          </div>
          
          <div class="d-flex align-items-center gap-3 mb-4 text-light-gray">
            <span class="fs-5">{{ getYear(movie.release_date) }}</span>
            <span class="badge bg-danger">평점 {{ movie.vote_average.toFixed(1) }}</span>
          </div>

          <!-- Genres -->
          <div class="mb-4">
            <span v-for="genre in movie.genres" :key="genre.name" class="badge rounded-pill bg-secondary me-2 bg-opacity-50 border border-secondary">
              {{ genre.name }}
            </span>
          </div>

          <!-- Director & Overview -->
          <div class="mb-5">
             <div class="mb-3" v-if="movie.director">
                <h3 class="section-title d-inline-block me-3">감독</h3>
                <span class="fs-5 text-light-gray">{{ movie.director }}</span>
             </div>

            <h3 class="section-title">줄거리</h3>
            <p class="overview-text">{{ movie.overview }}</p>
          </div>

          <!-- Actors -->
          <div class="mb-4">
            <h3 class="section-title">출연진</h3>
            <div class="d-flex flex-wrap gap-2">
              <span v-for="actor in movie.actors.slice(0, 10)" :key="actor.name" class="text-light-gray actor-name">
                {{ actor.name }}<span v-if="movie.actors.length > 1">,</span>
              </span>
              <span v-if="movie.actors.length > 10" class="text-secondary">...</span>
            </div>
          </div>
          
          <!-- Buttons -->
          <div class="d-flex gap-3 mt-5">
            <button class="btn btn-danger btn-lg px-4 d-flex align-items-center gap-2" @click="playTrailer">
                <i class="bi bi-play-fill fs-4"></i> 재생
            </button>
             <button class="btn btn-outline-light btn-lg px-4" @click="$router.go(-1)">
                뒤로가기
            </button>
          </div>
        </div>
      </div>

      <!-- Trailer Modal -->
      <Teleport to="body">
        <div class="modal fade" id="trailerModal" tabindex="-1" aria-labelledby="trailerModalLabel" aria-hidden="true">
          <div class="modal-dialog modal-xl modal-dialog-centered">
            <div class="modal-content bg-dark text-white border-secondary shadow-lg">
              <div class="modal-header border-secondary">
                <h5 class="modal-title fw-bold" id="trailerModalLabel">{{ movie.title }} 예고편</h5>
                <button type="button" class="btn-close btn-close-white" @click="stopTrailer" aria-label="Close"></button>
              </div>
              <div class="modal-body p-0 bg-black">
                <div class="ratio ratio-16x9">
                  <iframe 
                    v-if="store.trailerId"
                    :src="`https://www.youtube.com/embed/${store.trailerId}?autoplay=1`" 
                    title="YouTube video player" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen
                    class="w-100 h-100"
                  ></iframe>
                  <div v-else class="d-flex flex-column justify-content-center align-items-center text-secondary w-100 h-100">
                    <div class="spinner-border text-danger mb-3" role="status">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                    <p>예고편 영상 정보를 불러오는 중입니다...</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- Reviews Section -->
      <div class="row mt-5">
        <div class="col-12 text-white">
          <h3 class="section-title mb-4">리뷰 및 평점 
            <span v-if="averageRating !== null" class="badge bg-info text-dark ms-2">
              ⭐ {{ averageRating.toFixed(1) }}
            </span>
          </h3>
          
          <!-- Reviews List (최신순 정렬) -->
          <div class="reviews-list mb-5">
            <div v-if="store.currentReviews && store.currentReviews.length > 0">
              <div v-for="review in paginatedReviews" :key="review.id" class="review-item mb-4 p-3 border rounded border-secondary">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="fw-bold review-author position-relative" style="cursor: pointer; z-index: 10;" @click.stop="$router.push({ name: 'mypage', params: { userId: review.user_id } })">
                    {{ review.user_name }}
                  </span>
                  <div class="d-flex align-items-center gap-2">
                     <span class="text-light-gray small">{{ new Date(review.created_at).toLocaleDateString() }}</span>
                     <span class="badge bg-warning text-dark">⭐ {{ review.rank }}</span>
                  </div>
                </div>
                <div class="d-flex justify-content-between align-items-start">
                    <p class="text-light-gray mb-0 flex-grow-1" style="white-space: pre-wrap;">{{ review.content }}</p>
                    <button 
                        v-if="authStore.userProfile && review.user_id == authStore.userProfile.id" 
                        @click="deleteReview(review.id)" 
                        class="btn btn-sm btn-outline-danger ms-3 flex-shrink-0"
                    >
                        삭제
                    </button>
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
              <p>아직 작성된 리뷰가 없습니다. 첫 번째 리뷰를 남겨주세요!</p>
            </div>
          </div>

          <!-- Review Form (Now Last) -->
          <div class="review-form p-4 rounded bg-dark bg-opacity-50 border border-secondary">
            <h5 class="mb-3">리뷰 작성</h5>
            <form @submit.prevent="submitReview">
              <div class="mb-3">
                <label class="form-label text-light-gray d-block">평점</label>
                <div class="star-rating d-inline-flex align-items-center gap-2">
                  <div class="stars position-relative" style="cursor: pointer;" @mousemove="handleMouseMove" @mouseleave="handleMouseLeave" @click="setRating">
                    <!-- Background Stars (Empty) -->
                    <div class="text-secondary fs-3">
                      <i class="bi bi-star"></i>
                      <i class="bi bi-star"></i>
                      <i class="bi bi-star"></i>
                      <i class="bi bi-star"></i>
                      <i class="bi bi-star"></i>
                    </div>
                    <!-- Foreground Stars (Filled) -->
                    <div class="text-warning fs-3 position-absolute top-0 start-0 overflow-hidden" :style="{ width: starWidth }">
                      <div style="width: max-content;">
                        <i class="bi bi-star-fill"></i>
                        <i class="bi bi-star-fill"></i>
                        <i class="bi bi-star-fill"></i>
                        <i class="bi bi-star-fill"></i>
                        <i class="bi bi-star-fill"></i>
                      </div>
                    </div>
                  </div>
                  <span class="fs-5 fw-bold ms-2">{{ displayRank }}점</span>
                </div>
              </div>
              <div class="mb-3">
                <label for="reviewContent" class="form-label text-light-gray">내용</label>
                <textarea v-model="reviewContent" id="reviewContent" class="form-control bg-secondary text-white border-secondary" rows="3" placeholder="영화에 대한 감상평을 남겨주세요." required></textarea>
              </div>
              <div class="d-flex justify-content-end">
                <button type="submit" class="btn btn-primary px-4">작성하기</button>
              </div>
            </form>
          </div>

        </div>
      </div>
    </div>
  </div>
  <div v-else class="d-flex justify-content-center align-items-center vh-100 text-white">
    <div class="spinner-border text-danger" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useMovieStore } from '@/stores/movies';
import { useAuthStore } from '@/stores/auth'; // Auth Store Import

const route = useRoute();
const store = useMovieStore();
const authStore = useAuthStore(); // Auth Store Instance

const reviewContent = ref('');
const reviewRank = ref(10); // Actual score (1-10)
const hoverRank = ref(null); // For hover effect
const currentPage = ref(1);
const itemsPerPage = 5;
const modalInstance = ref(null); // Bootstrap Modal Instance

const movie = computed(() => store.currentMovie);

onMounted(() => {
  store.getMovieDetail(route.params.id);
  store.getReviews(route.params.id);
  // 사용자 프로필 정보를 가져와서 삭제 버튼 권한 확인에 사용
  if (authStore.token) {
    authStore.getUserProfile();
  }
});

const getYear = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).getFullYear();
};

const paginatedReviews = computed(() => {
  if (!store.currentReviews) return [];
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return store.currentReviews.slice(start, end);
});

const totalPages = computed(() => {
  if (!store.currentReviews) return 0;
  return Math.ceil(store.currentReviews.length / itemsPerPage);
});

const averageRating = computed(() => {
  if (!store.currentReviews || store.currentReviews.length === 0) return null;
  const totalRank = store.currentReviews.reduce((sum, review) => sum + review.rank, 0);
  return totalRank / store.currentReviews.length;
});

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

// Star Rating Logic
const displayRank = computed(() => {
  return hoverRank.value !== null ? hoverRank.value : reviewRank.value;
});

const starWidth = computed(() => {
  const rank = displayRank.value;
  return `${(rank / 10) * 100}%`;
});

const handleMouseMove = (event) => {
  const rect = event.currentTarget.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const width = rect.width;
  const percent = x / width;
  
  // Calculate score from 1 to 10
  let score = Math.ceil(percent * 10);
  if (score < 1) score = 1;
  if (score > 10) score = 10;
  
  hoverRank.value = score;
};

const handleMouseLeave = () => {
  hoverRank.value = null;
};

const setRating = () => {
  if (hoverRank.value !== null) {
    reviewRank.value = hoverRank.value;
  }
};

const toggleLike = async () => {
  try {
    await store.likeMovie(route.params.id);
  } catch (error) {
    alert('로그인이 필요합니다.');
  }
};

const playTrailer = async () => {
  if (movie.value) {
    // 1. Fetch Trailer ID
    await store.getMovieTrailer(movie.value.tmdb_id, movie.value.title);
    
    // 2. Initialize and Show Modal using global Bootstrap
    const modalEl = document.getElementById('trailerModal');
    if (modalEl) {
        // Create new instance if not exists
        if (!modalInstance.value) {
            modalInstance.value = new window.bootstrap.Modal(modalEl);
            
            // Add listener to clear video when closed via backdrop/ESC
            modalEl.addEventListener('hidden.bs.modal', () => {
                store.trailerId = null;
            });
        }
        modalInstance.value.show();
    }
  }
};

const stopTrailer = () => {
    store.trailerId = null;
    if (modalInstance.value) {
        modalInstance.value.hide();
    }
};

const submitReview = async () => {
  if (!reviewContent.value.trim()) return;

  const payload = {
    content: reviewContent.value,
    rank: reviewRank.value
  };

  try {
    await store.createReview(route.params.id, payload);
    reviewContent.value = '';
    reviewRank.value = 10;
    currentPage.value = 1; // Reset to first page to see new review
  } catch (error) {
    alert('리뷰 작성에 실패했습니다. 로그인이 필요할 수 있습니다.');
  }
};

const deleteReview = async (reviewId) => {
  if (!confirm('정말 이 리뷰를 삭제하시겠습니까?')) return;
  
  try {
    await store.deleteReview(route.params.id, reviewId);
    // 현재 페이지가 비었으면 이전 페이지로 (리뷰가 삭제되어 페이지가 줄어들 수 있음)
    if (paginatedReviews.value.length === 0 && currentPage.value > 1) {
      currentPage.value--;
    }
  } catch (error) {
    alert('리뷰 삭제에 실패했습니다.');
  }
};
</script>

<style scoped>
.movie-detail-container {
  position: relative;
  min-height: 100vh;
  padding-top: 100px; /* Navbar height + spacing */
  overflow-x: hidden;
  background-color: #141414;
}

/* Backdrop for ambient background */
.backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  filter: blur(20px) brightness(0.4);
  z-index: 0;
  mask-image: linear-gradient(to bottom, black 0%, transparent 100%); /* Fade out at bottom */
}

.backdrop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, #141414 10%, rgba(20, 20, 20, 0.6) 50%, #141414 90%),
              linear-gradient(to bottom, rgba(20, 20, 20, 0.4) 0%, #141414 100%);
}

.content-wrapper {
  position: relative;
  z-index: 1;
}

.poster-wrapper {
  transition: transform 0.3s ease;
}

.poster-img {
  border-radius: 8px;
}

.movie-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 4rem;
  letter-spacing: 2px;
  line-height: 1;
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
  color: #e5e5e5;
}

.overview-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #d1d1d1;
  max-width: 800px;
}

.text-light-gray {
  color: #b3b3b3;
}

.actor-name {
    font-size: 1rem;
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

.review-author {
    cursor: pointer;
    transition: color 0.2s ease;
}

.review-author:hover {
    color: #dc3545; /* 강조색으로 변경 */
    text-decoration: underline;
}
</style>
