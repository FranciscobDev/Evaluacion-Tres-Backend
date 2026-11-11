# 🦷 CheckDent — Sistema de Gestión Clínica Odontológica

Aplicación web desarrollada en **Python / Django** para la administración de prestaciones dentales, disponibilidad de agendas odontológicas y coordinación de pacientes en recepción.

---

## ⚙️ 1. Flujo Principal del Sistema

1. **Portal Público (Pacientes):**
   * Los pacientes no requieren cuenta ni inicio de sesión.
   * Pueden explorar el **Catálogo de Tratamientos** con sus valores, duración y fotografías clínicas, además de consultar la sección de **Contacto y Ubicación** para comunicarse directamente con recepción vía WhatsApp o teléfono.
2. **Portal de Odontólogos:**
   * Los dentistas inician sesión para publicar sus bloques de horarios disponibles (de forma individual o por jornada completa), revisar los pacientes citados y registrar notas clínicas de atención.
3. **Panel de Recepción:**
   * El personal de recepción visualiza las horas disponibles publicadas por los odontólogos, asigna citas validando el RUT chileno (Módulo 11), gestiona estados (*Agendada, Confirmada, En Atención, Realizada, Cancelada*) y contacta a los pacientes por WhatsApp en un clic.
4. **Administración (`Django Admin`):**
   * Exclusivo para el **Administrador Clínico**, quien gestiona el alta de nuevos odontólogos, recepcionistas y parámetros generales en `/admin/`.

---

## 🚀 2. Instalación y Ejecución

1. **Activar el entorno virtual:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Ejecutar migraciones y cargar datos iniciales:**
   ```powershell
   python manage.py migrate
   python manage.py poblar_datos
   ```

4. **Ejecutar pruebas y levantar el servidor:**
   ```powershell
   python manage.py test
   python manage.py runserver
   ```
   Accede en el navegador a `http://127.0.0.1:8000/`.

---

## 🔑 3. Credenciales del Personal Clínico

| Rol en el Sistema | Usuario | Contraseña | Acceso Principal |
| :--- | :--- | :--- | :--- |
| **Administrador Clínico** | `admin` | `admin123` | Panel Recepción, CRUD Tratamientos y Django Admin (`/admin/`) |
| **Odontólogo (Ortodoncia)** | `dr.mauricio` | `dentista123` | Mi Agenda, publicación de bloques horarios y notas clínicas |
| **Odontólogo (Endodoncia)** | `dr.ismael` | `dentista123` | Mi Agenda, publicación de bloques horarios y notas clínicas |
| **Odontólogo (Odontopediatría)** | `dr.francisco` | `dentista123` | Mi Agenda, publicación de bloques horarios y notas clínicas |
| **Recepcionista** | `carla.recepcion` | `recepcion123` | Panel de Citas, asignación de pacientes y contacto WhatsApp |

---

## 🤖 4. Bitácora de Prompts de Inteligencia Artificial (Criterio 2.1.4)

### Prompt 1: Arquitectura y Modelado ORM Relacional
* **Prompt Técnico utilizado:**
  > *"Necesito diseñar en Django 5/6 dos modelos relacionales para el catálogo clínico de CheckDent: `EspecialidadOdontologica` y `TratamientoOdontologico`. La relación debe ser ForeignKey con `on_delete=models.PROTECT` para evitar que eliminar una especialidad destruya tratamientos activos. Además, debe incluir validadores declarativos `MinValueValidator(0)` para arancel y cupos, estados cerrados mediante `choices`, soporte de imágenes `ImageField` con `upload_to='tratamientos/'` y control de baja lógica (`vigente=models.BooleanField(default=True)`)."*
* **Fundamento y Adaptación Crítica:**
  La IA propuso la estructura del modelo, la generación de slug automático con `slugify()` y la protección referencial. Se adaptó agregando el método `save()` para sanitizar códigos únicos en mayúsculas (`strip().upper()`) y asegurar que los aranceles y cupos no acepten números negativos.

### Prompt 2: Seguridad, Roles y Protección de Rutas Administrativas
* **Prompt Técnico utilizado:**
  > *"¿Cómo implementar un control de acceso por roles en Django que diferencie entre Odontólogos, Recepcionistas y Administrador, asegurando que solo el Administrador pueda acceder a `/admin/` y registrar funcionarios, mientras que dentistas y recepcionistas operen únicamente en sus paneles mediante `@login_required` y `@user_passes_test`?"*
* **Fundamento y Adaptación Crítica:**
  La IA recomendó extender `User` mediante un modelo `Perfil` con relación `OneToOneField`, sobrescribir `admin.site.has_permission` para restringir el acceso al Django Admin exclusivamente a superusuarios o rol `'administrador'`, y proteger las vistas de catálogo y agenda con decoradores `@user_passes_test`. Se resolvió además el conflicto de integridad `UNIQUE constraint` en el admin al añadir usuarios con `Inline`.

### Prompt 3: Manejo de Sesiones HTTP (`request.session`) y Context Processor
* **Prompt Técnico utilizado:**
  > *"Requiero implementar una colección transitoria en sesión HTTP (`request.session['presupuesto_dental']`) para que el equipo clínico pueda armar un plan de cotización con múltiples prestaciones, verificar cupos disponibles, modificar cantidades, calcular un recargo del 10% por insumos de bioseguridad, e inyectar globalmente el contador de ítems en el Navbar mediante un Context Processor sin saturar la vista pública del paciente."*
* **Fundamento y Adaptación Crítica:**
  Se implementó la colección basada en diccionarios serializables en sesión con claves por ID de tratamiento. El `context_processor` inyecta de forma segura el conteo total verificando `hasattr(req, 'session')`, permitiendo al personal clínico gestionar la cotización y emitir comprobantes imprimibles con folio único (`PRES-YYYYMMDD-HHMMSS`).
