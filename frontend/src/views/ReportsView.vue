<template>
  <div class="min-h-screen bg-gradient-to-br from-ns-darker via-ns-dark to-ns-darker">
    <header class="border-b border-slate-700/50 bg-ns-dark/50 backdrop-blur-lg sticky top-0 z-30">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3">
            <button @click="$router.push({ name: 'Dashboard' })" class="w-9 h-9 rounded-xl bg-slate-700/50 hover:bg-slate-600/50 flex items-center justify-center transition-colors border border-slate-600/30">
              <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            </button>
            <div>
              <h1 class="text-lg font-bold text-white tracking-tight">Informes & Dashboards</h1>
              <p class="text-xs text-slate-400 -mt-0.5">BI Application Hub</p>
            </div>
          </div>
          <button @click="createApp" class="px-4 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-400 hover:to-violet-500 transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
            Nueva App
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="loading" class="glass rounded-2xl p-12 text-center">
        <svg class="animate-spin h-10 w-10 mx-auto text-indigo-400 mb-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
        <p class="text-sm text-indigo-300">Cargando aplicaciones...</p>
      </div>

      <div v-else-if="apps.length === 0" class="glass rounded-2xl p-12 text-center animate-fade-in">
        <div class="w-20 h-20 mx-auto mb-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center"><span class="text-4xl">📦</span></div>
        <h3 class="text-white font-semibold mb-2">Sin aplicaciones BI</h3>
        <p class="text-sm text-slate-400 mb-4">Crea tu primera aplicación de informes para empezar.</p>
        <button @click="createApp" class="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-violet-600">+ Crear Nueva App</button>
      </div>

      <!-- App Cards Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-fade-in">
        <div v-for="app in apps" :key="app.id" class="glass rounded-2xl p-5 hover:ring-1 hover:ring-indigo-500/30 transition-all cursor-pointer group" @click="openApp(app.id)">
          <div class="flex items-start justify-between mb-3">
            <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/20 border border-indigo-500/20 flex items-center justify-center">
              <span class="text-xl">📊</span>
            </div>
            <button @click.stop="deleteApp(app.id)" class="w-7 h-7 rounded-lg bg-red-500/0 group-hover:bg-red-500/10 flex items-center justify-center text-red-400 opacity-0 group-hover:opacity-100 transition-all" title="Eliminar">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
          </div>
          <h3 class="text-white font-semibold text-sm mb-1 group-hover:text-indigo-300 transition-colors">{{ app.name }}</h3>
          <p v-if="app.description" class="text-xs text-slate-500 mb-3 line-clamp-2">{{ app.description }}</p>
          <div class="flex items-center gap-3 text-xs text-slate-500">
            <span class="flex items-center gap-1"><span class="text-indigo-400">📝</span> {{ app.script_count }} scripts</span>
            <span class="flex items-center gap-1"><span class="text-emerald-400">📊</span> {{ app.sheet_count }} hojas</span>
          </div>
          <p class="text-xs text-slate-600 mt-2 font-mono">{{ fmtDate(app.updated_at) }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

const router = useRouter()
const apps = ref([])
const loading = ref(true)

function fmtDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function fetchApps() {
  loading.value = true
  try { const { data } = await api.get('/reports/apps/'); apps.value = data } catch {}
  finally { loading.value = false }
}

async function createApp() {
  try {
    const { data } = await api.post('/reports/apps/', { name: 'Nueva Aplicación BI', description: '' })
    router.push({ name: 'ReportBuilder', params: { id: data.id } })
  } catch {}
}

function openApp(id) { router.push({ name: 'ReportBuilder', params: { id } }) }

async function deleteApp(id) {
  if (!confirm('¿Eliminar esta aplicación y todos sus scripts/hojas?')) return
  try { await api.delete(`/reports/apps/${id}/`); apps.value = apps.value.filter(a => a.id !== id) } catch {}
}

onMounted(fetchApps)
</script>
