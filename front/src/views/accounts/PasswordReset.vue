<template>
  <div class="d-flex align-items-center justify-content-center" style="min-height: 80vh;">
    <div class="form-container w-100">
      <h1 class="mb-4 text-white fw-bold">비밀번호 변경</h1>
      <form @submit.prevent="handleSubmit" class="d-flex flex-column gap-3 bg-transparent p-0 m-0 border-0" style="max-width: 100%;">
        <div>
          <div class="form-floating text-dark">
            <input type="text" class="form-control" id="username" placeholder="아이디" v-model.trim="username" :disabled="isVerified" :class="{ 'is-invalid': errorMsg }">
            <label for="username">아이디</label>
          </div>
          <div v-if="errorMsg" class="text-danger small mt-1 text-start">{{ errorMsg }}</div>
        </div>

        <div v-if="isVerified">
          <div class="form-floating text-dark mb-3">
            <input type="password" class="form-control" id="newPassword" placeholder="새 비밀번호" v-model.trim="newPassword" :class="{ 'is-invalid': errors.password }">
            <label for="newPassword">새 비밀번호</label>
          </div>
          <div v-if="errors.password" class="text-danger small mt-1 text-start">{{ errors.password.join(', ') }}</div>
          
          <div class="form-floating text-dark">
            <input type="password" class="form-control" id="newPasswordConfirm" placeholder="새 비밀번호 확인" v-model.trim="newPasswordConfirm" :class="{ 'is-invalid': errors.password }">
            <label for="newPasswordConfirm">새 비밀번호 확인</label>
          </div>
        </div>

        <button type="submit" class="btn btn-primary w-100 py-2 mt-3 fw-bold fs-5">
          {{ isVerified ? '비밀번호 변경' : '아이디 확인' }}
        </button>
        
        <div class="mt-4 text-secondary">
          <router-link :to="{name: 'login'}" class="text-white ms-1 text-decoration-none">로그인 페이지로 돌아가기</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const username = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')
const isVerified = ref(false)
const errorMsg = ref('')
const errors = ref({})
const store = useAuthStore()
const router = useRouter()

const handleSubmit = async () => {
  errors.value = {}
  
  if (!isVerified.value) {
    // ID 확인 단계
    if (!username.value) {
      errorMsg.value = '아이디를 입력해주세요.'
      return
    }
    const exists = await store.checkUsername(username.value)
    if (exists) {
      isVerified.value = true
      errorMsg.value = ''
    } else {
      errorMsg.value = '해당 ID는 존재하지 않습니다.'
    }
  } else {
    // 비밀번호 변경 단계
    if (newPassword.value !== newPasswordConfirm.value) {
      alert('비밀번호가 일치하지 않습니다.')
      return
    }
    
    const payload = {
      username: username.value,
      password: newPassword.value,
      password2: newPasswordConfirm.value,
    }
    
    try {
      await store.resetPassword(payload)
      alert('비밀번호가 성공적으로 변경되었습니다.')
      router.push({ name: 'login' })
    } catch (err) {
      if (err.response && err.response.data) {
        errors.value = err.response.data
      }
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
