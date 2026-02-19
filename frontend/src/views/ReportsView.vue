<template>
  <div class="min-h-screen bg-gradient-to-br from-ns-darker via-ns-dark to-ns-darker">
    <!-- Header -->
    <header class="border-b border-slate-700/50 bg-ns-dark/50 backdrop-blur-lg sticky top-0 z-30">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3">
            <button @click="$router.push({ name: 'Dashboard' })" class="w-9 h-9 rounded-xl bg-slate-700/50 hover:bg-slate-600/50 flex items-center justify-center transition-colors duration-200 border border-slate-600/30">
              <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 class="text-lg font-bold text-white tracking-tight">Informes & Dashboards</h1>
              <p class="text-xs text-slate-400 -mt-0.5">Qlik · CSV · Excel → Gráficos interactivos</p>
            </div>
          </div>
          <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 cursor-default" title="AGENTE_DATA_ENGINEER 📊">
            <span class="text-xs">📊</span>
            <span class="text-xs font-mono text-indigo-400">data_engineer</span>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Upload Zone -->
      <div class="glass rounded-2xl p-6 mb-6 animate-fade-in">
        <h2 class="text-white font-semibold mb-1 flex items-center gap-2">
          <span class="text-lg">📤</span> Subir Archivo de Datos
        </h2>
        <p class="text-sm text-slate-400 mb-5">Arrastra un archivo o selecciónalo. Formatos: <code class="text-indigo-400">.csv</code> <code class="text-indigo-400">.xlsx</code> <code class="text-indigo-400">.qvd</code></p>

        <!-- Drop Zone -->
        <div
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
          @click="$refs.fileInput.click()"
          class="relative border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-300"
          :class="isDragging
            ? 'border-indigo-400 bg-indigo-500/10'
            : 'border-slate-600/50 hover:border-indigo-500/50 hover:bg-slate-800/30'"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".csv,.xlsx,.xls,.qvd"
            @change="onFileSelect"
            class="hidden"
          />
          <div v-if="!uploading" class="space-y-3">
            <div class="w-16 h-16 mx-auto rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
              <svg class="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p class="text-sm text-slate-300">
              <span class="text-indigo-400 font-semibold">Haz clic</span> o arrastra tu archivo aquí
            </p>
            <p class="text-xs text-slate-500">Máximo 50 MB · Se procesará automáticamente</p>
          </div>
          <div v-else class="space-y-3">
            <svg class="animate-spin h-10 w-10 mx-auto text-indigo-400" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p class="text-sm text-indigo-300 font-medium">Procesando {{ uploadFilename }}...</p>
            <p class="text-xs text-slate-500">El Data Engineer está analizando tu archivo</p>
          </div>
        </div>

        <div v-if="uploadError" class="mt-4 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-fade-in">
          ❌ {{ uploadError }}
        </div>
        <div v-if="uploadSuccess" class="mt-4 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm animate-fade-in">
          ✅ {{ uploadSuccess }}
        </div>
      </div>

      <!-- Reports List -->
      <div v-if="reports.length > 0" class="glass rounded-2xl p-6 mb-6 animate-fade-in">
        <h2 class="text-white font-semibold mb-4 flex items-center justify-between">
          <span class="flex items-center gap-2"><span class="text-lg">📁</span> Informes Subidos</span>
          <span class="text-xs font-mono px-2 py-0.5 rounded-lg bg-slate-700/50 text-slate-400">{{ reports.length }} archivo{{ reports.length !== 1 ? 's' : '' }}</span>
        </h2>
        <div class="space-y-2">
          <div
            v-for="report in reports" :key="report.id"
            @click="loadReport(report.id)"
            class="flex items-center justify-between px-4 py-3 rounded-xl border transition-all duration-200 cursor-pointer"
            :class="activeReportId === report.id
              ? 'bg-indigo-500/10 border-indigo-500/30'
              : 'bg-slate-800/20 border-slate-700/30 hover:bg-slate-700/20'"
          >
            <div class="flex items-center gap-3">
              <span class="text-lg">{{ fileIcon(report.file_type) }}</span>
              <div>
                <p class="text-sm font-medium text-white">{{ report.filename }}</p>
                <p class="text-xs text-slate-500">{{ report.row_count }} filas · {{ report.column_count }} columnas · {{ report.charts_count }} gráficos</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-xs px-2 py-0.5 rounded-lg font-mono"
                :class="report.status === 'completed'
                  ? 'bg-emerald-500/15 text-emerald-400'
                  : report.status === 'error'
                    ? 'bg-red-500/15 text-red-400'
                    : 'bg-amber-500/15 text-amber-400'">
                {{ report.status }}
              </span>
              <button @click.stop="deleteReport(report.id)" class="w-7 h-7 rounded-lg bg-red-500/10 hover:bg-red-500/20 flex items-center justify-center text-red-400 transition-colors" title="Eliminar">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard Area -->
      <div v-if="dashboardData" class="space-y-6 animate-fade-in">
        <!-- Summary Cards -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="glass rounded-xl p-4">
            <p class="text-xs text-slate-500 mb-1">Total Filas</p>
            <p class="text-2xl font-bold text-white">{{ dashboardData.summary.total_rows.toLocaleString() }}</p>
          </div>
          <div class="glass rounded-xl p-4">
            <p class="text-xs text-slate-500 mb-1">Columnas</p>
            <p class="text-2xl font-bold text-indigo-400">{{ dashboardData.summary.total_columns }}</p>
          </div>
          <div class="glass rounded-xl p-4">
            <p class="text-xs text-slate-500 mb-1">Gráficos</p>
            <p class="text-2xl font-bold text-emerald-400">{{ dashboardData.charts.length }}</p>
          </div>
          <div class="glass rounded-xl p-4">
            <p class="text-xs text-slate-500 mb-1">Memoria</p>
            <p class="text-2xl font-bold text-amber-400">{{ dashboardData.summary.memory_usage_mb }} MB</p>
          </div>
        </div>

        <!-- KPI Cards (Numeric Stats) -->
        <div v-if="Object.keys(dashboardData.summary.numeric_stats).length" class="glass rounded-2xl p-6">
          <h3 class="text-white font-semibold mb-4 flex items-center gap-2"><span>📈</span> Estadísticas Numéricas</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="(stats, col) in dashboardData.summary.numeric_stats" :key="col" class="rounded-xl bg-slate-800/30 border border-slate-700/30 p-4">
              <p class="text-sm font-semibold text-indigo-400 mb-2 truncate">{{ col }}</p>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <div><span class="text-slate-500">Suma:</span> <span class="text-white font-mono">{{ stats.sum?.toLocaleString() }}</span></div>
                <div><span class="text-slate-500">Media:</span> <span class="text-white font-mono">{{ stats.mean?.toLocaleString() }}</span></div>
                <div><span class="text-slate-500">Mín:</span> <span class="text-white font-mono">{{ stats.min?.toLocaleString() }}</span></div>
                <div><span class="text-slate-500">Máx:</span> <span class="text-white font-mono">{{ stats.max?.toLocaleString() }}</span></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Grid -->
        <div v-if="dashboardData.charts.length" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-for="chart in dashboardData.charts" :key="chart.id" class="glass rounded-2xl p-6">
            <h3 class="text-white font-semibold mb-4 flex items-center gap-2">
              <span>{{ chart.type === 'bar' ? '📊' : chart.type === 'doughnut' ? '🍩' : '📈' }}</span>
              {{ chart.title }}
            </h3>
            <div class="h-72">
              <component
                :is="chartComponent(chart.type)"
                :data="chart.data"
                :options="chartOptions(chart.type)"
                class="w-full h-full"
              />
            </div>
          </div>
        </div>

        <!-- Table Preview -->
        <div v-if="dashboardData.table_preview" class="glass rounded-2xl p-6">
          <h3 class="text-white font-semibold mb-4 flex items-center justify-between">
            <span class="flex items-center gap-2"><span>📋</span> Vista Previa de Datos</span>
            <span class="text-xs font-mono px-2 py-0.5 rounded-lg bg-slate-700/50 text-slate-400">
              {{ dashboardData.table_preview.showing }} de {{ dashboardData.table_preview.total_rows.toLocaleString() }} filas
            </span>
          </h3>
          <div class="overflow-x-auto rounded-xl border border-slate-700/30">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-slate-700/30">
                  <th
                    v-for="col in dashboardData.table_preview.columns" :key="col"
                    class="px-4 py-2.5 text-left text-xs font-medium text-slate-400 uppercase tracking-wider whitespace-nowrap"
                  >{{ col }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800/30">
                <tr v-for="(row, i) in dashboardData.table_preview.rows" :key="i" class="hover:bg-slate-700/10 transition-colors">
                  <td
                    v-for="col in dashboardData.table_preview.columns" :key="col"
                    class="px-4 py-2.5 text-slate-300 whitespace-nowrap max-w-xs truncate font-mono text-xs"
                  >{{ row[col] ?? '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!dashboardData && !uploading && reports.length === 0" class="glass rounded-2xl p-12 text-center animate-fade-in">
        <div class="w-20 h-20 mx-auto mb-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
          <span class="text-4xl">📊</span>
        </div>
        <h3 class="text-white font-semibold mb-2">Sin informes todavía</h3>
        <p class="text-sm text-slate-400">Sube un archivo de datos para generar dashboards automáticamente.</p>
      </div>

      <!-- Loading dashboard -->
      <div v-if="loadingDashboard" class="glass rounded-2xl p-12 text-center animate-fade-in">
        <svg class="animate-spin h-10 w-10 mx-auto text-indigo-400 mb-4" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <p class="text-sm text-indigo-300">Cargando dashboard...</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, markRaw } from 'vue'
import api from '@/api/axios'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Bar, Doughnut, Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
)

const isDragging = ref(false)
const uploading = ref(false)
const uploadFilename = ref('')
const uploadError = ref('')
const uploadSuccess = ref('')
const reports = ref([])
const activeReportId = ref(null)
const dashboardData = ref(null)
const loadingDashboard = ref(false)

const chartComponents = { bar: markRaw(Bar), doughnut: markRaw(Doughnut), line: markRaw(Line) }
function chartComponent(type) { return chartComponents[type] || chartComponents.bar }

function chartOptions(type) {
  const base = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#94a3b8', font: { size: 11 } } },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(99, 102, 241, 0.3)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
      },
    },
  }
  if (type === 'bar' || type === 'line') {
    base.scales = {
      x: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: 'rgba(51, 65, 85, 0.3)' } },
      y: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: 'rgba(51, 65, 85, 0.3)' } },
    }
  }
  return base
}

function fileIcon(type) {
  return { csv: '📄', xlsx: '📗', xls: '📗', qvd: '🔮' }[type] || '📄'
}

async function fetchReports() {
  try {
    const { data } = await api.get('/reports/')
    reports.value = data
  } catch { /* silent */ }
}

async function uploadFile(file) {
  uploadError.value = ''
  uploadSuccess.value = ''
  uploading.value = true
  uploadFilename.value = file.name

  const formData = new FormData()
  formData.append('file', file)

  try {
    const { data } = await api.post('/reports/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    uploadSuccess.value = `"${file.name}" procesado: ${data.row_count} filas, ${data.charts_generated} gráficos generados.`
    await fetchReports()
    loadReport(data.id)
  } catch (err) {
    uploadError.value = err.response?.data?.detail || 'Error al subir el archivo.'
  } finally {
    uploading.value = false
  }
}

function onFileSelect(e) {
  const file = e.target.files[0]
  if (file) uploadFile(file)
  e.target.value = ''
}

function onDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) uploadFile(file)
}

async function loadReport(id) {
  activeReportId.value = id
  loadingDashboard.value = true
  dashboardData.value = null

  try {
    const { data } = await api.get(`/reports/${id}/data/`)
    dashboardData.value = data
  } catch (err) {
    uploadError.value = err.response?.data?.detail || 'Error al cargar el informe.'
  } finally {
    loadingDashboard.value = false
  }
}

async function deleteReport(id) {
  try {
    await api.delete(`/reports/${id}/`)
    reports.value = reports.value.filter(r => r.id !== id)
    if (activeReportId.value === id) {
      activeReportId.value = null
      dashboardData.value = null
    }
  } catch { /* silent */ }
}

onMounted(fetchReports)
</script>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: all 0.3s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
