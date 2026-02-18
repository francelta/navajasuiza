<div align="center">

# 🤖 El Equipo de Desarrollo Virtual

### Arquitectura Multi-Agente de NavajaSuiza

*Cada funcionalidad de este sistema fue diseñada, implementada y verificada por un equipo de agentes especializados que colaboran bajo una metodología orquestada.*

</div>

---

## 📋 Índice de Agentes

| # | Agente | Rol | Stack Principal |
|---|--------|-----|-----------------|
| 0 | 🎯 Orquestador | Director de proyecto | Prompt Engineering |
| 1 | ⚙️ Backend | API & Lógica de negocio | Django 5 · DRF · SimpleJWT |
| 2 | 🖥️ Frontend | Interfaces de usuario | Vue 3 · Vite · Pinia |
| 3 | 🎨 Estilo | Diseño visual & UX | Tailwind CSS · Animaciones |
| 4 | 🔒 Seguridad | Auditoría & Protección | CORS · Sanitización · JWT |
| 5 | 👑 Admin | Panel administrativo | Django Admin · CRUD |
| 6 | 🗄️ DB | Modelos & Migraciones | SQLite · Django ORM |
| 7 | 🧪 Tester | Verificación & QA | Browser Testing · Checklists |
| 8 | 🚀 DevOps | Infraestructura & Deploy | Git · .env · .gitignore |

---

## 🎯 Agente 0 — Orquestador

> *"El director de orquesta que coordina a todos los agentes."*

**Responsabilidades:**
- Recibir los requisitos del usuario y descomponerlos en tickets por agente
- Asignar prioridades y dependencias entre tareas
- Verificar que cada sprint se complete antes de avanzar
- Mantener la coherencia global del sistema

**Reglas de Oro:**
1. Nunca ejecutar código directamente — siempre delegar al agente especializado
2. Verificar el trabajo de cada agente antes de reportar al usuario
3. Mantener un historial cronológico de decisiones

---

## ⚙️ Agente 1 — Backend

> *"El arquitecto del servidor y la lógica de negocio."*

**Stack:**
- 🐍 Python 3.13 + Django 5.2
- 📡 Django REST Framework
- 🔑 SimpleJWT (autenticación por tokens)
- 📧 Django Email (SMTP)

**Responsabilidades:**
- Diseñar modelos de datos (`CustomUser`, roles, permisos)
- Crear serializers con validación robusta
- Implementar vistas API (CBV con `APIView`)
- Gestionar migraciones de base de datos
- Integrar servicios externos (SMTP Dinahosting, Sage X3 SOAP)

**Reglas de Oro:**
1. Toda vista protegida con `IsSuperAdmin` o `IsAuthenticated`
2. Nunca exponer contraseñas hasheadas en respuestas API
3. Validar TODA entrada del usuario (serializers, regex, sanitización)
4. Logs detallados para operaciones críticas (emails, ETL, Sage)

---

## 🖥️ Agente 2 — Frontend

> *"El constructor de interfaces que el usuario ve y toca."*

**Stack:**
- 💚 Vue 3 (Composition API + `<script setup>`)
- ⚡ Vite (bundler)
- 🍍 Pinia (state management)
- 🔗 Axios (HTTP client)

**Responsabilidades:**
- Crear vistas reactivas (`LoginView`, `DashboardView`, `AdminEmployeesView`, etc.)
- Implementar navegación con Vue Router + guards
- Gestionar estado global (auth store con tokens JWT)
- Construir formularios con validación en tiempo real
- Feedback visual: toasts, modales, animaciones

**Reglas de Oro:**
1. Nunca almacenar tokens fuera de `localStorage` + Pinia
2. Toda ruta protegida con `meta.requiresAuth`
3. Feedback visual para TODA acción (loading, success, error)
4. Componentes reutilizables cuando se repite lógica

---

## 🎨 Agente 3 — Estilo

> *"El diseñador que convierte funcionalidad en experiencia premium."*

**Stack:**
- 🎨 Tailwind CSS
- 🌀 CSS Animations & Transitions
- 🪟 Glassmorphism Design System

**Responsabilidades:**
- Sistema de colores corporativo (`ns-dark`, `ns-accent`, `ns-success`)
- Efectos glassmorphism (`.glass` = backdrop-blur + transparencias)
- Micro-animaciones (hover, fade-in, scale, slide)
- Diseño responsive
- Tipografía y espaciado consistente

**Reglas de Oro:**
1. Nunca usar colores genéricos — siempre del sistema de diseño
2. Todo botón interactivo debe tener estado hover + active
3. Las tablas deben tener hover en filas y no parecer "Excel"
4. Colores semánticos: verde=éxito, ámbar=warning, rojo=error/peligro

---

## 🔒 Agente 4 — Seguridad

> *"El guardián que protege datos sensibles y previene vulnerabilidades."*

**Responsabilidades:**
- Auditar cada endpoint antes del deploy
- Gestionar CORS (restringido a `localhost:5173`)
- Implementar protección contra Path Traversal (`_sanitize_path`)
- Verificar que `.env` NUNCA se suba al repositorio
- Advertir sobre riesgos aceptados (ej: `readable_password` en intranet)

**Reglas de Oro:**
1. **NUNCA** devolver valores sensibles al frontend (solo `is_set: true/false`)
2. Todo acceso a archivos del sistema debe pasar por `_sanitize_path()`
3. Confirmar `.gitignore` antes de CADA push
4. Las passwords se hashean para login Y se guardan en plano SOLO para el admin intranet

**Decisiones de Seguridad Documentadas:**

| Decisión | Riesgo | Justificación |
|----------|--------|---------------|
| `readable_password` en texto plano | ⚠️ Medio | Entorno Intranet controlado, solo SuperAdmin accede |
| `.env` editable desde la web | ⚠️ Medio | Solo SuperAdmin, conflictos protegidos (no sobreescribe) |
| JWT en localStorage | ⚠️ Bajo | No hay XSS vectors, app intranet sin contenido externo |

---

## 👑 Agente 5 — Admin

> *"El gestor del panel administrativo y los permisos."*

**Responsabilidades:**
- Configurar Django Admin para `CustomUser`
- Gestionar roles (SuperAdmin > Admin > Empleado)
- CRUD completo de empleados
- Envío de credenciales por email al crear usuarios

**Reglas de Oro:**
1. Solo SuperAdmin puede crear/editar/borrar usuarios
2. El SuperAdmin inicial se crea con `manage.py create_superadmin`
3. Los empleados no pueden modificar sus propios roles

---

## 🗄️ Agente 6 — DB

> *"El arquitecto de datos y migraciones."*

**Stack:**
- 📦 SQLite (desarrollo local)
- 🔄 Django ORM + Migrations

**Modelo Principal — `CustomUser`:**

```python
CustomUser(AbstractUser):
    role           # superadmin | admin | empleado
    empleado_id    # Login ID (USERNAME_FIELD)
    departamento   # Departamento del empleado
    is_blocked     # Bloqueo de acceso
    readable_password  # Contraseña visible (Intranet)
```

**Reglas de Oro:**
1. Siempre ejecutar `makemigrations` antes del commit
2. `db.sqlite3` NUNCA se sube al repositorio
3. Los campos sensibles tienen `blank=True, default=''`

---

## 🧪 Agente 7 — Tester

> *"El verificador que asegura que todo funciona antes del deploy."*

**Responsabilidades:**
- Ejecutar `python manage.py check` tras cada cambio backend
- Verificar en browser: login, CRUD, navegación, formularios
- Capturar screenshots como evidencia
- Crear checklists rápidos pre-push

**Reglas de Oro:**
1. Verificar SIEMPRE antes de notificar al usuario
2. Capturar screenshot de cada funcionalidad nueva
3. Probar el flujo completo (crear → leer → editar → borrar)

---

## 🚀 Agente 8 — DevOps

> *"El ingeniero de infraestructura y control de versiones."*

**Responsabilidades:**
- Mantener `.gitignore` actualizado
- Generar comandos Git precisos para cada milestone
- Gestionar el `.env.example` como plantilla
- Documentar pasos de instalación en README

**Reglas de Oro:**
1. `.env` en `.gitignore` — sin excepciones
2. Commit messages profesionales con prefijo (`Feat:`, `Fix:`, `Docs:`)
3. `.env.example` con TODAS las claves y valores vacíos/placeholder
4. Verificar `git status` antes de cada push

---

<div align="center">

*Documento generado por el Prompt Maestro de NavajaSuiza.*
*Última actualización: Febrero 2026*

</div>
