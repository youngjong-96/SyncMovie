<template>
  <div class="home-container">
    <div class="content-overlay">
      <h1 class="title">SyncMovie</h1>
      <p class="subtitle">모든 영화를 한눈에, 당신만의 취향을 찾아보세요</p>
      
      <div class="cta-buttons">
        <RouterLink :to="{ name: 'login' }" class="btn btn-primary">로그인</RouterLink>
        <RouterLink :to="{ name: 'signup' }" class="btn btn-secondary">회원가입</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.home-container {
  height: 100vh;
  width: 100%;
  background-image: url('@/assets/mainpage.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

/* 어두운 오버레이 추가 */
.home-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1;
}

.content-overlay {
  position: relative;
  z-index: 2;
  text-align: center;
  color: white;
  padding: 2rem;
  max-width: 800px;
}

.title {
  font-size: 4rem;
  font-weight: 800;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  font-family: 'Arial', sans-serif; /* 필요시 폰트 변경 */
}

.subtitle {
  font-size: 1.5rem;
  margin-bottom: 3rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.cta-buttons {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
}

.btn {
  padding: 0.8rem 2.5rem;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #e50914; /* 넷플릭스 레드 스타일 */
  color: white;
  border: 2px solid #e50914;
}

.btn-primary:hover {
  background-color: #f40612;
  transform: scale(1.05);
}

.btn-secondary {
  background-color: rgba(109, 109, 110, 0.7);
  color: white;
  border: 2px solid rgba(109, 109, 110, 0.7);
}

.btn-secondary:hover {
  background-color: rgba(109, 109, 110, 0.4);
  border-color: white;
  transform: scale(1.05);
}
</style>
