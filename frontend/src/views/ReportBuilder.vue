<template>
  <div class="min-h-screen bg-gradient-to-br from-ns-darker via-ns-dark to-ns-darker">
    <!-- Header -->
    <header class="border-b border-slate-700/50 bg-ns-dark/50 backdrop-blur-lg sticky top-0 z-30">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-14">
          <div class="flex items-center gap-3">
            <button @click="$router.push({ name: 'Reports' })" class="w-8 h-8 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 flex items-center justify-center transition-colors border border-slate-600/30">
              <svg class="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            </button>
            <div>
              <input v-model="app.name" @blur="saveAppMeta" class="text-base font-bold text-white bg-transparent border-b border-transparent hover:border-slate-600 focus:border-indigo-400 focus:outline-none pb-0.5 transition-colors w-64" />
              <p class="text-xs text-slate-500 -mt-0.5">App #{{ $route.params.id }}</p>
            </div>
          </div>
          <!-- Top-level view switcher -->
          <div class="flex gap-1 p-0.5 rounded-lg bg-slate-800/50 border border-slate-700/30">
            <button v-for="v in views" :key="v.id" @click="activeView = v.id"
              class="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
              :class="activeView === v.id ? 'bg-ns-accent text-white shadow' : 'text-slate-400 hover:text-white'">
              {{ v.icon }} {{ v.label }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">

      <!-- ═══════════════════════════════════ -->
      <!-- VIEW 1: Conexiones Globales        -->
      <!-- ═══════════════════════════════════ -->
      <div v-if="activeView === 'connections'" class="space-y-5 animate-fade-in">
        <div class="glass rounded-2xl p-5">
          <h2 class="text-white font-semibold mb-3 flex items-center gap-2 text-sm"><span>🔌</span> {{ editingConnId ? 'Editar Conexión' : 'Nueva Conexión' }}</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5">
            <div><label class="lbl">Nombre</label><input v-model="cf.name" class="inp" placeholder="SageX3" /></div>
            <div><label class="lbl">Motor</label><select v-model="cf.engine" class="inp"><option value="sqlserver">SQL Server</option><option value="mysql">MySQL</option><option value="postgresql">PostgreSQL</option></select></div>
            <div><label class="lbl">Host</label><input v-model="cf.host" class="inp" placeholder="192.168.2.202" /></div>
            <div><label class="lbl">Puerto</label><input v-model.number="cf.port" type="number" class="inp" /></div>
            <div><label class="lbl">Base de Datos</label><input v-model="cf.database" class="inp" placeholder="SAGEX3DATA" /></div>
            <div><label class="lbl">Usuario</label><input v-model="cf.username" class="inp" /></div>
            <div><label class="lbl">Contraseña</label><input v-model="cf.password" type="password" class="inp" /></div>
            <div class="flex items-end gap-2">
              <button @click="saveConn" class="flex-1 py-2 rounded-lg text-xs font-semibold text-white bg-indigo-500 hover:bg-indigo-400 transition-colors">{{ editingConnId ? '💾' : '+' }}</button>
              <button v-if="editingConnId" @click="cancelEditConn" class="py-2 px-3 rounded-lg text-xs text-slate-400 border border-slate-600/30 hover:bg-slate-700/30">✕</button>
            </div>
          </div>
          <div v-if="connMsg" class="mt-2 px-3 py-1.5 rounded-lg text-xs" :class="connMsg.ok ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'">{{ connMsg.ok ? '✅' : '❌' }} {{ connMsg.text }}</div>
        </div>
        <div class="glass rounded-2xl p-5">
          <h2 class="text-white font-semibold mb-3 text-sm flex items-center justify-between"><span>🗄️ Conexiones</span><span class="text-xs font-mono px-2 py-0.5 rounded bg-slate-700/50 text-slate-400">{{ conns.length }}</span></h2>
          <div v-if="!conns.length" class="text-center py-4 text-xs text-slate-500">Sin conexiones.</div>
          <div v-else class="space-y-1.5">
            <div v-for="c in conns" :key="c.id" class="flex items-center justify-between px-3 py-2.5 rounded-xl bg-slate-800/20 border border-slate-700/30 hover:bg-slate-700/20 transition-colors">
              <div class="flex items-center gap-2.5">
                <span>{{ eiconn(c.engine) }}</span>
                <div><p class="text-sm font-medium text-white">{{ c.name }}</p><p class="text-xs text-slate-500 font-mono">{{ c.host }}/{{ c.database }}</p></div>
              </div>
              <div class="flex gap-1.5">
                <button @click="testConn(c.id)" class="px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-400 text-xs hover:bg-cyan-500/20 transition-colors">🔗 Test</button>
                <button @click="startEditConn(c)" class="w-7 h-7 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-xs">✏️</button>
                <button @click="delConn(c.id)" class="w-7 h-7 rounded-lg bg-red-500/10 hover:bg-red-500/20 flex items-center justify-center text-red-400 text-xs">🗑️</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════ -->
      <!-- VIEW 2: Editor de Carga            -->
      <!-- ═══════════════════════════════════ -->
      <div v-if="activeView === 'editor'" class="animate-fade-in">
        <div class="flex gap-4" style="min-height: calc(100vh - 140px);">
          <!-- Sidebar: Script Tabs -->
          <div class="w-56 flex-shrink-0 glass rounded-2xl p-4 flex flex-col">
            <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Scripts de Carga</h3>
            <div class="space-y-1 flex-1 overflow-y-auto">
              <div v-for="s in app.scripts" :key="s.id" @click="selectScript(s)"
                class="flex items-center gap-2 px-3 py-2 rounded-lg text-xs cursor-pointer transition-all"
                :class="activeScript?.id === s.id ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:bg-slate-700/30 border border-transparent'">
                <span class="w-5 h-5 rounded bg-slate-700/50 flex items-center justify-center text-[10px] font-mono">{{ s.order + 1 }}</span>
                <span class="truncate flex-1">{{ s.name }}</span>
                <span v-if="s.last_error" class="w-2 h-2 rounded-full bg-red-400" title="Error"></span>
                <span v-else-if="s.last_row_count > 0" class="w-2 h-2 rounded-full bg-emerald-400" title="OK"></span>
              </div>
            </div>
            <button @click="addScript" class="mt-3 w-full py-2 rounded-lg text-xs font-semibold text-indigo-400 border border-indigo-500/30 hover:bg-indigo-500/10 transition-colors">+ Nuevo Script</button>
          </div>

          <!-- Main Editor Area -->
          <div class="flex-1 space-y-4">
            <div v-if="activeScript" class="glass rounded-2xl p-5">
              <div class="grid grid-cols-3 gap-3 mb-3">
                <div><label class="lbl">Nombre del Script</label><input v-model="activeScript.name" class="inp" /></div>
                <div>
                  <label class="lbl">Conexión</label>
                  <select v-model.number="activeScript.connection" class="inp">
                    <option :value="null" disabled>Selecciona...</option>
                    <option v-for="c in conns" :key="c.id" :value="c.id">{{ eiconn(c.engine) }} {{ c.name }}</option>
                  </select>
                </div>
                <div class="flex items-end gap-2">
                  <button @click="saveScript" class="flex-1 py-2 rounded-lg text-xs font-semibold text-white bg-indigo-500 hover:bg-indigo-400 transition-colors">💾 Guardar</button>
                  <button @click="delScript" class="py-2 px-3 rounded-lg text-xs text-red-400 border border-red-500/30 hover:bg-red-500/10 transition-colors">🗑️</button>
                </div>
              </div>
              <div class="relative">
                <div class="absolute top-2 right-2 px-1.5 py-0.5 rounded bg-slate-700/60 text-[10px] text-slate-500 font-mono z-10">SQL</div>
                <textarea v-model="activeScript.query_text" rows="14" spellcheck="false"
                  class="w-full px-4 py-3 rounded-xl bg-ns-darker/90 border border-slate-600/50 text-green-400 font-mono text-sm leading-relaxed resize-y focus:outline-none focus:border-indigo-400 transition-all placeholder-slate-600"
                  placeholder="SELECT * FROM BPCUSTOMER WHERE BPCSTA = 2"
                ></textarea>
              </div>
            </div>
            <div v-else class="glass rounded-2xl p-12 text-center">
              <span class="text-3xl block mb-2">📝</span>
              <p class="text-sm text-slate-500">Selecciona o crea un script en el panel izquierdo.</p>
            </div>

            <!-- Execute All + Log -->
            <div class="glass rounded-2xl p-5">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-white font-semibold text-sm flex items-center gap-2"><span>⚡</span> Carga de Datos</h3>
                <button @click="executeAll" :disabled="executing || !app.scripts?.length" class="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 disabled:opacity-40 transition-all flex items-center gap-1.5">
                  <svg v-if="executing" class="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                  ▶️ Cargar Todos los Datos
                </button>
              </div>
              <!-- Execution Log -->
              <div v-if="execLog.length" class="space-y-1.5">
                <div v-for="(entry, i) in execLog" :key="i" class="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-mono"
                  :class="entry.status === 'ok' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'">
                  <span>{{ entry.status === 'ok' ? '✅' : '❌' }}</span>
                  <span class="font-semibold">{{ entry.script }}</span>
                  <span class="text-slate-500">→ {{ entry.connection }}</span>
                  <span class="ml-auto">{{ entry.rows }} filas · {{ entry.time_ms }}ms</span>
                </div>
              </div>
              <p v-else class="text-xs text-slate-500">Ejecuta todos los scripts para cargar el modelo de datos.</p>
            </div>

            <!-- Data Preview per table -->
            <div v-if="Object.keys(loadedTables).length" class="space-y-4">
              <div v-for="(tbl, name) in loadedTables" :key="name" class="glass rounded-2xl p-5">
                <h3 class="text-white font-semibold text-sm mb-2 flex items-center justify-between">
                  <span>📋 {{ name }}</span>
                  <span class="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400">{{ tbl.row_count }} filas</span>
                </h3>
                <div class="overflow-x-auto rounded-xl border border-slate-700/30 max-h-48">
                  <table class="w-full text-xs"><thead class="sticky top-0 bg-slate-800"><tr class="border-b border-slate-700/30">
                    <th v-for="col in tbl.columns" :key="col.name" class="px-3 py-2 text-left font-medium text-slate-400 uppercase whitespace-nowrap">{{ col.name }}</th>
                  </tr></thead><tbody class="divide-y divide-slate-800/30">
                    <tr v-for="(row, i) in tbl.rows.slice(0, 20)" :key="i" class="hover:bg-slate-700/10">
                      <td v-for="col in tbl.columns" :key="col.name" class="px-3 py-1.5 whitespace-nowrap font-mono" :class="col.type === 'numeric' ? 'text-emerald-400 text-right' : 'text-slate-300'">{{ row[col.name] ?? '—' }}</td>
                    </tr>
                  </tbody></table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════ -->
      <!-- VIEW 3: Visor de Hojas (Sheets)    -->
      <!-- ═══════════════════════════════════ -->
      <div v-if="activeView === 'sheets'" class="animate-fade-in">
        <!-- Sheet Tabs -->
        <div class="flex items-center gap-1 mb-4 p-1 rounded-xl bg-slate-800/50 border border-slate-700/30">
          <button v-for="sh in app.sheets" :key="sh.id" @click="activeSheet = sh"
            class="px-4 py-2 rounded-lg text-xs font-medium transition-all"
            :class="activeSheet?.id === sh.id ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:text-white border border-transparent'">
            {{ sh.title }}
          </button>
          <button @click="addSheet" class="px-3 py-2 rounded-lg text-xs text-indigo-400 hover:bg-indigo-500/10 transition-colors">+ Hoja</button>
        </div>

        <div v-if="activeSheet" class="space-y-5">
          <!-- Sheet config -->
          <div class="glass rounded-2xl p-5">
            <div class="grid grid-cols-3 gap-3">
              <div><label class="lbl">Título de Hoja</label><input v-model="activeSheet.title" class="inp" /></div>
              <div class="flex items-end gap-2">
                <button @click="saveSheet" class="py-2 px-4 rounded-lg text-xs font-semibold text-white bg-emerald-500 hover:bg-emerald-400 transition-colors">💾 Guardar Hoja</button>
                <button @click="addChart" :disabled="!hasData" class="py-2 px-4 rounded-lg text-xs font-semibold text-white bg-violet-500 hover:bg-violet-400 disabled:opacity-40 transition-colors">+ Gráfico</button>
                <button @click="delSheet" class="py-2 px-3 rounded-lg text-xs text-red-400 border border-red-500/30 hover:bg-red-500/10 transition-colors">🗑️</button>
              </div>
            </div>
            <p v-if="!hasData" class="text-xs text-amber-400 mt-2">⚠️ Carga datos en el "Editor de Carga" para crear gráficos.</p>
          </div>

          <!-- Charts Grid -->
          <div v-if="activeSheet.layout_json.length" class="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div v-for="(ch, idx) in activeSheet.layout_json" :key="ch.id" class="glass rounded-2xl p-5">
              <div class="flex items-center justify-between mb-2">
                <input v-model="ch.title" class="text-white font-semibold bg-transparent border-b border-transparent hover:border-slate-600 focus:border-indigo-400 focus:outline-none text-sm pb-0.5 w-40 transition-colors" />
                <div class="flex items-center gap-1.5">
                  <select v-model="ch.type" @change="renderCharts" class="px-2 py-1 rounded-lg bg-ns-darker border border-slate-600/50 text-white text-xs"><option value="bar">📊</option><option value="doughnut">🍩</option><option value="line">📈</option></select>
                  <button @click="activeSheet.layout_json.splice(idx, 1)" class="w-6 h-6 rounded text-red-400 hover:bg-red-500/20 flex items-center justify-center text-xs">✕</button>
                </div>
              </div>
              <div class="grid grid-cols-3 gap-2 mb-2">
                <div><label class="block text-[10px] text-slate-500">Tabla</label>
                  <select v-model="ch.source" @change="renderCharts" class="w-full px-2 py-1 rounded-lg bg-ns-darker border border-slate-600/50 text-white text-xs">
                    <option v-for="t in tableNames" :key="t" :value="t">{{ t }}</option>
                  </select>
                </div>
                <div><label class="block text-[10px] text-slate-500">Dimensión</label>
                  <select v-model="ch.dimension" @change="renderCharts" class="w-full px-2 py-1 rounded-lg bg-ns-darker border border-slate-600/50 text-white text-xs">
                    <option v-for="c in getCatCols(ch.source)" :key="c" :value="c">{{ c }}</option>
                  </select>
                </div>
                <div><label class="block text-[10px] text-slate-500">Métrica</label>
                  <select v-model="ch.metric" @change="renderCharts" class="w-full px-2 py-1 rounded-lg bg-ns-darker border border-slate-600/50 text-white text-xs">
                    <option v-for="c in getNumCols(ch.source)" :key="c" :value="c">{{ c }}</option>
                  </select>
                </div>
              </div>
              <div v-if="ch.chartData" class="h-52">
                <component :is="ccmp(ch.type)" :data="ch.chartData" :options="copts(ch.type)" />
              </div>
              <div v-else class="h-52 flex items-center justify-center text-xs text-slate-500">Configura tabla, dimensión y métrica</div>
            </div>
          </div>
          <div v-else class="glass rounded-2xl p-10 text-center"><span class="text-3xl block mb-2">📊</span><p class="text-xs text-slate-500">Añade gráficos para diseñar este dashboard.</p></div>
        </div>
        <div v-else class="glass rounded-2xl p-10 text-center"><span class="text-3xl block mb-2">📄</span><p class="text-xs text-slate-500">Crea una hoja para empezar.</p></div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, markRaw } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Bar, Doughnut, Line } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend, Filler)
const CL = ['rgba(99,102,241,0.8)','rgba(16,185,129,0.8)','rgba(245,158,11,0.8)','rgba(239,68,68,0.8)','rgba(139,92,246,0.8)','rgba(6,182,212,0.8)','rgba(236,72,153,0.8)','rgba(34,197,94,0.8)','rgba(251,146,60,0.8)','rgba(59,130,246,0.8)']
const _c = { bar: markRaw(Bar), doughnut: markRaw(Doughnut), line: markRaw(Line) }
function ccmp(t) { return _c[t] || _c.bar }
function copts(t) {
  const b = { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#94a3b8', font: { size: 10 } } } } }
  if (t !== 'doughnut') b.scales = { x: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: 'rgba(51,65,85,0.3)' } }, y: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: 'rgba(51,65,85,0.3)' } } }
  return b
}
function eiconn(e) { return { sqlserver: '🟦', mysql: '🐬', postgresql: '🐘' }[e] || '🗄️' }

const route = useRoute()
const activeView = ref('connections')
const views = [
  { id: 'connections', label: 'Conexiones', icon: '🔌' },
  { id: 'editor', label: 'Editor de Carga', icon: '📝' },
  { id: 'sheets', label: 'Hojas', icon: '📊' },
]

const app = reactive({ name: '', description: '', scripts: [], sheets: [] })
const conns = ref([])
const executing = ref(false)
const execLog = ref([])
const loadedTables = ref({})
const activeScript = ref(null)
const activeSheet = ref(null)

// Connection form
const cf = reactive({ name: '', engine: 'sqlserver', host: '', port: 1433, database: '', username: '', password: '' })
const editingConnId = ref(null)
const connMsg = ref(null)

const hasData = computed(() => Object.keys(loadedTables.value).length > 0)
const tableNames = computed(() => Object.keys(loadedTables.value))

function getCatCols(src) {
  const t = loadedTables.value[src]
  return t ? t.columns.filter(c => c.type === 'categorical').map(c => c.name) : []
}
function getNumCols(src) {
  const t = loadedTables.value[src]
  return t ? t.columns.filter(c => c.type === 'numeric').map(c => c.name) : []
}

// ── Connections ──
async function fetchConns() { try { const { data } = await api.get('/reports/connections/'); conns.value = data } catch {} }
async function saveConn() {
  connMsg.value = null
  try {
    if (editingConnId.value) { await api.put(`/reports/connections/${editingConnId.value}/`, cf); connMsg.value = { ok: true, text: 'Actualizada.' } }
    else { await api.post('/reports/connections/', cf); connMsg.value = { ok: true, text: 'Creada.' } }
    await fetchConns(); cancelEditConn()
  } catch (e) { connMsg.value = { ok: false, text: e.response?.data?.detail || e.response?.data?.name?.[0] || 'Error.' } }
}
function startEditConn(c) { editingConnId.value = c.id; Object.assign(cf, { name: c.name, engine: c.engine, host: c.host, port: c.port, database: c.database, username: c.username || '', password: '' }) }
function cancelEditConn() { editingConnId.value = null; Object.assign(cf, { name: '', engine: 'sqlserver', host: '', port: 1433, database: '', username: '', password: '' }) }
async function delConn(id) { if (!confirm('¿Eliminar?')) return; try { await api.delete(`/reports/connections/${id}/`); conns.value = conns.value.filter(c => c.id !== id) } catch {} }
async function testConn(id) { connMsg.value = null; try { const { data } = await api.post(`/reports/connections/${id}/test/`); connMsg.value = { ok: data.success, text: data.message } } catch (e) { connMsg.value = { ok: false, text: e.response?.data?.message || 'Error.' } } }

// ── App ──
async function loadApp() {
  try {
    const { data } = await api.get(`/reports/apps/${route.params.id}/`)
    Object.assign(app, data)
    if (app.scripts?.length) activeScript.value = app.scripts[0]
    if (app.sheets?.length) activeSheet.value = app.sheets[0]
  } catch {}
}
async function saveAppMeta() { try { await api.put(`/reports/apps/${route.params.id}/`, { name: app.name, description: app.description }) } catch {} }

// ── Scripts ──
function selectScript(s) { activeScript.value = s }
async function addScript() {
  try {
    const { data } = await api.post('/reports/scripts/', { app: route.params.id, connection: conns.value[0]?.id, name: `Script ${(app.scripts?.length || 0) + 1}`, query_text: '', order: app.scripts?.length || 0 })
    app.scripts.push(data); activeScript.value = data
  } catch {}
}
async function saveScript() {
  if (!activeScript.value) return
  try { const { data } = await api.put(`/reports/scripts/${activeScript.value.id}/`, activeScript.value); Object.assign(activeScript.value, data) } catch {}
}
async function delScript() {
  if (!activeScript.value || !confirm('¿Eliminar este script?')) return
  try { await api.delete(`/reports/scripts/${activeScript.value.id}/`); app.scripts = app.scripts.filter(s => s.id !== activeScript.value.id); activeScript.value = app.scripts[0] || null } catch {}
}

// ── Execute All ──
async function executeAll() {
  executing.value = true; execLog.value = []; loadedTables.value = {}
  try {
    const { data } = await api.post(`/reports/apps/${route.params.id}/execute/`)
    execLog.value = data.log; loadedTables.value = data.tables
    await loadApp() // refresh metadata
    renderCharts()
  } catch (e) { execLog.value = [{ script: 'Error', connection: '', status: 'error', rows: 0, time_ms: 0, message: e.response?.data?.detail || 'Error.' }] }
  finally { executing.value = false }
}

// ── Sheets ──
async function addSheet() {
  try {
    const { data } = await api.post('/reports/sheets/', { app: route.params.id, title: `Hoja ${(app.sheets?.length || 0) + 1}`, layout_json: [], order: app.sheets?.length || 0 })
    app.sheets.push(data); activeSheet.value = data
  } catch {}
}
async function saveSheet() {
  if (!activeSheet.value) return
  try { await api.put(`/reports/sheets/${activeSheet.value.id}/`, {
    title: activeSheet.value.title,
    layout_json: activeSheet.value.layout_json.map(({ id, type, title, source, dimension, metric }) => ({ id, type, title, source, dimension, metric }))
  }) } catch {}
}
async function delSheet() {
  if (!activeSheet.value || !confirm('¿Eliminar?')) return
  try { await api.delete(`/reports/sheets/${activeSheet.value.id}/`); app.sheets = app.sheets.filter(s => s.id !== activeSheet.value.id); activeSheet.value = app.sheets[0] || null } catch {}
}

// ── Charts ──
let cn = 0
function addChart() {
  const firstTable = tableNames.value[0] || ''
  activeSheet.value.layout_json.push({
    id: `c_${++cn}`, type: 'bar', title: `Gráfico ${cn}`,
    source: firstTable, dimension: getCatCols(firstTable)[0] || '', metric: getNumCols(firstTable)[0] || '', chartData: null
  })
  renderCharts()
}
function renderCharts() {
  if (!activeSheet.value) return
  for (const ch of activeSheet.value.layout_json) {
    const tbl = loadedTables.value[ch.source]
    if (!tbl || !ch.dimension || !ch.metric) { ch.chartData = null; continue }
    const g = {}
    for (const r of tbl.rows) { const k = String(r[ch.dimension] ?? 'N/A'); g[k] = (g[k] || 0) + (Number(r[ch.metric]) || 0) }
    const entries = Object.entries(g).sort((a, b) => b[1] - a[1]).slice(0, 15)
    ch.chartData = { labels: entries.map(e => e[0]), datasets: [{ label: ch.metric, data: entries.map(e => Math.round(e[1] * 100) / 100), backgroundColor: CL.slice(0, entries.length), borderColor: 'rgba(15,23,42,1)', borderWidth: 1 }] }
  }
}

onMounted(async () => { await fetchConns(); await loadApp() })
</script>

<style scoped>
.inp { @apply w-full px-3 py-2 rounded-lg bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-indigo-400 transition-all; }
.lbl { @apply block text-[10px] font-medium text-slate-500 mb-0.5; }
</style>
