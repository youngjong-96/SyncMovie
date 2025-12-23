<template>
  <div class="d-flex align-items-center justify-content-center" style="min-height: 80vh;">
    <div class="form-container w-100">
      <h1 class="mb-4 text-white fw-bold">로그인</h1>
      <form @submit.prevent="performLogIn" class="d-flex flex-column gap-3 bg-transparent p-0 m-0 border-0" style="max-width: 100%;">
        <div>
          <div class="form-floating text-dark">
            <input type="text" class="form-control" id="username" placeholder="아이디" v-model.trim="username" :class="{ 'is-invalid': errors.username }">
            <label for="username">아이디</label>
          </div>
          <div v-if="errors.username" class="text-danger small mt-1 text-start">{{ errors.username.join(', ') }}</div>
        </div>

        <div>
          <div class="form-floating text-dark">
            <input type="password" class="form-control" id="password" placeholder="비밀번호" v-model.trim="password" :class="{ 'is-invalid': errors.password }">
            <label for="password">비밀번호</label>
          </div>
          <div v-if="errors.password" class="text-danger small mt-1 text-start">{{ errors.password.join(', ') }}</div>
        </div>
        
        <div v-if="errors.non_field_errors" class="text-danger small text-center fw-bold">{{ errors.non_field_errors.join(', ') }}</div>

        <button type="submit" class="btn btn-primary w-100 py-2 mt-3 fw-bold fs-5">로그인</button>
        
        <!-- <div class="d-flex justify-content-between mt-2">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" id="rememberMe">
            <label class="form-check-label text-secondary" for="rememberMe" style="font-size: 0.8rem;">
              로그인 정보 저장
            </label>
          </div>
          <a href="#" class="text-secondary text-decoration-none" style="font-size: 0.8rem;">도움이 필요하신가요?</a>
        </div> -->

        <div class="mt-4 text-secondary">
          <router-link :to="{name: 'passwordReset'}" class="text-white text-decoration-none d-block mb-2">비밀번호 찾기/변경</router-link>
          SyncMovie 회원이 아니신가요? <br></br>
          <router-link :to="{name: 'signup'}" class="text-white ms-1 text-decoration-none">지금 가입하세요.</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')
const errors = ref({})
const store = useAuthStore()

const performLogIn = async () => {
  errors.value = {}
  const payload = {
    username: username.value,
    password: password.value,
  }
  try {
    await store.logIn(payload)
  } catch (err) {
    if (err.response && err.response.data) {
      errors.value = err.response.data
    }
  }
}
</script>

<style scoped>
.form-floating > .form-control:focus ~ label,
.form-floating > .form-control:not(:placeholder-shown) ~ label {
  color: #8c8c8c;
  transform: scale(.85) translateY(-0.5rem) translateX(0.15rem);
}
.form-floating > label {
  color: #8c8c8c;
}
</style>
