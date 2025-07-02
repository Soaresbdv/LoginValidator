<template>
  <form @submit.prevent="register">
    <h2>Registro</h2>
    <input v-model="email" type="email" placeholder="Email" required>
    <input v-model="password" type="password" placeholder="Senha" required>
    <button type="submit">Registrar</button>
  </form>

  <div v-if="showVerification">
    <h3>Verifique seu Email</h3>
    <input v-model="verificationCode" placeholder="Código de 6 dígitos">
    <button @click="verify">Verificar</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      verificationCode: '',
      showVerification: false
    }
  },
  methods: {
    async register() {
      const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: this.email,
          password: this.password
        })
      })
      if (response.ok) {
        this.showVerification = true
      }
    },
    async verify() {
      const response = await fetch('/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: this.email,
          code: this.verificationCode
        })
      })
      if (response.ok) {
        this.$router.push('/login')
      }
    }
  }
}
</script>