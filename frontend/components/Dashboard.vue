<template>
    <div>
        <h2>Bem-vindo, {{ store.user.username }}!</h2>
        <button @click="store.logout()">Sair</button>
        <section v-if="!store.user.twofa_enabled">
            <h3>Ativar 2FA</h3>
            <button @click="enable2FA">Configurar</button>
        </section>
    </div>
</template>