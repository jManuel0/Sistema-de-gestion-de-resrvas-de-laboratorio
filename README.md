## Sistema de Gestion de Reservas de Laboratorios (Django)

Proyecto: **`reservas_laboratorio_juanmanuel`**  
App principal: **`reservas_juanmanuel`**

### Estructura

- `reservas_laboratorio_juanmanuel/`: configuracion del proyecto (`settings`, `urls`, `asgi`, `wsgi`)
- `reservas_juanmanuel/`: app de reservas (modelo, vistas, urls, formularios)
- `templates/`
  - `base.html`: plantilla base
  - `registration/login.html`: login
  - `registration/register.html`: registro
  - `reservas_juanmanuel/`: pantallas del CRUD, filtros y estadisticas
- `db.sqlite3`: base de datos local
- `requirements.txt`: dependencias

### Entorno virtual

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Correr el proyecto

```bash
source .venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

### Usuarios de prueba

Estas credenciales funcionan usando el archivo `db.sqlite3` incluido en el proyecto.  
Si se crea una base nueva desde cero, estos usuarios no existiran hasta volver a registrarlos.

- `Administrador`
  - Usuario: `carlos2`
  - Clave: `1234Ct6789`
- `Docente`
  - Usuario: `Juan_0729`
  - Clave: `Juan3173145521`
- `Estudiante`
  - Usuario: `felipe07`
  - Clave: `miguelfelipe1`

### Roles

- Se manejan los grupos `Docente`, `Administrador` y `Estudiante`.
- Los usuarios pueden crearse desde registro o desde el panel `/admin/`.
- Si usas una base nueva, debes volver a crear los usuarios o copiar el `db.sqlite3`.

### Reglas del sistema

- `Docente`
  - Crea reservas
  - Solo puede editar o eliminar sus reservas si estan en estado `Pendiente`
- `Administrador`
  - Ve todas las reservas
  - Puede aprobar o rechazar cualquier reserva pendiente
- `Estudiante`
  - Puede iniciar sesion y consultar las reservas aprobadas
- `Validacion de choques`
  - En el mismo laboratorio y fecha no se permiten horarios solapados

### Despliegue en Vercel

El proyecto incluye configuracion para Vercel:

- `vercel.json`: ejecuta migraciones y `collectstatic` durante el build
- `.python-version`: fija Python para despliegue
- `.env.example`: lista las variables necesarias
- `settings.py`: usa SQLite en local y `DATABASE_URL` en produccion

Variables requeridas en Vercel:

```text
DJANGO_SECRET_KEY=una-clave-segura
DEBUG=False
DJANGO_ALLOWED_HOSTS=.vercel.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.vercel.app
DATABASE_URL=postgres://usuario:password@host:5432/base_de_datos
```

Importante: para produccion usa Postgres u otra base externa. SQLite solo es para desarrollo local.
