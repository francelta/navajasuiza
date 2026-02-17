<template>
  <div class="min-h-screen bg-gradient-to-br from-ns-darker via-ns-dark to-ns-darker">
    <!-- Header -->
    <header class="border-b border-slate-700/50 bg-ns-dark/50 backdrop-blur-lg sticky top-0 z-30">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3">
            <button @click="$router.push({ name: 'Dashboard' })" class="w-9 h-9 rounded-xl bg-slate-700/50 hover:bg-slate-600/50 flex items-center justify-center transition-colors duration-200 border border-slate-600/30">
              <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 class="text-lg font-bold text-white tracking-tight">Gestión de Usuarios</h1>
              <p class="text-xs text-slate-400 -mt-0.5">Alta de Empleados</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-ns-accent-light bg-ns-accent/15 px-3 py-1 rounded-lg font-medium">
              🔑 SuperAdmin
            </span>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <!-- Title -->
      <div class="text-center mb-8 animate-fade-in">
        <h2 class="text-2xl font-bold text-white mb-2">Dar de Alta Empleado</h2>
        <p class="text-slate-400 text-sm">Las credenciales se enviarán automáticamente al email del empleado</p>
      </div>

      <!-- Success Message -->
      <Transition name="slide-fade">
        <div v-if="successMsg" class="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm text-center animate-fade-in">
          <div class="flex items-center justify-center gap-2 mb-1">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="font-semibold">¡Empleado creado!</span>
          </div>
          {{ successMsg }}
        </div>
      </Transition>

      <!-- Error Message -->
      <Transition name="slide-fade">
        <div v-if="errorMsg" class="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm text-center">
          <div class="flex items-center justify-center gap-2 mb-1">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span class="font-semibold">Error</span>
          </div>
          {{ errorMsg }}
        </div>
      </Transition>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="glass rounded-2xl p-6 sm:p-8 space-y-5 animate-fade-in-up">
        <!-- Name row -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="first_name" class="block text-sm font-medium text-slate-300 mb-1.5">Nombre</label>
            <input
              id="first_name"
              v-model="form.first_name"
              type="text"
              required
              placeholder="Juan"
              class="w-full px-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300"
            />
          </div>
          <div>
            <label for="last_name" class="block text-sm font-medium text-slate-300 mb-1.5">Apellidos</label>
            <input
              id="last_name"
              v-model="form.last_name"
              type="text"
              required
              placeholder="García López"
              class="w-full px-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300"
            />
          </div>
        </div>

        <!-- Email -->
        <div>
          <label for="email" class="block text-sm font-medium text-slate-300 mb-1.5">Email Corporativo</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </span>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              placeholder="juan.garcia@acristalia.com"
              class="w-full pl-10 pr-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300"
            />
          </div>
          <p v-if="emailError" class="text-red-400 text-xs mt-1">{{ emailError }}</p>
        </div>

        <!-- Passwords -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="password" class="block text-sm font-medium text-slate-300 mb-1.5">Contraseña</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              minlength="6"
              placeholder="Mín. 6 caracteres"
              class="w-full px-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300"
            />
          </div>
          <div>
            <label for="confirm_password" class="block text-sm font-medium text-slate-300 mb-1.5">Confirmar Contraseña</label>
            <input
              id="confirm_password"
              v-model="confirmPassword"
              type="password"
              required
              minlength="6"
              placeholder="Repetir contraseña"
              class="w-full px-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300"
              :class="{ 'border-red-500/50': confirmPassword && form.password !== confirmPassword }"
            />
            <p v-if="confirmPassword && form.password !== confirmPassword" class="text-red-400 text-xs mt-1">
              Las contraseñas no coinciden
            </p>
          </div>
        </div>

        <!-- Role & Department -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="role" class="block text-sm font-medium text-slate-300 mb-1.5">Rol</label>
            <select
              id="role"
              v-model="form.role"
              class="w-full px-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300 appearance-none"
            >
              <option value="empleado">👤 Empleado</option>
              <option value="admin">⚙️ Administrador</option>
              <option value="superadmin">🔑 SuperAdmin</option>
            </select>
          </div>
          <div>
            <label for="departamento" class="block text-sm font-medium text-slate-300 mb-1.5">Departamento</label>
            <input
              id="departamento"
              v-model="form.departamento"
              type="text"
              placeholder="Ventas, IT, RRHH..."
              class="w-full px-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300"
            />
          </div>
        </div>

        <!-- Submit -->
        <div class="pt-2">
          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="w-full py-3.5 px-4 rounded-xl font-semibold text-white bg-gradient-to-r from-ns-accent to-indigo-600 hover:from-ns-accent-light hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-ns-accent/50 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-ns-accent/20 hover:shadow-ns-accent/40 hover:scale-[1.02] active:scale-[0.98]"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Creando y enviando email...
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              Crear Empleado y Enviar Credenciales
            </span>
          </button>
        </div>
      </form>

      <!-- Info note -->
      <div class="mt-6 text-center text-xs text-slate-500 animate-fade-in">
        <p>📧 Se enviará un email con las credenciales al correo corporativo del empleado</p>
        <p class="mt-1">Si falla el envío de email, el usuario NO será creado (rollback automático)</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/api/axios'

const loading = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  role: 'empleado',
  departamento: '',
})

const confirmPassword = ref('')

const emailError = computed(() => {
  if (!form.value.email) return ''
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.value.email)) {
    return 'Introduce un email válido'
  }
  return ''
})

const isFormValid = computed(() => {
  return (
    form.value.first_name.trim() &&
    form.value.last_name.trim() &&
    form.value.email.trim() &&
    !emailError.value &&
    form.value.password.length >= 6 &&
    form.value.password === confirmPassword.value
  )
})

async function handleSubmit() {
  if (!isFormValid.value) return

  loading.value = true
  successMsg.value = ''
  errorMsg.value = ''

  try {
    const { data } = await api.post('/admin/employees/', {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      email: form.value.email,
      password: form.value.password,
      role: form.value.role,
      departamento: form.value.departamento,
    })

    successMsg.value = data.detail
    // Reset form
    form.value = {
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      role: 'empleado',
      departamento: '',
    }
    confirmPassword.value = ''
  } catch (err) {
    const detail = err.response?.data?.detail || 'Error al crear el empleado.'
    const smtpError = err.response?.data?.smtp_error
    errorMsg.value = smtpError ? `${detail}\n${smtpError}` : detail
  } finally {
    loading.value = false
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
select option {
  background-color: #0f172a;
  color: #e2e8f0;
}
</style>
