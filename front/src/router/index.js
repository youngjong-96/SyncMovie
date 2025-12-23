import { createRouter, createWebHistory } from 'vue-router'
import LogIn from '@/views/accounts/LogIn.vue'
import SignUp from '@/views/accounts/SignUp.vue'
import MyPage from '@/views/accounts/MyPage.vue'
import PasswordReset from '@/views/accounts/PasswordReset.vue'
import MainPage from '@/views/movies/MainPage.vue'
import MovieDetail from '@/views/movies/MovieDetail.vue'
import RecommendPage from '@/views/movies/RecommendPage.vue'
import HomePage from '@/views/HomePage.vue'
import SearchView from '@/views/movies/SearchView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path: '/', name: 'home', component: HomePage},
    {path: '/movies', name: 'movies', component: MainPage},
    {path: '/movies/:id', name: 'movieDetail', component: MovieDetail},
    {path: '/recommend/:type?/:step?', name: 'recommend', component: RecommendPage},
    {path: '/signup', name: 'signup', component: SignUp},
    {path: '/login', name: 'login', component: LogIn},
    {path: '/password-reset', name: 'passwordReset', component: PasswordReset},
    {path: '/mypage/:userId?', name: 'mypage', component: MyPage},
    {path: '/search', name: 'search', component: SearchView},
  ],
})

router.beforeEach((to, from) => {
  const token = localStorage.getItem('token')
  const isLoggedIn = !!token

  const publicPages = ['home', 'login', 'signup', 'passwordReset']
  const authRequired = !publicPages.includes(to.name)

  if (authRequired && !isLoggedIn) {
    alert('회원가입 혹은 로그인 후 서비스를 이용할 수 있습니다.')
    return { name: 'signup' }
  }

  if (isLoggedIn && publicPages.includes(to.name)) {
    return { name: 'movies' }
  }
})

export default router
