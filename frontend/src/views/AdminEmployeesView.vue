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
              <p class="text-xs text-slate-400 -mt-0.5">Panel Administrativo</p>
            </div>
          </div>
          <button
            @click="openCreateModal"
            class="flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-white bg-gradient-to-r from-ns-accent to-indigo-600 hover:from-ns-accent-light hover:to-indigo-500 transition-all duration-300 shadow-lg shadow-ns-accent/20 hover:shadow-ns-accent/40 hover:scale-[1.02] active:scale-[0.98] text-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Añadir Empleado
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading -->
      <div v-if="loadingList" class="flex items-center justify-center py-20">
        <svg class="animate-spin h-8 w-8 text-ns-accent" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>

      <!-- Empty state -->
      <div v-else-if="employees.length === 0" class="text-center py-20 animate-fade-in">
        <svg class="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <h3 class="text-lg text-slate-400 mb-2">No hay empleados registrados</h3>
        <p class="text-sm text-slate-500">Pulsa "Añadir Empleado" para dar de alta al primer usuario</p>
      </div>

      <!-- Employees Table -->
      <div v-else class="glass rounded-2xl overflow-hidden animate-fade-in">
        <!-- Table Header Info -->
        <div class="px-6 py-4 border-b border-slate-700/50 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-slate-300">{{ employees.length }} empleado{{ employees.length !== 1 ? 's' : '' }}</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-slate-500">
            <span class="w-2 h-2 rounded-full bg-ns-success animate-pulse"></span>
            Datos en tiempo real
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-700/50">
                <th class="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-400 bg-slate-800/30">ID</th>
                <th class="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-400 bg-slate-800/30">Nombre Completo</th>
                <th class="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-400 bg-slate-800/30">Email</th>
                <th class="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-400 bg-slate-800/30">Contraseña</th>
                <th class="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-400 bg-slate-800/30">Rol</th>
                <th class="px-6 py-3.5 text-center text-xs font-semibold uppercase tracking-wider text-slate-400 bg-slate-800/30">Acciones</th>
              </tr>
            </thead>
            <TransitionGroup name="table-row" tag="tbody">
              <tr
                v-for="emp in employees"
                :key="emp.id"
                class="border-b border-slate-800/50 hover:bg-slate-700/20 transition-colors duration-200 group"
              >
                <!-- ID -->
                <td class="px-6 py-4">
                  <span class="text-xs font-mono text-ns-accent bg-ns-accent/10 px-2 py-1 rounded-lg">{{ emp.empleado_id }}</span>
                </td>
                <!-- Name -->
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                      {{ getInitials(emp) }}
                    </div>
                    <div>
                      <p class="text-sm font-medium text-white">{{ emp.full_name }}</p>
                      <p class="text-xs text-slate-500">{{ emp.departamento || 'Sin departamento' }}</p>
                    </div>
                  </div>
                </td>
                <!-- Email -->
                <td class="px-6 py-4">
                  <span class="text-sm text-slate-300">{{ emp.email }}</span>
                </td>
                <!-- Password -->
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-mono" :class="passwordVisible[emp.id] ? 'text-emerald-400' : 'text-slate-500'">
                      {{ passwordVisible[emp.id] ? (emp.readable_password || '—') : '••••••••' }}
                    </span>
                    <button
                      @click="togglePassword(emp.id)"
                      class="text-slate-500 hover:text-slate-300 transition-colors p-1"
                      :title="passwordVisible[emp.id] ? 'Ocultar' : 'Mostrar'"
                    >
                      <svg v-if="!passwordVisible[emp.id]" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    </button>
                  </div>
                </td>
                <!-- Role -->
                <td class="px-6 py-4">
                  <span
                    class="text-xs font-medium px-2.5 py-1 rounded-lg"
                    :class="roleBadgeClass(emp.role)"
                  >{{ roleLabels[emp.role] || emp.role }}</span>
                </td>
                <!-- Actions -->
                <td class="px-6 py-4 text-center">
                  <div class="flex items-center justify-center gap-2 opacity-60 group-hover:opacity-100 transition-opacity">
                    <button
                      @click="openEditModal(emp)"
                      class="p-2 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 hover:text-amber-300 transition-all duration-200"
                      title="Editar"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      @click="confirmDelete(emp)"
                      class="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 transition-all duration-200"
                      title="Eliminar"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </TransitionGroup>
          </table>
        </div>
      </div>

      <!-- Toast Notification -->
      <Transition name="toast">
        <div v-if="toast.show" class="fixed bottom-6 right-6 z-50 max-w-sm">
          <div
            class="px-5 py-3 rounded-xl shadow-2xl border backdrop-blur-lg flex items-center gap-3"
            :class="toast.type === 'success'
              ? 'bg-emerald-900/80 border-emerald-500/30 text-emerald-300'
              : 'bg-red-900/80 border-red-500/30 text-red-300'"
          >
            <span v-if="toast.type === 'success'">✅</span>
            <span v-else>❌</span>
            <span class="text-sm">{{ toast.message }}</span>
          </div>
        </div>
      </Transition>
    </main>

    <!-- ============================================ -->
    <!-- MODAL: Create / Edit Employee              -->
    <!-- ============================================ -->
    <Transition name="modal">
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="closeModal">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
        <div class="relative glass rounded-2xl w-full max-w-lg p-6 sm:p-8 animate-fade-in-up border border-slate-600/30">
          <!-- Modal Header -->
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold text-white">
              {{ isEditing ? '✏️ Editar Empleado' : '➕ Nuevo Empleado' }}
            </h3>
            <button @click="closeModal" class="text-slate-400 hover:text-white transition-colors p-1">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Modal Form -->
          <form @submit.prevent="submitForm" class="space-y-4">
            <!-- Name row -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-400 mb-1">Nombre</label>
                <input v-model="form.first_name" type="text" required placeholder="Juan"
                  class="w-full px-3.5 py-2.5 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300 text-sm" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-400 mb-1">Apellidos</label>
                <input v-model="form.last_name" type="text" required placeholder="García López"
                  class="w-full px-3.5 py-2.5 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300 text-sm" />
              </div>
            </div>

            <!-- Email -->
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Email Corporativo</label>
              <input v-model="form.email" type="email" required placeholder="usuario@acristalia.com"
                class="w-full px-3.5 py-2.5 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300 text-sm" />
            </div>

            <!-- Password -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-400 mb-1">
                  Contraseña {{ isEditing ? '(dejar vacío = sin cambios)' : '' }}
                </label>
                <input v-model="form.password" type="text" :required="!isEditing" minlength="6" placeholder="Mín. 6 caracteres" autocomplete="off"
                  class="w-full px-3.5 py-2.5 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300 text-sm font-mono" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-400 mb-1">Confirmar Contraseña</label>
                <input v-model="confirmPassword" type="text" :required="!isEditing && !!form.password" minlength="6" placeholder="Repetir"
                  class="w-full px-3.5 py-2.5 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300 text-sm font-mono"
                  :class="{ 'border-red-500/50': confirmPassword && form.password !== confirmPassword }" />
                <p v-if="confirmPassword && form.password !== confirmPassword" class="text-red-400 text-xs mt-1">No coinciden</p>
              </div>
            </div>

            <!-- Role & Department -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-400 mb-1">Rol</label>
                <select v-model="form.role"
                  class="w-full px-3.5 py-2.5 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300 text-sm appearance-none">
                  <option value="empleado">👤 Empleado</option>
                  <option value="admin">⚙️ Administrador</option>
                  <option value="superadmin">🔑 SuperAdmin</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-400 mb-1">Departamento</label>
                <input v-model="form.departamento" type="text" placeholder="Ventas, IT..."
                  class="w-full px-3.5 py-2.5 rounded-xl bg-ns-darker/80 border border-slate-600/50 text-white placeholder-slate-500 focus:outline-none focus:border-ns-accent focus:ring-1 focus:ring-ns-accent/50 transition-all duration-300 text-sm" />
              </div>
            </div>

            <!-- Error -->
            <p v-if="formError" class="text-red-400 text-sm bg-red-500/10 rounded-lg px-3 py-2 border border-red-500/20">{{ formError }}</p>

            <!-- Submit -->
            <div class="flex gap-3 pt-2">
              <button type="button" @click="closeModal"
                class="flex-1 py-2.5 rounded-xl text-sm font-medium text-slate-300 bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/30 transition-all duration-200">
                Cancelar
              </button>
              <button type="submit" :disabled="submitting || !isFormValid"
                class="flex-1 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-ns-accent to-indigo-600 hover:from-ns-accent-light hover:to-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300 shadow-lg shadow-ns-accent/20">
                <span v-if="submitting" class="flex items-center justify-center gap-2">
                  <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  {{ isEditing ? 'Guardando...' : 'Creando...' }}
                </span>
                <span v-else>{{ isEditing ? 'Guardar Cambios' : 'Crear y Enviar Email' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ============================================ -->
    <!-- MODAL: Delete Confirmation                  -->
    <!-- ============================================ -->
    <Transition name="modal">
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showDeleteModal = false">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
        <div class="relative glass rounded-2xl w-full max-w-sm p-6 text-center animate-fade-in-up border border-red-500/20">
          <div class="w-14 h-14 rounded-full bg-red-500/15 flex items-center justify-center mx-auto mb-4">
            <svg class="w-7 h-7 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-white mb-2">¿Eliminar empleado?</h3>
          <p class="text-sm text-slate-400 mb-5">
            Estás a punto de eliminar permanentemente a
            <span class="text-white font-medium">{{ deleteTarget?.full_name }}</span>.
            Esta acción no se puede deshacer.
          </p>
          <div class="flex gap-3">
            <button @click="showDeleteModal = false"
              class="flex-1 py-2.5 rounded-xl text-sm font-medium text-slate-300 bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600/30 transition-all duration-200">
              Cancelar
            </button>
            <button @click="executeDelete" :disabled="deleting"
              class="flex-1 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-red-500 to-red-700 hover:from-red-400 hover:to-red-600 disabled:opacity-40 transition-all duration-300 shadow-lg shadow-red-500/20">
              {{ deleting ? 'Eliminando...' : '🗑️ Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import api from '@/api/axios'

// State
const employees = ref([])
const loadingList = ref(true)
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const deleting = ref(false)
const deleteTarget = ref(null)
const formError = ref('')
const confirmPassword = ref('')
const passwordVisible = reactive({})

const toast = reactive({ show: false, message: '', type: 'success' })

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  role: 'empleado',
  departamento: '',
})

// Data
const roleLabels = {
  superadmin: '🔑 SuperAdmin',
  admin: '⚙️ Admin',
  empleado: '👤 Empleado',
}

// Computed
const isFormValid = computed(() => {
  const f = form.value
  const hasBasicInfo = f.first_name.trim() && f.last_name.trim() && f.email.trim()

  if (isEditing.value) {
    // Password optional on edit, but if provided must match
    if (f.password && f.password !== confirmPassword.value) return false
    return hasBasicInfo
  }

  // Create: password required + must match
  return hasBasicInfo && f.password.length >= 6 && f.password === confirmPassword.value
})

// Methods
function getInitials(emp) {
  const f = (emp.first_name || '')[0] || ''
  const l = (emp.last_name || '')[0] || ''
  return (f + l).toUpperCase() || '?'
}

function roleBadgeClass(role) {
  const map = {
    superadmin: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
    admin: 'bg-sky-500/15 text-sky-400 border border-sky-500/30',
    empleado: 'bg-slate-500/15 text-slate-400 border border-slate-500/30',
  }
  return map[role] || map.empleado
}

function togglePassword(id) {
  passwordVisible[id] = !passwordVisible[id]
}

function showToast(message, type = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3500)
}

async function fetchEmployees() {
  loadingList.value = true
  try {
    const { data } = await api.get('/admin/employees/')
    employees.value = data
  } catch (err) {
    showToast('Error al cargar empleados', 'error')
  } finally {
    loadingList.value = false
  }
}

function resetForm() {
  form.value = { first_name: '', last_name: '', email: '', password: '', role: 'empleado', departamento: '' }
  confirmPassword.value = ''
  formError.value = ''
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  resetForm()
  showModal.value = true
}

function openEditModal(emp) {
  isEditing.value = true
  editingId.value = emp.id
  form.value = {
    first_name: emp.first_name,
    last_name: emp.last_name,
    email: emp.email,
    password: '',
    role: emp.role,
    departamento: emp.departamento || '',
  }
  confirmPassword.value = ''
  formError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function confirmDelete(emp) {
  deleteTarget.value = emp
  showDeleteModal.value = true
}

async function submitForm() {
  if (!isFormValid.value || submitting.value) return
  submitting.value = true
  formError.value = ''

  try {
    if (isEditing.value) {
      // PATCH update
      const payload = { ...form.value }
      if (!payload.password) delete payload.password
      delete payload.confirmPassword

      await api.patch(`/admin/employees/${editingId.value}/`, payload)
      showToast('Empleado actualizado correctamente')
    } else {
      // POST create
      const { data } = await api.post('/admin/employees/', form.value)
      if (!data.email_sent) {
        showToast('Empleado creado. Email NO enviado — comunica credenciales manualmente', 'error')
      } else {
        showToast('Empleado creado y email enviado')
      }
    }
    closeModal()
    await fetchEmployees()
  } catch (err) {
    const detail = err.response?.data
    if (detail?.email) {
      formError.value = Array.isArray(detail.email) ? detail.email[0] : detail.email
    } else if (detail?.detail) {
      formError.value = detail.detail
    } else if (typeof detail === 'object') {
      formError.value = Object.values(detail).flat().join(' ')
    } else {
      formError.value = 'Error al guardar. Inténtalo de nuevo.'
    }
  } finally {
    submitting.value = false
  }
}

async function executeDelete() {
  if (!deleteTarget.value || deleting.value) return
  deleting.value = true

  try {
    await api.delete(`/admin/employees/${deleteTarget.value.id}/`)
    // Remove from local state (smooth animation)
    employees.value = employees.value.filter(e => e.id !== deleteTarget.value.id)
    showToast(`"${deleteTarget.value.full_name}" eliminado`)
    showDeleteModal.value = false
  } catch (err) {
    showToast('Error al eliminar empleado', 'error')
  } finally {
    deleting.value = false
  }
}

onMounted(fetchEmployees)
</script>

<style scoped>
/* Table row transitions */
.table-row-enter-active,
.table-row-leave-active {
  transition: all 0.4s ease;
}
.table-row-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}
.table-row-leave-to {
  opacity: 0;
  transform: translateX(20px);
  max-height: 0;
}

/* Modal transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95) translateY(10px);
}

/* Toast transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.95);
}

select option {
  background-color: #0f172a;
  color: #e2e8f0;
}
</style>
