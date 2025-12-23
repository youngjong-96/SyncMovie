<template>
    <div class="home-container">
        <!-- 메인 1개 -->
        <div class="hero-section d-flex align-items-center" :style="heroStyle">
            <div class="hero-overlay"></div>
            <div class="container position-relative z-1">
                <div class="row">
                    <div class="col-md-6" v-if="heroMovie">
                        <Transition name="fade-text" mode="out-in">
                            <div :key="heroMovie.id">
                                <h1 class="display-3 fw-bold hero-title mb-3">{{ heroMovie.title }}</h1>
                                <p class="lead hero-description mb-4 text-truncate-multiline">
                                    {{ heroMovie.overview || '이 영화에 대한 줄거리가 아직 준비되지 않았습니다.' }}
                                </p>
                                <div class="d-flex gap-3">
                                    <button class="btn btn-light btn-lg px-4 d-flex align-items-center gap-2" @click="playTrailer">
                                        <i class="bi bi-play-fill fs-4"></i> 재생
                                    </button>
                                    <button @click="goDetail(heroMovie.id)" class="btn btn-secondary btn-lg px-4 d-flex align-items-center gap-2 bg-opacity-75 border-0">
                                        <i class="bi bi-info-circle fs-5"></i> 상세 정보
                                    </button>
                                </div>
                            </div>
                        </Transition>
                    </div>
                </div>
            </div>
        </div>

        <!-- Movie Rows -->
        <div class="container-fluid content-rows pb-5">
            <!-- 지금 뜨는 콘텐츠 -->
            <section class="movie-section">
                <h3 class="mb-3 ps-4 row-title">지금 뜨는 콘텐츠</h3>
                
                <div class="movie-row-container ps-4 pe-4">
                    <div class="d-flex gap-3 overflow-auto movie-row pb-4 movie-row">
                        <!-- Movie Cards -->
                        <div v-for="movie in store.movies" :key="movie.id" class="movie-card flex-shrink-0" @click="goDetail(movie.id)">
                            <div class="card bg-dark text-white border-0">
                                <img :src="movie.poster_path || 'https://via.placeholder.com/300x450?text=No+Poster'" class="card-img-top rounded" :alt="movie.title">
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Genre Movie Rows -->
            <section v-for="genre in genres" :key="genre" class="movie-section mt-5">
                <h3 class="mb-3 row-title">{{ genre }} 영화</h3>
                <div class="movie-row-container">
                    <div class="d-flex gap-3 overflow-auto movie-row pb-4">
                        <template v-if="store.genreMovies && store.genreMovies[genre]">
                            <div v-for="movie in store.genreMovies[genre]" :key="movie.id" class="movie-card flex-shrink-0" @click="goDetail(movie.id)">
                                <div class="card bg-dark text-white border-0">
                                    <img :src="movie.poster_path || 'https://via.placeholder.com/300x450?text=No+Poster'" class="card-img-top rounded" :alt="movie.title">
                                </div>
                            </div>
                        </template>
                        <div v-else class="text-white">로딩 중...</div>
                    </div>
                </div>
            </section>
        </div>

        <!-- Trailer Modal -->
        <Teleport to="body">
            <div class="modal fade" id="mainTrailerModal" tabindex="-1" aria-labelledby="mainTrailerModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-xl modal-dialog-centered">
                    <div class="modal-content bg-dark text-white border-secondary shadow-lg">
                        <div class="modal-header border-secondary">
                            <h5 class="modal-title fw-bold" id="mainTrailerModalLabel">{{ heroMovie ? heroMovie.title : '' }} 예고편</h5>
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
    </div>
</template>

<script setup>
import { onMounted, computed, ref, onUnmounted } from 'vue';
import { useMovieStore } from '@/stores/movies';
import { useRouter } from 'vue-router';

const store = useMovieStore();
const router = useRouter();

const genres = ['액션', '코미디', '드라마', '로맨스', '공포', '스릴러', '애니메이션'];
const modalInstance = ref(null);
const currentHeroIndex = ref(0)
let heroTimer = null

// heroMovie(메인으로 나오는 영화)를 인덱스에 따라 반응형으로 계산
const heroMovie = computed(() => {
    const limit = 10
    return store.movies.length > 0 ? store.movies[currentHeroIndex.value % limit] : null;
});

// 타이머 설정 함수(heroMovie 시간마다 넘어가도록)
const startHeroRotation = () => {
    heroTimer = setInterval(() => {
        const limit = Math.min(store.movies.length, 10);
        if (limit > 0) {
            currentHeroIndex.value = (currentHeroIndex.value + 1) % limit;
        }
    }, 5000); // 5초
};

onMounted(async () => {
    // 메인 영화 목록이 없으면 호출
    if (store.movies.length === 0) {
        await store.getMovies();
    }

    // 장르별 영화 목록이 없으면 호출
    for (const genre of genres) {
        if (!store.genreMovies[genre] || store.genreMovies[genre].length === 0) {
            store.getMoviesByGenre(genre);
        }
    }
    
    // 영화 데이터를 가져온 후 로테이션 시작
    startHeroRotation();
});

// 컴포넌트 제거 시 타이머 해제 (메모리 누수 방지)
onUnmounted(() => {
    if (heroTimer) clearInterval(heroTimer);
});

const heroStyle = computed(() => {
    const image = heroMovie.value?.poster_path || 'https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=2094&auto=format&fit=crop';
    return {
        backgroundImage: `url('${image}')`
    };
});

const goDetail = (id) => {
    router.push({ name: 'movieDetail', params: { id } });
};

const playTrailer = async () => {
    if (heroMovie.value) {
        await store.getMovieTrailer(heroMovie.value.tmdb_id, heroMovie.value.title);
        
        const modalEl = document.getElementById('mainTrailerModal');
        if (modalEl) {
            if (!modalInstance.value) {
                modalInstance.value = new window.bootstrap.Modal(modalEl);
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
</script>

<style scoped>
.home-container {
    background-color: #141414;
    min-height: 100vh;
}

/* Hero Section Styles */
.hero-section {
    height: 85vh;
    background-size: cover;
    background-position: center top;
    position: relative;
    margin-bottom: -100px;
    transition: background-image 1s ease-in-out;
    mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 80%, rgba(0,0,0,0) 100%);
    -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 80%, rgba(0,0,0,0) 100%);
}

.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to right, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 60%),
                linear-gradient(to top, #141414 0%, transparent 20%);
}

.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 2px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
}

.hero-description {
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    max-width: 600px;
    font-size: 1.2rem;
}

.text-truncate-multiline {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Row Styles */
.content-rows {
    position: relative;
    z-index: 2;
}

.row-title {
    font-weight: 600;
    font-size: 1.5rem;
    color: #e5e5e5;
    transition: color 0.3s;
}

.row-title:hover {
    color: #fff;
}

.movie-row {
    scrollbar-width: thin; /* Firefox */
    scrollbar-color: #555 #141414; /* Firefox */
    padding-bottom: 10px; /* Add padding to prevent scrollbar from overlapping content */
}

/* Custom Scrollbar for Webkit (Chrome, Safari, Edge) */
.movie-row::-webkit-scrollbar {
    height: 8px; /* Height of the horizontal scrollbar */
}

.movie-row::-webkit-scrollbar-track {
    background: #141414; /* Background of the scrollbar track */
    border-radius: 4px;
}

.movie-row::-webkit-scrollbar-thumb {
    background-color: #555; /* Color of the scrollbar thumb */
    border-radius: 4px;
    border: 2px solid #141414; /* Creates padding around thumb */
}

.movie-row::-webkit-scrollbar-thumb:hover {
    background-color: #888; /* Color on hover */
}

.movie-card {
    width: 200px;
    transition: transform 0.3s ease, z-index 0.3s;
    cursor: pointer;
}

.movie-card:hover {
    transform: scale(1.05);
    z-index: 10;
}

.movie-card img {
    height: 300px;
    object-fit: cover;
}

.card-title {
    font-size: 0.9rem;
    color: #b3b3b3;
}

.movie-section {
    width: 100%;
    padding: 0 4%; /* 기본 좌우 여백 */
}

/* 초고해상도 (2230px 이상) 스타일 적용 */
@media (min-width: 2330px) {
    .movie-section {
        /* 콘텐츠 영역의 최대 너비를 제한하여 중앙으로 모음 */
        max-width: 2100px; 
        margin-left: auto;
        margin-right: auto;
        padding: 0;
    }

    .movie-row {
        /* 화면이 너무 넓어 여백이 남는 경우 아이템들을 중앙 정렬 */
        
    }

    /* 만약 아이템이 너무 많아 중앙 정렬 시 왼쪽이 잘린다면 
       justify-content: center 대신 부모의 width 조절 방식을 유지하세요. */
}


/* 텍스트 페이드 전환 효과 */
.fade-text-enter-active,
.fade-text-leave-active {
    transition: all 0.5s ease;
}

.fade-text-enter-from {
    opacity: 0;
    transform: translateY(20px); /* 아래에서 위로 올라오며 등장 */
}

.fade-text-leave-to {
    opacity: 0;
    transform: translateY(-10px); /* 위로 살짝 올라가며 퇴장 */
}
</style>

