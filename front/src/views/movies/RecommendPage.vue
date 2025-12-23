<template>
  <div class="recommend-container">
    <h1>영화 추천</h1>
    
    <!-- 영화 선택 및 추천 요청 -->
      <div v-if="selectedType && !showRecommendations" class="movie-selection">
      <h2 v-if="selectedType === 'overview'">
        취향을 알려주세요. 영화를 선택하세요:
      </h2>
      <h2 v-else>
        좋아하는 배우가 나온 영화를 선택하세요:
      </h2>

      <div class="d-flex align-items-center gap-2">
        <button
          @click="refreshMovies"
          class="btn btn-outline-primary mb-3"
          :disabled="isLoadingRecommendations"
        >
          새로고침
        </button>

        <div v-if="selectedMovies.length > 0" class="mb-3">
          <button
            @click="getRecommendations"
            class="btn btn-success"
            :disabled="isLoadingRecommendations"
          >
            <!-- 로딩 중일 때 텍스트 변경 -->
            {{ isLoadingRecommendations
                ? '추천 중...'
                : (selectedType === 'overview' ? '줄거리 기반' : '인물 기반') + ' 추천 받기'
            }}
          </button>
        </div>
      </div>

      <div class="movie-grid">
        <div 
          v-for="movie in currentMovies" 
          :key="movie.id" 
          class="movie-card"
          @click="toggleSelectMovie(movie)"
          :class="{ selected: selectedMovies.some(m => m.id === movie.id) }"
        >
          <img :src="movie.poster_path" :alt="movie.title" />
          <!-- <span v-if="movie.vote_average !== null" class="badge text-white ms-2 mt-2 fs-6">
              평점: ⭐ {{ movie.vote_average.toFixed(1) }}
          </span> -->
        </div>
      </div>
    </div>

    <!-- 추천 결과 -->
    <div v-if="showRecommendations" class="recommendations">
      <h2>추천 영화</h2>
      <button @click="backToSelection" class="btn btn-outline-secondary mb-3">다시 선택하기</button>
      <div class="movie-grid">
        <div v-for="movie in recommendations" :key="movie.id" class="movie-card" @click="goToDetail(movie.id)">
          <img :src="movie.poster_path" :alt="movie.title" />
          <span v-if="movie.vote_average !== null" class="badge text-white ms-2 mt-2 fs-6">
              평점: ⭐ {{ movie.vote_average.toFixed(1) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 🔹 로딩 오버레이 -->
    <div v-if="isLoadingRecommendations" class="loading-overlay">
      <div class="loading-modal">
        <div class="loading-title">추천 중...</div>
        <div class="loading-bar">
          <div class="loading-bar-inner"></div>
        </div>
        <p class="loading-desc">당신의 취향에 맞는 영화를 찾고 있어요.</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useRecommendStore } from '@/stores/recommend'
import { mapState, mapActions } from 'pinia'
import { watch } from 'vue' 

export default {
  name: 'RecommendPage',
  data() {
    return {
      currentMovies: [], // 화면에 렌더링될 영화 리스트
      isLoadingRecommendations: false,
    }
  },
  computed: {
    // Pinia 상태 구독
    ...mapState(useRecommendStore, [
      'selectedType', 
      'selectedMovies', 
      'recommendations', 
      'showRecommendations', 
      'seenUnselectedMovies'
    ])
  },
  methods: {
    ...mapActions(useRecommendStore, ['initType', 'resetAll']),

    // // 1. 타입 선택 버튼 클릭 시 (줄거리/인물)
    // async selectType(type) {
    //   this.initType(type); // 스토어 초기화
    //   this.$router.push(`/recommend/${type}`);
    //   await this.shuffleMovies(); // 즉시 영화 목록 로드
    // },

    // 🔹 모달에서 호출할 타입 변경 함수
    async changeRecommendType(type) {
      const store = useRecommendStore()

      // 1) URL 이동
      this.$router.push(`/recommend/${type}`)

      // 2) 스토어/화면 초기화
      this.initType(type)
      this.currentMovies = []
      this.isLoadingRecommendations = false
      store.showRecommendations = false
      store.recommendations = []

      // 3) 새 영화 로딩
      await this.shuffleMovies()
    },

    // 2. 영화 카드 클릭 시 선택 토글
    toggleSelectMovie(movie) {
      const store = useRecommendStore();
      const index = store.selectedMovies.findIndex(m => m.id === movie.id);
      if (index > -1) {
        store.selectedMovies.splice(index, 1);
      } else {
        store.selectedMovies.push(movie);
      }
      // 선택된 영화는 목록 맨 앞으로 유지하기 위해 리스트 재배열
      this.updateCurrentMoviesDisplay();
    },

    // 3. API로부터 랜덤 영화 가져오기
    async shuffleMovies() {
      const numUnselected = Math.max(10 - this.selectedMovies.length, 0);
      const excludeIds = this.selectedMovies.map(m => m.id).join(',');
      
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/v1/movies/random/?num=${numUnselected}&exclude=${excludeIds}`);
        this.currentMovies = [...this.selectedMovies, ...response.data];
        
        // Pinia에 거쳐간 영화 저장
        const store = useRecommendStore();
        store.seenUnselectedMovies.push(...response.data);
      } catch (error) {
        console.error('영화 로드 실패:', error);
      }
    },

    // 4. 새로고침 버튼 클릭 시
    async refreshMovies() {
      const numUnselected = Math.max(10 - this.selectedMovies.length, 0);
      // 현재 선택된 것 + 이미 본 것 제외
      const excludeIds = [...this.selectedMovies.map(m => m.id), ...this.seenUnselectedMovies.map(m => m.id)].join(',');
      
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/v1/movies/random/?num=${numUnselected}&exclude=${excludeIds}`);
        let newUnselected = response.data;
        
        // 후보 부족 시 본 영화 목록 초기화 후 재시도
        if (newUnselected.length < numUnselected) {
          const store = useRecommendStore();
          store.seenUnselectedMovies = [];
          const retryRes = await axios.get(`http://127.0.0.1:8000/api/v1/movies/random/?num=${numUnselected}&exclude=${this.selectedMovies.map(m=>m.id).join(',')}`);
          newUnselected = retryRes.data;
        }

        this.currentMovies = [...this.selectedMovies, ...newUnselected];
        useRecommendStore().seenUnselectedMovies.push(...newUnselected);
      } catch (error) {
        console.error('새로고침 실패:', error);
      }
    },

    // 5. 추천 받기 버튼 클릭 시
    async getRecommendations() {
      if (this.selectedMovies.length === 0) return;
      this.isLoadingRecommendations = true;

      try {
        const response = await axios.post('http://127.0.0.1:8000/api/v1/recommend/', {
          movie_ids: this.selectedMovies.map(m => m.id),
          type: this.selectedType
        });
        
        const store = useRecommendStore();
        store.recommendations = response.data;
        store.showRecommendations = true;
        
        this.$router.push(`/recommend/${this.selectedType}/results`);
      } catch (error) {
        console.error('추천 실패:', error);
      } finally {
        this.isLoadingRecommendations = false;
      }
    },

    // 6. 다시 선택하기 버튼
    backToSelection() {
      const store = useRecommendStore()
      const type = this.selectedType || this.$route.params.type || 'overview'

      // 스토어/화면 상태 초기화
      this.resetAll()
      this.currentMovies = []
      this.isLoadingRecommendations = false
      store.showRecommendations = false
      store.recommendations = []

      // 바로 이전 타입 페이지로 이동
      this.$router.push(`/recommend/${type}`)
    },


    // 7. 영화 선택 상태에 따른 화면 리스트 업데이트
    updateCurrentMoviesDisplay() {
      const unselected = this.currentMovies.filter(m => !this.selectedMovies.some(sm => sm.id === m.id));
      this.currentMovies = [...this.selectedMovies, ...unselected];
    },

    goToDetail(movieId) {
      this.$router.push(`/movies/${movieId}`);
    }
  },

  async mounted() {
  const store = useRecommendStore()

    if (this.$route.path.includes('/results')) {
      return
    }

    if (this.$route.params.type) {
      // 타입만 맞는다고 끝이 아니라, currentMovies 가 비어있으면 로딩
      if (this.selectedType !== this.$route.params.type) {
        this.initType(this.$route.params.type)
        store.showRecommendations = false
        store.recommendations = []
        this.currentMovies = []
      }
      this.isLoadingRecommendations = false

      // 🔥 currentMovies 가 없으면 반드시 영화 로드
      if (!this.currentMovies.length) {
        await this.shuffleMovies()
      }
    } else {
      this.resetAll()
    }
  },

  async beforeRouteUpdate(to, from, next) {
    // results 페이지면 추천 결과 유지
    if (to.path.includes('/results')) {
      next()
      return
    }

    // results가 아니면 초기화 + 로딩
    this.initType(to.params.type)
    this.currentMovies = []
    this.isLoadingRecommendations = false
    const store = useRecommendStore()
    store.showRecommendations = false
    store.recommendations = []
    await this.shuffleMovies()
    next()
  }

}

</script>

<style scoped>
.recommend-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.recommend-type {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.movie-selection, .recommendations {
  margin-top: 20px;
}

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

/* 화면 전체를 덮는 반투명 + 블러 배경 */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

/* 중앙 로딩 박스 */
.loading-modal {
  background: #111;
  padding: 24px 32px;
  border-radius: 16px;
  border: 2px solid #fff;
  text-align: center;
  min-width: 260px;
  color: #fff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
}

.loading-title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 4px;
  margin-bottom: 12px;
}

/* 진행 바 */
.loading-bar {
  position: relative;
  width: 260px;
  height: 18px;
  margin: 0 auto;
  border-radius: 999px;
  border: 3px solid #ffffff;
  overflow: hidden;
  background-color: transparent;
}

.loading-bar-inner {
  position: absolute;
  left: -40%;
  top: 0;
  width: 40%;
  height: 100%;
  background-color: #28a745;  /* success 색 */
  border-radius: 999px;
  animation: loading-slide 1.1s linear infinite;
}

.loading-desc {
  margin-top: 10px;
  font-size: 13px;
  opacity: 0.8;
}

@keyframes loading-slide {
  0%   { left: -40%; }
  100% { left: 100%; }
}

</style>
