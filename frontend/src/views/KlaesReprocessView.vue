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
              <h1 class="text-lg font-bold text-white tracking-tight">Reprocesamiento Klaes</h1>
              <p class="text-xs text-slate-400 -mt-0.5">XML → ETL → Sage X3</p>
            </div>
          </div>
          <span class="text-xs text-amber-400 bg-amber-500/10 px-3 py-1 rounded-lg font-medium border border-amber-500/20">
            📋 Tarea 1
          </span>
        </div>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <!-- Input Section -->
      <div class="glass rounded-2xl p-6 sm:p-8 mb-6 animate-fade-in">
        <h2 class="text-xl font-bold text-white mb-1">Código de Producción</h2>
        <p class="text-slate-400 text-sm mb-5">Introduce el código Q/R para buscar y reprocesar el archivo XML</p>

        <form @submit.prevent="startReprocess" class="flex flex-col sm:flex-row gap-3">
          <div class="flex-1 relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </span>
            <input
              id="klaes_code"
              v-model="code"
              type="text"
              maxlength="8"
              placeholder="Q1234567"
              :disabled="processing"
              class="w-full pl-11 pr-4 py-3.5 rounded-xl bg-ns-darker/80 border text-white placeholder-slate-500 focus:outline-none focus:ring-1 transition-all duration-300 uppercase tracking-widest font-mono text-lg"
              :class="codeInputClasses"
              @input="onCodeInput"
            />
            <span v-if="codeError" class="absolute right-3 top-1/2 -translate-y-1/2 text-red-400">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            <span v-if="codeValid && code.length === 8" class="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-400">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
          </div>
          <button
            type="submit"
            :disabled="!codeValid || processing"
            class="px-6 py-3.5 rounded-xl font-semibold text-white bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-amber-500/20 hover:shadow-amber-500/40 hover:scale-[1.02] active:scale-[0.98] whitespace-nowrap"
          >
            <span v-if="processing" class="flex items-center gap-2">
              <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Procesando...
            </span>
            <span v-else class="flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Ejecutar
            </span>
          </button>
        </form>
        <p v-if="codeError" class="text-red-400 text-xs mt-2">{{ codeError }}</p>
        <p v-else class="text-slate-500 text-xs mt-2">Formato: Q o R seguido de 7 dígitos</p>
      </div>

      <!-- Progress Console -->
      <Transition name="slide-fade">
        <div v-if="steps.length > 0" class="glass rounded-2xl p-6 sm:p-8 animate-fade-in-up">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-white flex items-center gap-2">
              <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Consola de Progreso
            </h3>
            <span
              class="text-xs font-medium px-2.5 py-1 rounded-lg"
              :class="summaryClasses"
            >
              {{ processedCode }}
            </span>
          </div>

          <!-- Step List -->
          <div class="space-y-2">
            <div
              v-for="(step, index) in steps"
              :key="index"
              class="flex items-start gap-3 p-3 rounded-xl transition-all duration-300"
              :class="stepBgClass(step)"
              :style="{ animationDelay: `${index * 0.1}s` }"
            >
              <!-- Status Icon -->
              <div class="flex-shrink-0 mt-0.5">
                <span v-if="step.status === 'ok'" class="text-emerald-400 text-lg">✅</span>
                <span v-else-if="step.status === 'error'" class="text-red-400 text-lg">❌</span>
                <span v-else-if="step.status === 'warning'" class="text-amber-400 text-lg">⚠️</span>
                <span v-else class="text-slate-400 text-lg">⏳</span>
              </div>

              <!-- Step Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-mono text-slate-500">PASO {{ step.step }}</span>
                  <span class="text-sm font-medium" :class="stepTextClass(step)">
                    {{ stepLabels[step.step] || 'Procesando...' }}
                  </span>
                </div>
                <p class="text-sm mt-0.5" :class="step.status === 'error' ? 'text-red-300' : 'text-slate-400'">
                  {{ step.message }}
                </p>
                <p v-if="step.detail && typeof step.detail === 'object'" class="text-xs text-slate-500 mt-1 font-mono truncate">
                  {{ formatDetail(step.detail) }}
                </p>
              </div>
            </div>
          </div>

          <!-- Summary -->
          <div v-if="summary" class="mt-4 pt-4 border-t border-slate-700/50">
            <p class="text-sm font-medium" :class="pipelineSuccess ? 'text-emerald-400' : 'text-red-400'">
              {{ summary }}
            </p>
          </div>
        </div>
      </Transition>

      <!-- Pipeline diagram -->
      <div class="mt-8 text-center text-xs text-slate-600 animate-fade-in">
        <div class="flex items-center justify-center gap-2 flex-wrap">
          <span class="px-2 py-1 rounded bg-slate-800/50">📄 XML</span>
          <span>→</span>
          <span class="px-2 py-1 rounded bg-slate-800/50">🔍 Buscar</span>
          <span>→</span>
          <span class="px-2 py-1 rounded bg-slate-800/50">📂 Copiar</span>
          <span>→</span>
          <span class="px-2 py-1 rounded bg-slate-800/50">⚙️ ETL</span>
          <span>→</span>
          <span class="px-2 py-1 rounded bg-slate-800/50">💾 CSV</span>
          <span>→</span>
          <span class="px-2 py-1 rounded bg-slate-800/50">🚀 Sage</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/api/axios'

const code = ref('')
const processing = ref(false)
const steps = ref([])
const summary = ref('')
const pipelineSuccess = ref(false)
const processedCode = ref('')

const codeRegex = /^[QRqr]\d{7}$/

const codeValid = computed(() => codeRegex.test(code.value))
const codeError = computed(() => {
  if (!code.value) return ''
  if (code.value.length > 0 && !/^[QRqr]/.test(code.value)) {
    return 'Debe comenzar con Q o R'
  }
  if (code.value.length === 8 && !codeValid.value) {
    return 'Formato inválido. Esperado: Q/R + 7 dígitos'
  }
  return ''
})

const codeInputClasses = computed(() => {
  if (codeError.value) return 'border-red-500/50 focus:border-red-500 focus:ring-red-500/50'
  if (codeValid.value && code.value.length === 8) return 'border-emerald-500/50 focus:border-emerald-500 focus:ring-emerald-500/50'
  return 'border-slate-600/50 focus:border-amber-500 focus:ring-amber-500/50'
})

const summaryClasses = computed(() => {
  if (pipelineSuccess.value) return 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
  if (steps.value.length > 0) return 'bg-red-500/15 text-red-400 border border-red-500/30'
  return 'bg-slate-700/50 text-slate-400'
})

const stepLabels = {
  1: 'Validación de Código',
  2: 'Búsqueda de Archivo XML',
  3: 'Copia a Carpeta Importación',
  4: 'Ejecución ETL',
  5: 'Backup CSV',
  6: 'Importación Sage X3',
}

function onCodeInput() {
  // Force uppercase and filter non-alphanumeric
  code.value = code.value.toUpperCase().replace(/[^QR0-9]/gi, '').slice(0, 8)
}

function stepBgClass(step) {
  if (step.status === 'ok') return 'bg-emerald-500/5'
  if (step.status === 'error') return 'bg-red-500/5'
  if (step.status === 'warning') return 'bg-amber-500/5'
  return 'bg-slate-700/20'
}

function stepTextClass(step) {
  if (step.status === 'ok') return 'text-emerald-300'
  if (step.status === 'error') return 'text-red-300'
  if (step.status === 'warning') return 'text-amber-300'
  return 'text-slate-300'
}

function formatDetail(detail) {
  if (detail.found_path) return `📍 ${detail.found_path}`
  if (detail.destination) return `📂 ${detail.destination}`
  if (detail.backup_path) return `💾 ${detail.backup_path}`
  if (detail.stderr) return `⚠️ ${detail.stderr}`
  if (detail.soap_fault) return `🔴 ${detail.soap_fault}`
  return JSON.stringify(detail)
}

async function startReprocess() {
  if (!codeValid.value || processing.value) return

  processing.value = true
  steps.value = []
  summary.value = ''
  pipelineSuccess.value = false
  processedCode.value = code.value.toUpperCase()

  try {
    const { data } = await api.post('/tools/klaes/reprocess/', {
      code: code.value,
    })

    steps.value = data.steps
    summary.value = data.summary
    pipelineSuccess.value = data.success
  } catch (err) {
    if (err.response?.data?.steps) {
      steps.value = err.response.data.steps
      summary.value = err.response.data.summary
      pipelineSuccess.value = false
    } else {
      steps.value = [{
        step: 0,
        status: 'error',
        message: err.response?.data?.detail || 'Error de conexión con el servidor.',
      }]
      summary.value = '❌ Error de comunicación con el backend.'
    }
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.4s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
