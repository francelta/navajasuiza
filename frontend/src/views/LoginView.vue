<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-ns-darker via-ns-dark to-ns-darker relative overflow-hidden">
    <!-- Background decoration -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-ns-accent/5 blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-indigo-600/5 blur-3xl"></div>
    </div>

    <!-- Login Card -->
    <div class="relative z-10 w-full max-w-md animate-fade-in">
      <div class="glass rounded-2xl p-8 shadow-2xl shadow-black/30">
        <!-- Logo Area -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-ns-accent to-indigo-600 mb-4 shadow-lg shadow-ns-accent/25">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-white tracking-tight">NavajaSuiza</h1>
          <p class="text-slate-400 text-sm mt-1">Panel Empresarial — Acceso Restringido</p>
        </div>

        <!-- Error Message -->
        <Transition name="slide-fade">
          <div v-if="auth.error" class="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm text-center">
            {{ auth.error }}
          </div>
        </Transition>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Empleado ID -->
          <div>
            <label for="empleado_id" class="block text-sm font-medium text-slate-300 mb-1.5">
              ID Empleado
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </span>
              <input
                id="empleado_id"
                v-model="empleadoId"
                type="text"
                required
                placeholder="EMP001"
                autocomplete="username"
                class="w-full pl-10 pr-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300"
              />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-slate-300 mb-1.5">
              Contraseña
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </span>
              <input
                id="password"
                v-model="password"
                type="password"
                required
                placeholder="••••••••"
                autocomplete="current-password"
                class="w-full pl-10 pr-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300"
              />
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="auth.loading"
            class="w-full py-3 px-4 rounded-xl font-semibold text-white bg-gradient-to-r from-ns-accent to-indigo-600 hover:from-ns-accent-light hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-ns-accent/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-ns-accent/20 hover:shadow-ns-accent/40 hover:scale-[1.02] active:scale-[0.98]"
          >
            <span v-if="auth.loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Accediendo...
            </span>
            <span v-else>Iniciar Sesión</span>
          </button>
        </form>

        <!-- Footer -->
        <p class="text-center text-xs text-slate-500 mt-6">
          Acceso exclusivo para empleados autorizados
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const empleadoId = ref('')
const password = ref('')

async function handleLogin() {
  const result = await auth.login(empleadoId.value, password.value)
  if (result.success) {
    router.push({ name: 'Dashboard' })
  }
}
</script>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
