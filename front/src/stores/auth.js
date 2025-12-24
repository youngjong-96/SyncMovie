import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const userProfile = ref(null) // Added state for user profile
  const isLoggedIn = computed(() => !!token.value)
  const router = useRouter()
  const API_URL = import.meta.env.VITE_API_URL

  // 회원가입
  const signUp = function (payload) {
    return axios({
        method: 'post',
        url: `${API_URL}/accounts/signup/`,
        data: payload
      })
      .then((res) => {
        // 회원가입 성공 시 바로 로그인 처리 (토큰 발급)
        const key = res.data.key
        token.value = key
        localStorage.setItem('token', key)
        router.push({ name: 'movies' })
      })
      .catch((err) => {
        console.log(err)
        throw err
      })
  }

  // 로그인
  const logIn = function (payload) {
    return axios({
        method: 'post',
        url: `${API_URL}/accounts/login/`,
        data: payload
      })
      .then((res) => {
        const key = res.data.key
        token.value = key
        localStorage.setItem('token', key)
        router.push({ name: 'movies' })
      })
      .catch((err) => {
        console.log(err)
        throw err
      })
  }

  // 로그아웃
  const logOut = function (redirectLocation = { name: 'home' }) {
    token.value = null
    userProfile.value = null // Clear profile on logout
    localStorage.removeItem('token')
    router.push(redirectLocation)
  }

  // 유저 프로필 받아오기
  const getUserProfile = async (userId = null) => {
    try {
      const url = userId 
        ? `${API_URL}/api/v1/accounts/profile/${userId}/` 
        : `${API_URL}/api/v1/accounts/profile/`

      const response = await axios({
        method: 'get',
        url: url,
        headers: {
          Authorization: `Token ${token.value}`
        }
      })
      userProfile.value = response.data
    } catch (err) {
      console.log(err)
    }
  }

  // 유저 ID 확인
  const checkUsername = async (username) => {
    try {
      const response = await axios({
        method: 'post',
        url: `${API_URL}/api/v1/accounts/check-username/`,
        data: { username }
      })
      return response.data.exists
    } catch (err) {
      console.log(err)
      return false
    }
  }

  // 비밀번호 수정
  const resetPassword = function (payload) {
    return axios({
      method: 'post',
      url: `${API_URL}/api/v1/accounts/reset-password/`,
      data: payload
    })
    .then((res) => {
      return res.data
    })
    .catch((err) => {
      throw err
    })
  }

  // 회원 탈퇴
  const deleteAccount = async () => {
    const accessToken = token.value
    logOut({ name: 'login' })
    
    try {
      await axios({
        method: 'delete',
        url: `${API_URL}/api/v1/accounts/delete/`,
        headers: {
          Authorization: `Token ${accessToken}`
        }
      })
    } catch (err) {
      console.log(err)
    }
  }

  return { token, userProfile, isLoggedIn, API_URL, signUp, logIn, logOut, getUserProfile, checkUsername, resetPassword, deleteAccount }
})
