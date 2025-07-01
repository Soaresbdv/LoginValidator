<template>
    <form @submit.prevent="submit">
        <h2>Login</h2>
        <input v-model="username" placeholder="Usuário" required>
        <input v-model="password" type="password" placeholder="Senha" required>
        <button type="submit">Entrar</button>
    </form>
</template>

<script>
import { authApi } from '../assets/js/auth.js';

export default {
  data() {
    return {
      username: '',
      password: '',
      error: null
    }
  },
  methods: {
    async submit() {
      try {
        const result = await authApi.login(this.username, this.password);
        
        if (result.success) {
          if (result.requires_2fa) {
            this.$emit('need2fa', this.username);
          } else {
            this.$emit('login-success', result.token);
          }
        } else {
          this.error = 'Credenciais inválidas';
        }
      } catch (err) {
        this.error = 'Erro ao conectar com o servidor';
      }
    }
  }
}
</script>