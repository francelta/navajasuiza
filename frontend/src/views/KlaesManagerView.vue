<template>
  <div class="min-h-screen bg-gradient-to-br from-ns-darker via-ns-dark to-ns-darker">
    <!-- Header -->
    <header class="border-b border-slate-700/50 bg-ns-dark/50 backdrop-blur-lg sticky top-0 z-30">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3">
            <button @click="$router.push({ name: 'Dashboard' })" class="w-9 h-9 rounded-xl bg-slate-700/50 hover:bg-slate-600/50 flex items-center justify-center transition-colors duration-200 border border-slate-600/30">
              <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 class="text-lg font-bold text-white tracking-tight">Klaes Actions</h1>
              <p class="text-xs text-slate-400 -mt-0.5">SQL Server · Base de Datos de Materiales</p>
            </div>
          </div>
          <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-violet-500/10 border border-violet-500/20 cursor-default" title="import antigravity 🐍">
            <span class="text-xs">🚀</span>
            <span class="text-xs font-mono text-violet-400">antigravity</span>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Tabs -->
      <div class="flex gap-1 p-1 rounded-xl bg-slate-800/50 border border-slate-700/30 mb-6 animate-fade-in">
        <button
          v-for="tab in tabs" :key="tab.id"
          @click="activeTab = tab.id"
          class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all duration-300"
          :class="activeTab === tab.id
            ? 'bg-ns-accent text-white shadow-lg shadow-ns-accent/20'
            : 'text-slate-400 hover:text-white hover:bg-slate-700/30'"
        >
          <span>{{ tab.icon }}</span>
          {{ tab.label }}
        </button>
      </div>

      <!-- ================================ -->
      <!-- TAB 1: Consultar Material       -->
      <!-- ================================ -->
      <div v-if="activeTab === 'query'" class="animate-fade-in">
        <div class="glass rounded-2xl p-6">
          <h2 class="text-white font-semibold mb-1 flex items-center gap-2">
            <span class="text-lg">🔍</span> Consultar Material
          </h2>
          <p class="text-sm text-slate-400 mb-5">Introduce el ID del material para consultar sus datos en la base de datos Klaes.</p>

          <div class="flex gap-3 mb-6">
            <div class="flex-1 relative">
              <input v-model="queryId" type="text" placeholder="ID Material (ej: MAT-001)" @keyup.enter="queryMaterial"
                class="w-full px-4 py-3 pl-11 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 font-mono focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300" />
              <svg class="w-5 h-5 text-slate-500 absolute left-3.5 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <button @click="queryMaterial" :disabled="!queryId.trim() || querying"
              class="px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-ns-accent to-indigo-600 hover:from-ns-accent-light hover:to-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-ns-accent/20 text-sm flex items-center gap-2">
              <svg v-if="querying" class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
              {{ querying ? 'Buscando...' : 'Consultar' }}
            </button>
          </div>

          <div v-if="queryError" class="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm mb-4 animate-fade-in">❌ {{ queryError }}</div>

          <Transition name="slide">
            <div v-if="materialData" class="rounded-xl border border-slate-700/40 overflow-hidden animate-fade-in">
              <div class="px-5 py-3 bg-slate-800/30 border-b border-slate-700/30 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-white flex items-center gap-2">📦 {{ materialData.material_id }}</h3>
                <span class="text-xs text-slate-500 font-mono">{{ materialData._queried_by }}</span>
              </div>
              <div class="divide-y divide-slate-800/40">
                <div v-for="field in materialFields" :key="field.key" class="px-5 py-3 flex items-center justify-between hover:bg-slate-700/10 transition-colors">
                  <span class="text-sm text-slate-400 flex items-center gap-2"><span>{{ field.icon }}</span> {{ field.label }}</span>
                  <span class="text-sm font-mono" :class="field.class || 'text-white'">{{ formatValue(materialData[field.key], field) }}</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <!-- ================================ -->
      <!-- TAB 2: Actualizar Precio        -->
      <!-- ================================ -->
      <div v-if="activeTab === 'update'" class="animate-fade-in">
        <div class="glass rounded-2xl p-6">
          <h2 class="text-white font-semibold mb-1 flex items-center gap-2"><span class="text-lg">💰</span> Actualizar Precio de Venta</h2>
          <p class="text-sm text-slate-400 mb-5">Modifica el precio de venta (VKPreis) de un material en la base de datos Klaes.</p>
          <form @submit.prevent="updatePrice" class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">ID del Material</label>
              <input v-model="updateForm.material_id" type="text" required placeholder="MAT-001"
                class="w-full px-4 py-3 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 font-mono focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400/50 transition-all duration-300" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Nuevo Precio de Venta (€)</label>
              <div class="relative">
                <input v-model="updateForm.new_price" type="number" step="0.01" min="0" required placeholder="99.50"
                  class="w-full px-4 py-3 pl-10 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 font-mono focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400/50 transition-all duration-300" />
                <span class="absolute left-3.5 top-3.5 text-slate-500 text-sm">€</span>
              </div>
            </div>
            <div class="flex items-start gap-3 px-4 py-3 rounded-xl bg-amber-500/8 border border-amber-500/20">
              <span class="text-amber-400 text-lg mt-0.5">⚠️</span>
              <div>
                <p class="text-sm text-amber-300 font-medium">Operación de escritura</p>
                <p class="text-xs text-amber-400/70">Este cambio se aplicará directamente en la base de datos de Klaes. Se registrará en la auditoría como <code class="bg-amber-500/20 px-1 rounded text-amber-300">API_NAVAJASUIZA</code>.</p>
              </div>
            </div>
            <div v-if="updateError" class="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-fade-in">❌ {{ updateError }}</div>
            <Transition name="slide"><div v-if="updateSuccess" class="px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm animate-fade-in flex items-center gap-2">✅ {{ updateSuccess }}</div></Transition>
            <button type="submit" :disabled="!updateForm.material_id.trim() || !updateForm.new_price || updating"
              class="w-full py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-amber-500/20 text-sm flex items-center justify-center gap-2">
              <svg v-if="updating" class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
              {{ updating ? 'Actualizando...' : '💰 Actualizar Precio' }}
            </button>
          </form>
        </div>
      </div>

      <!-- ================================ -->
      <!-- TAB 3: Consultar Q              -->
      <!-- ================================ -->
      <div v-if="activeTab === 'quotation'" class="animate-fade-in">
        <div class="glass rounded-2xl p-6">
          <h2 class="text-white font-semibold mb-1 flex items-center gap-2">
            <span class="text-lg">📋</span> Consultar Presupuesto
          </h2>
          <p class="text-sm text-slate-400 mb-5">Busca un presupuesto por su número para ver cabecera y desglose de posiciones.</p>

          <!-- Search bar -->
          <div class="flex gap-3 mb-6">
            <div class="flex-1 relative">
              <input v-model="qNumber" type="text" placeholder="Número (ej: Q230001)" @keyup.enter="queryQuotation"
                class="w-full px-4 py-3 pl-11 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 font-mono focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400/50 transition-all duration-300" />
              <svg class="w-5 h-5 text-slate-500 absolute left-3.5 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <button @click="queryQuotation" :disabled="!qNumber.trim() || queryingQ"
              class="px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-emerald-500/20 text-sm flex items-center gap-2">
              <svg v-if="queryingQ" class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
              {{ queryingQ ? 'Buscando...' : 'Buscar' }}
            </button>
          </div>

          <!-- Error -->
          <div v-if="qError" class="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm mb-4 animate-fade-in">
            ❌ {{ qError }}
          </div>

          <!-- Results: Master-Detail -->
          <Transition name="slide">
            <div v-if="quotationData" class="space-y-4 animate-fade-in">

              <!-- MASTER: Cabecera Card -->
              <div class="rounded-xl border border-slate-700/40 overflow-hidden">
                <div class="px-5 py-3 bg-slate-800/30 border-b border-slate-700/30 flex items-center justify-between">
                  <h3 class="text-sm font-semibold text-white flex items-center gap-2">
                    📋 Presupuesto {{ quotationData.cabecera.ID }}
                  </h3>
                  <span class="text-xs text-slate-500 font-mono">{{ quotationData.queried_by }}</span>
                </div>
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-0">
                  <!-- Cliente -->
                  <div class="px-5 py-4 border-b border-r border-slate-800/30">
                    <p class="text-xs text-slate-500 mb-1">Cliente</p>
                    <p class="text-sm font-semibold text-white truncate">{{ quotationData.cabecera.Cliente || '—' }}</p>
                  </div>
                  <!-- Estado -->
                  <div class="px-5 py-4 border-b border-r border-slate-800/30">
                    <p class="text-xs text-slate-500 mb-1">Estado</p>
                    <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs font-semibold"
                      :class="getStatusClass(quotationData.cabecera.EstadoInterno)">
                      {{ quotationData.cabecera.EstadoInterno || '—' }}
                    </span>
                  </div>
                  <!-- Fecha -->
                  <div class="px-5 py-4 border-b border-r border-slate-800/30">
                    <p class="text-xs text-slate-500 mb-1">Fecha</p>
                    <p class="text-sm text-white font-mono">{{ formatDate(quotationData.cabecera.Fecha) }}</p>
                  </div>
                  <!-- Total -->
                  <div class="px-5 py-4 border-b border-slate-800/30">
                    <p class="text-xs text-slate-500 mb-1">Total Neto</p>
                    <p class="text-lg font-bold text-emerald-400">€ {{ formatPrice(quotationData.cabecera.PrecioTotalNeto) }}</p>
                  </div>
                </div>
                <!-- Extra row: Moneda + Estado Impresion -->
                <div class="grid grid-cols-3 gap-0">
                  <div class="px-5 py-3 border-r border-slate-800/30">
                    <p class="text-xs text-slate-500 mb-0.5">Moneda</p>
                    <p class="text-sm text-slate-300 font-mono">{{ quotationData.cabecera.Moneda || '€' }}</p>
                  </div>
                  <div class="px-5 py-3 border-r border-slate-800/30">
                    <p class="text-xs text-slate-500 mb-0.5">Estado Impresión</p>
                    <p class="text-sm text-slate-300">{{ quotationData.cabecera.EstadoImpresion || '—' }}</p>
                  </div>
                  <div class="px-5 py-3">
                    <p class="text-xs text-slate-500 mb-0.5">Modalidad</p>
                    <p class="text-sm text-slate-300">{{ quotationData.cabecera.ModalidadImpresion || '—' }}</p>
                  </div>
                </div>
              </div>

              <!-- DETAIL: Items Table -->
              <div class="rounded-xl border border-slate-700/40 overflow-hidden">
                <div class="px-5 py-3 bg-slate-800/30 border-b border-slate-700/30 flex items-center justify-between">
                  <h3 class="text-sm font-semibold text-white flex items-center gap-2">
                    📦 Posiciones
                  </h3>
                  <span class="text-xs font-mono px-2 py-0.5 rounded-lg bg-slate-700/50 text-slate-400">
                    {{ quotationData.total_items }} línea{{ quotationData.total_items !== 1 ? 's' : '' }}
                  </span>
                </div>

                <div v-if="quotationData.items.length === 0" class="px-5 py-8 text-center text-slate-500 text-sm">
                  No hay posiciones para este presupuesto.
                </div>

                <table v-else class="w-full">
                  <thead>
                    <tr class="text-xs text-slate-500 uppercase tracking-wider border-b border-slate-800/30">
                      <th class="px-5 py-2.5 text-left font-medium">Pos</th>
                      <th class="px-5 py-2.5 text-left font-medium">Cant.</th>
                      <th class="px-5 py-2.5 text-left font-medium">Descripción</th>
                      <th class="px-5 py-2.5 text-center font-medium">Ancho × Alto</th>
                      <th class="px-5 py-2.5 text-right font-medium">P. Unitario</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-800/30">
                    <tr v-for="item in quotationData.items" :key="item.PosNr"
                      class="hover:bg-slate-700/10 transition-colors">
                      <td class="px-5 py-3 text-sm font-mono text-ns-accent">{{ item.PosNr }}</td>
                      <td class="px-5 py-3 text-sm text-white font-mono">{{ item.Cantidad || '—' }}</td>
                      <td class="px-5 py-3 text-sm text-slate-300 max-w-xs truncate">{{ item.Descripcion || '—' }}</td>
                      <td class="px-5 py-3 text-sm text-center text-slate-400 font-mono">
                        <span v-if="item.Ancho || item.Alto">{{ item.Ancho || '—' }} × {{ item.Alto || '—' }}</span>
                        <span v-else>—</span>
                      </td>
                      <td class="px-5 py-3 text-sm text-right font-mono text-emerald-400">
                        {{ item.PrecioUnitario != null ? '€ ' + Number(item.PrecioUnitario).toFixed(2) : '—' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '@/api/axios'

const activeTab = ref('query')
const tabs = [
  { id: 'query', label: 'Consultar Material', icon: '🔍' },
  { id: 'update', label: 'Actualizar Precio', icon: '💰' },
  { id: 'quotation', label: 'Consultar Q', icon: '📋' },
]

// === TAB 1: Material Query ===
const queryId = ref('')
const querying = ref(false)
const queryError = ref('')
const materialData = ref(null)

const materialFields = [
  { key: 'descripcion', label: 'Descripción', icon: '📝' },
  { key: 'descripcion2', label: 'Descripción 2', icon: '📄' },
  { key: 'grupo', label: 'Grupo', icon: '🏷️' },
  { key: 'unidad', label: 'Unidad', icon: '📏' },
  { key: 'precio_venta', label: 'Precio Venta', icon: '💶', class: 'text-emerald-400', format: 'price' },
  { key: 'precio_compra', label: 'Precio Compra', icon: '🏷️', class: 'text-amber-400', format: 'price' },
  { key: 'proveedor', label: 'Proveedor', icon: '🏭' },
  { key: 'ref_proveedor', label: 'Ref. Proveedor', icon: '🔗' },
  { key: 'observaciones', label: 'Observaciones', icon: '💬' },
  { key: 'bloqueado', label: 'Bloqueado', icon: '🔒', format: 'boolean' },
]

function formatValue(val, field) {
  if (val === null || val === undefined || val === '') return '—'
  if (field.format === 'price') return `€ ${Number(val).toFixed(2)}`
  if (field.format === 'boolean') return val ? '🔴 Sí' : '🟢 No'
  return String(val)
}

async function queryMaterial() {
  if (!queryId.value.trim() || querying.value) return
  querying.value = true
  queryError.value = ''
  materialData.value = null
  try {
    const { data } = await api.get(`/klaes/material/${encodeURIComponent(queryId.value.trim())}/`)
    materialData.value = { ...data.material, _queried_by: data.queried_by }
  } catch (err) {
    queryError.value = err.response?.data?.detail || 'Error al consultar la base de datos Klaes.'
  } finally {
    querying.value = false
  }
}

// === TAB 2: Price Update ===
const updateForm = reactive({ material_id: '', new_price: '' })
const updating = ref(false)
const updateError = ref('')
const updateSuccess = ref('')

async function updatePrice() {
  if (!updateForm.material_id.trim() || !updateForm.new_price || updating.value) return
  updating.value = true
  updateError.value = ''
  updateSuccess.value = ''
  try {
    const { data } = await api.put('/klaes/price/', {
      material_id: updateForm.material_id.trim(),
      new_price: parseFloat(updateForm.new_price),
    })
    updateSuccess.value = data.detail
    updateForm.material_id = ''
    updateForm.new_price = ''
  } catch (err) {
    updateError.value = err.response?.data?.detail || 'Error al actualizar el precio en Klaes.'
  } finally {
    updating.value = false
  }
}

// === TAB 3: Quotation Query ===
const qNumber = ref('')
const queryingQ = ref(false)
const qError = ref('')
const quotationData = ref(null)

function formatDate(val) {
  if (!val) return '—'
  try {
    return new Date(val).toLocaleDateString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit' })
  } catch {
    return String(val)
  }
}

function formatPrice(val) {
  if (val === null || val === undefined) return '—'
  return Number(val).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getStatusClass(status) {
  if (!status) return 'bg-slate-700/50 text-slate-400'
  const s = String(status).toLowerCase()
  if (s.includes('offen') || s.includes('abiert')) return 'bg-amber-500/15 text-amber-400'
  if (s.includes('bestellt') || s.includes('confirm') || s.includes('acept')) return 'bg-emerald-500/15 text-emerald-400'
  if (s.includes('storno') || s.includes('cancel')) return 'bg-red-500/15 text-red-400'
  return 'bg-slate-700/50 text-slate-300'
}

async function queryQuotation() {
  if (!qNumber.value.trim() || queryingQ.value) return
  queryingQ.value = true
  qError.value = ''
  quotationData.value = null
  try {
    const { data } = await api.get(`/klaes/quotation/${encodeURIComponent(qNumber.value.trim())}/`)
    quotationData.value = data
  } catch (err) {
    qError.value = err.response?.data?.detail || 'Presupuesto no encontrado.'
  } finally {
    queryingQ.value = false
  }
}
</script>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: all 0.3s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
