import { reactive } from 'vue'

export const store = reactive({
    user: null,
    token: null,
    setAuthData(user, token) {
        this.user = user
        this.token = token
        localStorage.setItem('auth_token', token)
    },
    logout() {
        this.user = null
        this.token = null
        localStorage.removeItem('auth_token')
    }
})