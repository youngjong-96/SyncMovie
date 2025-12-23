<template>
  <div class="d-flex align-items-center justify-content-center" style="min-height: 80vh;">
    <div class="form-container" style="max-width: 600px; width: 100%;">
      <div class="d-flex align-items-baseline mb-4">
        <h1 class="text-white fw-bold mb-0">회원가입</h1>
        <small class="text-secondary ms-2">*는 필수항목</small>
      </div>
      <form @submit.prevent="performSignUp" class="d-flex flex-column gap-3 bg-transparent p-0 m-0 border-0" style="max-width: 100%;">
        <!-- 아이디 -->
        <div>
          <div class="d-flex gap-2">
            <div class="form-floating text-dark flex-grow-1">
              <input 
                type="text" 
                class="form-control" 
                id="username" 
                placeholder="아이디" 
                v-model.trim="username" 
                :class="{ 'is-invalid': errors.username || (isUsernameChecked && !isUsernameAvailable) }"
              >
              <label for="username">아이디 <span class="text-danger">*</span></label>
            </div>
            <button 
              type="button" 
              class="btn btn-primary flex-shrink-0 px-3 fw-bold" 
              @click="checkUsernameDuplication"
              style="min-width: 100px;"
            >
              중복 확인
            </button>
          </div>
          <div v-if="usernameFeedback" :class="isUsernameAvailable ? 'text-success' : 'text-danger'" class="small mt-1 text-start fw-bold">
            {{ usernameFeedback }}
          </div>
          <div v-if="errors.username" class="text-danger small mt-1 text-start">{{ errors.username.join(', ') }}</div>
        </div>

        <!-- 닉네임 -->
        <div>
          <div class="d-flex gap-2">
            <div class="form-floating text-dark flex-grow-1">
              <input 
                type="text" 
                class="form-control" 
                id="nickname" 
                placeholder="닉네임" 
                v-model.trim="nickname" 
                :class="{ 'is-invalid': errors.nickname || (isNicknameChecked && !isNicknameAvailable) }"
              >
              <label for="nickname">닉네임 <span class="text-danger">*</span></label>
            </div>
            
            <button 
              type="button" 
              class="btn btn-primary flex-shrink-0 px-3 fw-bold" 
              @click="checkNicknameDuplication"
              style="min-width: 100px;"
            >
              중복 확인
            </button>

            <button 
              type="button" 
              class="btn btn-outline-light flex-shrink-0 px-3" 
              @click="recommendNickname" 
              :disabled="isAiLoading"
              style="min-width: 90px;"
            >
              <span v-if="isAiLoading" class="spinner-border spinner-border-sm" role="status"></span>
              <span v-else>AI 추천</span>
            </button>
          </div>

          <div v-if="nicknameFeedback" :class="isNicknameAvailable ? 'text-success' : 'text-danger'" class="small mt-1 text-start fw-bold">
            {{ nicknameFeedback }}
          </div>
          
          <div v-if="errors.nickname" class="text-danger small mt-1 text-start">{{ errors.nickname.join(', ') }}</div>
        </div>

        <!-- 비밀번호 -->
        <div>
          <div class="form-floating text-dark">
            <input type="password" class="form-control" id="password" placeholder="비밀번호" v-model.trim="password" :class="{ 'is-invalid': errors.password1 }">
            <label for="password">비밀번호 <span class="text-danger">*</span></label>
          </div>
          <div v-if="errors.password1" class="text-danger small mt-1 text-start">{{ errors.password1.join(', ') }}</div>
        </div>

        <!-- 비밀번호 확인 -->
        <div>
          <div class="form-floating text-dark">
            <input type="password" class="form-control" id="password2" placeholder="비밀번호 확인" v-model.trim="password2">
            <label for="password2">비밀번호 확인 <span class="text-danger">*</span></label>
          </div>
        </div>

        <!-- 이메일 -->
        <div>
          <div class="form-floating text-dark">
            <input type="email" class="form-control" id="email" placeholder="이메일" v-model.trim="email" :class="{ 'is-invalid': errors.email }">
            <label for="email">이메일</label>
          </div>
          <div v-if="errors.email" class="text-danger small mt-1 text-start">{{ errors.email.join(', ') }}</div>
        </div>
        
        <div v-if="errors.non_field_errors" class="text-danger small text-center">{{ errors.non_field_errors.join(', ') }}</div>

        <!-- 회원가입 버튼 -->
        <button type="submit" class="btn btn-primary w-100 py-2 mt-3 fw-bold fs-5">회원가입</button>
        
        <!-- 로그인하기 -->
        <div class="mt-4 text-secondary">
          이미 계정이 있으신가요? <router-link :to="{name: 'login'}" class="text-white ms-1 text-decoration-none">로그인하기</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const username = ref('')
const nickname = ref('')
const email = ref('')
const password = ref('')
const password2 = ref('')
const errors = ref({})
const store = useAuthStore()

// 아이디 중복 확인 관련 변수
const isUsernameChecked = ref(false)
const isUsernameAvailable = ref(false)
const usernameFeedback = ref('')

// AI 추천 관련 상태 변수
const isAiLoading = ref(false)
const aiSuggestion = ref('')

// 닉네임 중복 확인 관련 변수
const isNicknameChecked = ref(false)    // 중복 확인 버튼을 눌렀는가?
const isNicknameAvailable = ref(false)  // 사용 가능한 닉네임인가?
const nicknameFeedback = ref('')         // 결과 메시지 (성공/실패)

const performSignUp = async () => {
  errors.value = {} // 초기화
  // 아이디 중복 확인 검사
  if (!isUsernameChecked.value) {
    alert('아이디 중복 확인을 진행해주세요.')
    return
  }
  if (!isUsernameAvailable.value) {
    alert('이미 사용 중인 아이디입니다.')
    return
  }
  // 닉네임 중복 확인 검사
  if (!isNicknameChecked.value) {
    alert('닉네임 중복 확인을 진행해주세요.')
    return
  }
  if (!isNicknameAvailable.value) {
    alert('이미 사용 중인 닉네임입니다.')
    return
  }

  if (password.value !== password2.value) {
    alert('비밀번호가 일치하지 않습니다.')
    return
  }

  const payload = {
    username: username.value,
    nickname: nickname.value,
    password1: password.value,
    password2: password2.value,
  }
  if (email.value) {
    payload.email = email.value
  }
  
  try {
    await store.signUp(payload)
  } catch (err) {
    if (err.response && err.response.data) {
      errors.value = err.response.data
    }
  }
}

// 아이디 변경 시 상태 초기화
watch(username, () => {
  isUsernameChecked.value = false
  isUsernameAvailable.value = false
  usernameFeedback.value = ''
})

// 아이디 중복 확인 함수
const checkUsernameDuplication = async () => {
  if (!username.value) {
    alert('아이디를 입력해주세요.')
    return
  }
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/accounts/check-username/', {
      params: { username: username.value }
    })
    isUsernameAvailable.value = response.data.is_available
    usernameFeedback.value = response.data.message
    isUsernameChecked.value = true
  } catch (error) {
    console.error('아이디 중복 확인 실패:', error)
  }
}

// 닉네임 추천 함수
const recommendNickname = async () => {
  isAiLoading.value = true
  try {
    // 백엔드 DRF 서버 엔드포인트 호출
    const response = await axios.get('http://127.0.0.1:8000/api/v1/accounts/recommend-nickname/')
    const suggestedName = response.data.nickname
    
    aiSuggestion.value = suggestedName
    nickname.value = suggestedName
  } catch (error) {
    console.error("닉네임 추천 실패:", error)
    alert("닉네임 추천 기능을 일시적으로 사용할 수 없습니다.")
  } finally {
    isAiLoading.value = false
  }
}

// 닉네임 값이 변경되면 다시 중복 확인을 받도록 초기화
watch(nickname, () => {
  isNicknameChecked.value = false
  isNicknameAvailable.value = false
  nicknameFeedback.value = ''
})

// 닉네임 중복 확인 함수
const checkNicknameDuplication = async () => {
  if (!nickname.value) {
    alert('닉네임을 입력해주세요.')
    return
  }
  
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/v1/accounts/check-nickname/`, {
      params: { nickname: nickname.value }
    })
    
    isNicknameAvailable.value = response.data.is_available
    nicknameFeedback.value = response.data.message
    isNicknameChecked.value = true
    
  } catch (error) {
    console.error('중복 확인 실패:', error)
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
.btn-outline-light {
  border: 1px solid #dee2e6;
}
</style>
