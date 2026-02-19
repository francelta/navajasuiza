<template>
  <div class="min-h-screen bg-gradient-to-br from-ns-darker via-ns-dark to-ns-darker">
    <!-- Header -->
    <header class="border-b border-slate-700/50 bg-ns-dark/50 backdrop-blur-lg sticky top-0 z-30">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo & Title -->
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-ns-accent to-indigo-600 flex items-center justify-center shadow-lg shadow-ns-accent/20">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h1 class="text-lg font-bold text-white tracking-tight">NavajaSuiza</h1>
              <p class="text-xs text-slate-400 -mt-0.5">Panel de Herramientas</p>
            </div>
          </div>

          <!-- User Info & Logout -->
          <div class="flex items-center gap-4">
            <div class="text-right hidden sm:block">
              <p class="text-sm font-medium text-white">{{ auth.userName }}</p>
              <p class="text-xs text-slate-400">{{ roleBadge }}</p>
            </div>
            <button
              @click="handleLogout"
              class="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-700/50 hover:bg-red-500/20 text-slate-300 hover:text-red-400 border border-slate-600/40 hover:border-red-500/30 transition-all duration-300 text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span class="hidden sm:inline">Salir</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <!-- Welcome -->
      <div class="text-center mb-10 animate-fade-in">
        <h2 class="text-2xl sm:text-3xl font-bold text-white mb-2">
          Bienvenido, <span class="text-ns-accent-light">{{ auth.user?.first_name || auth.userName }}</span>
        </h2>
        <p class="text-slate-400">Selecciona una herramienta para comenzar</p>
      </div>

      <!-- 8 Buttons Grid (4x2) -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-5">
        <ToolButton
          v-for="tool in tools"
          :key="tool.number"
          :number="tool.number"
          :label="tool.label"
          :icon="tool.icon"
          :color="tool.color"
          @click="handleToolClick(tool)"
        />
      </div>

      <!-- Status bar -->
      <div class="mt-10 text-center text-xs text-slate-500 animate-fade-in">
        <span class="inline-flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-ns-success animate-pulse"></span>
          Sistema operativo — Entorno Local
        </span>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ToolButton from '@/components/ToolButton.vue'

const router = useRouter()
const auth = useAuthStore()

const roleLabels = {
  superadmin: '🔑 SuperAdmin',
  admin: '⚙️ Administrador',
  empleado: '👤 Empleado',
}

const roleBadge = computed(() => roleLabels[auth.userRole] || auth.userRole)

const tools = [
  { number: 1, label: 'Reprocesar Klaes', icon: 'folder', color: 'amber', route: 'KlaesReprocess' },
  { number: 2, label: 'Klaes Actions', icon: 'chart', color: 'emerald', route: 'KlaesManager' },
  { number: 3, label: 'Informes', icon: 'clipboard', color: 'indigo', route: 'Reports' },
  { number: 4, label: 'Calendario', icon: 'calendar', color: 'rose' },
  { number: 5, label: 'Mensajería', icon: 'chat', color: 'cyan' },
  { number: 6, label: 'Seguridad', icon: 'shield', color: 'violet' },
  { number: 7, label: 'Gestión Usuarios', icon: 'users', color: 'sky', route: 'AdminEmployees' },
  { number: 8, label: 'Configuración', icon: 'cog', color: 'orange', route: 'EnvSetup' },
]

function handleToolClick(tool) {
  if (tool.route) {
    router.push({ name: tool.route })
  } else {
    console.log(`Herramienta ${tool.number}: ${tool.label} — Próximamente`)
  }
}

function handleLogout() {
  auth.logout()
  router.push({ name: 'Login' })
}
</script>
