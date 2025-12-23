<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top bg-black bg-opacity-75">
      <div class="container-fluid">
        <router-link class="navbar-brand brand-logo" :to="{ name: 'home' }">
          SyncMovie
        </router-link>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navbarNav" aria-controls="navbarNav"
                aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <!-- 왼쪽 메뉴 -->
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link class="nav-link active" aria-current="page" :to="{ name: 'home' }">
                홈
              </router-link>
            </li>
            <li class="nav-item">
                <a
                  class="nav-link"
                  href="#"
                  @click.prevent="handleRecommendClick"
                >
                  추천
                </a>
              <!-- <router-link class="nav-link" :to="{ name: 'recommend' }">
                추천
              </router-link> -->
            </li>
          </ul>

          <!-- 🔥 오른쪽: 검색창 + 프로필 묶기 -->
          <div class="right-box ms-lg-auto">
            <!-- 검색창 -->
            <form class="d-flex align-items-center me-3" @submit.prevent="goSearch">
              <input
                v-model="keyword"
                class="form-control form-control-sm bg-dark text-white border-0 py-0 search-input"
                type="search"
                placeholder="제목으로 영화 검색하기"
                style="height: 28px; font-size: 0.8rem; width: 180px;"
              >
              <button
                class="btn btn-outline-light btn-sm ms-2 py-0 px-2"
                type="submit"
                style="height: 28px;"
              >
                <i class="bi bi-search"></i>
              </button>
            </form>

            <!-- 프로필 / 로그인 영역 -->
            <ul class="navbar-nav mb-0">
              <li class="nav-item" v-if="!store.isLoggedIn">
                <div class="d-flex gap-2">
                  <router-link :to="{ name: 'login' }" class="btn btn-danger btn-sm">
                    로그인
                  </router-link>
                  <router-link :to="{ name: 'signup' }" class="btn btn-outline-light btn-sm">
                    회원가입
                  </router-link>
                </div>
              </li>
              <li class="nav-item dropdown" v-else>
                <a class="nav-link dropdown-toggle" href="#" role="button"
                   data-bs-toggle="dropdown" aria-expanded="false">
                  <i class="bi bi-person-circle fs-5"></i>
                </a>
                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                  <li>
                    <router-link :to="{ name: 'mypage' }" class="dropdown-item">
                      마이페이지
                    </router-link>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="performLogOut">
                      로그아웃
                    </a>
                  </li>
                  <li>
                    <a class="dropdown-item text-danger" href="#"
                       @click.prevent="performDeleteAccount">
                      회원탈퇴
                    </a>
                  </li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>
    <!-- 추천 타입 선택 모달 -->
    <div
      class="modal fade"
      id="recommendTypeModal"
      tabindex="-1"
      aria-labelledby="recommendTypeModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content bg-dark text-white">
          <div class="modal-header border-0">
            <h5 class="modal-title" id="recommendTypeModalLabel">
              추천 방식을 선택하세요
            </h5>
            <button
              type="button"
              class="btn-close btn-close-white"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>

          <div class="modal-body text-center">
            <button
              class="btn btn-primary me-2 mb-2"
              @click="goRecommend('overview')"
              data-bs-dismiss="modal"
            >
              줄거리 기반 추천
            </button>
            <button
              class="btn btn-secondary mb-2"
              @click="goRecommend('actors')"
              data-bs-dismiss="modal"
            >
              인물 기반 추천
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="main-content">
      <router-view />
      <!-- <router-view :key="$route.fullPath" /> -->
    </div>
  </div>
</template>


<script setup>
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { ref } from 'vue'

const store = useAuthStore()
const router = useRouter()

// 🔍 검색어 상태
const keyword = ref('')

// 🔍 검색 실행 함수
const goSearch = () => {
  const q = keyword.value.trim()
  if (!q) return
  router.push({ name: 'search', query: { q } })

  keyword.value = ''
}

const performLogOut = async () => {
  await store.logOut()
}

const performDeleteAccount = async () => {
  if (confirm('정말 탈퇴하시겠습니까?')) {
    await store.deleteAccount()
  }
}

const goRecommend = (type) => {
  router.push(`/recommend/${type}`)      // overview / actors
}

const handleRecommendClick = () => {
  if (!store.isLoggedIn) {
    alert('회원가입 혹은 로그인 후 서비스를 이용할 수 있습니다.')
    router.push({ name: 'signup' })  // 또는 login
    return
  }

  // 로그인 상태일 때만 모달 수동으로 열기
  const modalEl = document.getElementById('recommendTypeModal')
  if (modalEl) {
    const modal = new bootstrap.Modal(modalEl)
    modal.show()
  }
  // const modalEl = document.getElementById('recommendTypeModal')
  // if (modalEl) {
  //   const modal = new bootstrap.Modal(modalEl)
  //   modal.show()

  //   // 모달이 열릴 때 내부 버튼에 포커스 이동
  //   const handleShown = () => {
  //     const firstButton = modalEl.querySelector('button')
  //     if (firstButton) {
  //       firstButton.focus()
  //     }
  //     modalEl.removeEventListener('shown.bs.modal', handleShown)
  //   }
  //   modalEl.addEventListener('shown.bs.modal', handleShown)

  //   // 모달이 닫힐 때 포커스를 외부로 이동
  //   const handleHidden = () => {
  //     document.body.focus()
  //     modalEl.removeEventListener('hidden.bs.modal', handleHidden)
  //   }
  //   modalEl.addEventListener('hidden.bs.modal', handleHidden)
  // }
}

</script>

<style scoped>
.brand-logo {
  font-family: 'Bebas Neue', sans-serif;
  color: #E50914 !important;
  font-size: 2rem;
  letter-spacing: 2px;
}

.main-content {
  padding-top: 80px; /* Adjust based on navbar height */
  min-height: 100vh;
}

.navbar {
  transition: background-color 0.3s ease-in-out;
}

.nav-link {
  font-size: 0.9rem;
  font-weight: 500;
  color: #e5e5e5 !important;
  transition: color 0.3s;
}

.nav-link:hover {
  color: #b3b3b3 !important;
}

/* Override Bootstrap button styles for Netflix look */
.btn-danger {
  background-color: #E50914;
  border: none;
}

.btn-danger:hover {
  background-color: #c11119;
}

.search-input::placeholder {
  color: #aaa !important;
  opacity: 1;
}

.search-input:focus::placeholder {
  color: transparent !important;
}

/* 기본: 모바일(드롭 상태)에서는 위아래(column) */
.right-box {
  display: flex;
  flex-direction: column;
  align-items: flex-start;   /* 왼쪽 정렬; 필요하면 center로 변경 */
  gap: 6px;
}

/* 검색창 내부는 항상 가로 정렬 */
.search-box {
  display: flex;
  align-items: center;
}

/* 넓은 화면(lg 이상)에서는 옆으로(row) */
@media (min-width: 992px) {
  .right-box {
    flex-direction: row;      /* 🔥 가로 배치 */
    align-items: center;
    gap: 16px;
  }
}
</style>
