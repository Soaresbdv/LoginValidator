<template>
    <div class="two-fa">
        <h2>Verificação em Duas Etapas</h2>
        <p>Digite o código do Google Authenticator</p>
        <input v-model="code" placeholder="Código de 6 dígitos">
        <button @click="verify">Verificar</button>
        <button @click="cancel" class="cancel">Cancelar</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            code: ''
        }
    },
    methods: {
        verify() {
            if (this.code.length === 6) {
                this.$emit('verify', this.code)
            }
        },
        cancel() {
            this.$emit('cancel')
        }
    }
}
</script>