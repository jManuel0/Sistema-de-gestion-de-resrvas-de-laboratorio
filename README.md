## Sistema de Gestión de Reservas de Laboratorios (Django)

Proyecto: **`reservas_laboratorio_juanmanuel`**  
App principal: **`reservas_juanmanuel`**

### Estructura

- `reservas_laboratorio_juanmanuel/`: configuración del proyecto (settings/urls/asgi/wsgi)
- `reservas_juanmanuel/`: app de reservas (modelo, vistas CBV, urls, formularios)
- `templates/`
  - `base.html`: plantilla base (Bootstrap)
  - `registration/login.html`: login
  - `reservas/`: pantallas del CRUD, filtros, estado y estadísticas
- `db.sqlite3`: base de datos local
- `requirements.txt`: dependencias

### Entorno virtual (Windows + bash)

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Correr el proyecto

```bash
source .venv/Scripts/activate
python manage.py migrate
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

### Roles (Docente / Administrador)

- Se crean automáticamente los grupos **`Docente`** y **`Administrador`** al ejecutar `migrate` (signal `post_migrate`).
- Recomendación para pruebas:
  - Crea un superusuario (admin Django):

```bash
source .venv/Scripts/activate
python manage.py createsuperuser
```

- Asigna usuarios a grupos desde `http://127.0.0.1:8000/admin/` → **Users** → **Groups**.

### Reglas del sistema

- **Docente**:
  - Crea reservas (estado inicial: *Pendiente*)
  - Solo puede **editar/eliminar** si su reserva está **Pendiente**
- **Administrador**:
  - Ve todas las reservas
  - Puede **aprobar o rechazar** cualquier reserva
- **Validación de choques**:
  - En el mismo laboratorio y fecha, no permite intervalos solapados.


### Despliegue en Vercel

El proyecto incluye configuracion para Vercel:

- `vercel.json`: ejecuta migraciones y `collectstatic` durante el build.
- `.python-version`: fija Python 3.12 para Vercel.
- `.env.example`: lista las variables necesarias.
- `settings.py`: usa SQLite en local y `DATABASE_URL` en produccion.

Variables requeridas en Vercel:

```text
DJANGO_SECRET_KEY=una-clave-segura
DEBUG=False
DJANGO_ALLOWED_HOSTS=.vercel.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.vercel.app
DATABASE_URL=postgres://usuario:password@host:5432/base_de_datos
```

Importante: para produccion usa Postgres u otra base externa. SQLite solo es para desarrollo local.
