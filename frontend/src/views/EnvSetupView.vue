<template>
  <div class="min-h-screen bg-gradient-to-br from-ns-darker via-ns-dark to-ns-darker">
    <!-- Header -->
    <header class="border-b border-slate-700/50 bg-ns-dark/50 backdrop-blur-lg sticky top-0 z-30">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3">
            <button @click="$router.push({ name: 'Dashboard' })" class="w-9 h-9 rounded-xl bg-slate-700/50 hover:bg-slate-600/50 flex items-center justify-center transition-colors duration-200 border border-slate-600/30">
              <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 class="text-lg font-bold text-white tracking-tight">Configuración del Sistema</h1>
              <p class="text-xs text-slate-400 -mt-0.5">Setup Wizard — Variables de Entorno</p>
            </div>
          </div>
          <!-- Progress badge -->
          <div v-if="summary" class="flex items-center gap-2">
            <div class="w-24 h-2 rounded-full bg-slate-700/50 overflow-hidden">
              <div class="h-full rounded-full transition-all duration-700 ease-out"
                :class="summary.percentage === 100 ? 'bg-emerald-500' : 'bg-amber-500'"
                :style="{ width: summary.percentage + '%' }"></div>
            </div>
            <span class="text-xs font-mono" :class="summary.percentage === 100 ? 'text-emerald-400' : 'text-amber-400'">
              {{ summary.configured }}/{{ summary.total }}
            </span>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <svg class="animate-spin h-8 w-8 text-ns-accent" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>

      <template v-else>
        <!-- Summary Banner -->
        <div v-if="summary" class="glass rounded-2xl p-5 mb-6 animate-fade-in">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-xl flex items-center justify-center"
                :class="summary.percentage === 100 ? 'bg-emerald-500/15' : 'bg-amber-500/15'">
                <span class="text-2xl">{{ summary.percentage === 100 ? '✅' : '⚙️' }}</span>
              </div>
              <div>
                <h2 class="text-white font-semibold">
                  {{ summary.percentage === 100 ? 'Configuración Completa' : 'Configuración Pendiente' }}
                </h2>
                <p class="text-sm text-slate-400">
                  {{ summary.configured }} de {{ summary.total }} variables configuradas
                  <span v-if="summary.pending > 0" class="text-amber-400 ml-1">({{ summary.pending }} pendientes)</span>
                </p>
              </div>
            </div>
            <button
              v-if="pendingChanges.length > 0"
              @click="saveAll"
              :disabled="saving"
              class="flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-white bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40 hover:scale-[1.02] active:scale-[0.98] text-sm"
            >
              <svg v-if="saving" class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Guardar {{ pendingChanges.length }} cambio{{ pendingChanges.length !== 1 ? 's' : '' }}
            </button>
          </div>
        </div>

        <!-- Groups  -->
        <div class="space-y-4">
          <div v-for="(group, gi) in groups" :key="group.name"
            class="glass rounded-2xl overflow-hidden animate-fade-in"
            :style="{ animationDelay: gi * 0.08 + 's' }">
            <!-- Group header -->
            <div class="px-5 py-3.5 border-b border-slate-700/40 flex items-center justify-between bg-slate-800/20">
              <div class="flex items-center gap-3">
                <span class="text-lg">{{ groupIcons[group.name] || '📋' }}</span>
                <h3 class="text-sm font-semibold text-white">{{ group.name }}</h3>
              </div>
              <span class="text-xs font-mono px-2 py-0.5 rounded-lg"
                :class="group.configured === group.total
                  ? 'bg-emerald-500/15 text-emerald-400'
                  : 'bg-amber-500/15 text-amber-400'">
                {{ group.configured }}/{{ group.total }}
              </span>
            </div>

            <!-- Variables -->
            <div class="divide-y divide-slate-800/40">
              <div v-for="v in group.variables" :key="v.key"
                class="px-5 py-3.5 flex items-center gap-4 hover:bg-slate-700/10 transition-colors duration-200">
                <!-- Status icon -->
                <div class="flex-shrink-0">
                  <span v-if="v.is_set" class="text-emerald-400 text-lg">✅</span>
                  <span v-else class="text-amber-400 text-lg">⚠️</span>
                </div>

                <!-- Label + key -->
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium" :class="v.is_set ? 'text-slate-300' : 'text-white'">
                    {{ v.label }}
                  </p>
                  <p class="text-xs font-mono text-slate-500 truncate">{{ v.key }}</p>
                </div>

                <!-- Input / Status -->
                <div class="w-64 flex-shrink-0">
                  <div v-if="v.is_set" class="flex items-center gap-2">
                    <input type="text" disabled
                      :value="v.current_value || (v.is_sensitive ? '••••••••' : 'Configurado')"
                      class="w-full px-3 py-2 rounded-lg bg-slate-800/30 border border-slate-700/30 text-slate-500 text-sm cursor-not-allowed font-mono" />
                    <span class="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center">
                      <svg class="w-3 h-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                      </svg>
                    </span>
                  </div>
                  <input v-else
                    v-model="formValues[v.key]"
                    :type="v.is_sensitive ? 'password' : 'text'"
                    :placeholder="v.placeholder"
                    class="w-full px-3 py-2 rounded-lg bg-ns-darker/80 border border-amber-500/30 text-white placeholder-slate-500 text-sm font-mono focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400/50 transition-all duration-300" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Toast -->
      <Transition name="toast">
        <div v-if="toast.show" class="fixed bottom-6 right-6 z-50 max-w-sm">
          <div class="px-5 py-3 rounded-xl shadow-2xl border backdrop-blur-lg flex items-center gap-3"
            :class="toast.type === 'success'
              ? 'bg-emerald-900/80 border-emerald-500/30 text-emerald-300'
              : 'bg-red-900/80 border-red-500/30 text-red-300'">
            <span>{{ toast.type === 'success' ? '✅' : '❌' }}</span>
            <span class="text-sm">{{ toast.message }}</span>
          </div>
        </div>
      </Transition>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/api/axios'

const loading = ref(true)
const saving = ref(false)
const groups = ref([])
const summary = ref(null)
const formValues = reactive({})
const toast = reactive({ show: false, message: '', type: 'success' })

const groupIcons = {
  'Django': '🔧',
  'Email SMTP': '📧',
  'Klaes / ETL': '📄',
  'Sage X3': '🏭',
}

const pendingChanges = computed(() => {
  return Object.entries(formValues)
    .filter(([_, value]) => value && value.trim())
    .map(([key, value]) => ({ key, value: value.trim() }))
})

function showToast(message, type = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3500)
}

async function fetchStatus() {
  loading.value = true
  try {
    const { data } = await api.get('/config/status/')
    groups.value = data.groups
    summary.value = data.summary

    // Clear form values — only populate empty ones
    for (const group of data.groups) {
      for (const v of group.variables) {
        if (!v.is_set && !formValues[v.key]) {
          formValues[v.key] = ''
        }
      }
    }
  } catch (err) {
    showToast('Error al cargar la configuración', 'error')
  } finally {
    loading.value = false
  }
}

async function saveAll() {
  if (pendingChanges.value.length === 0 || saving.value) return
  saving.value = true

  let successCount = 0
  let errorMessages = []

  for (const { key, value } of pendingChanges.value) {
    try {
      await api.post('/config/update/', { key, value })
      successCount++
      delete formValues[key]
    } catch (err) {
      errorMessages.push(err.response?.data?.detail || `Error en ${key}`)
    }
  }

  if (successCount > 0) {
    showToast(`${successCount} variable${successCount > 1 ? 's' : ''} guardada${successCount > 1 ? 's' : ''} correctamente`)
  }
  if (errorMessages.length > 0) {
    setTimeout(() => showToast(errorMessages.join('. '), 'error'), successCount > 0 ? 3600 : 0)
  }

  saving.value = false
  await fetchStatus()
}

onMounted(fetchStatus)
</script>

<style scoped>
.toast-enter-active, .toast-leave-active {
  transition: all 0.4s ease;
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.95);
}
</style>
