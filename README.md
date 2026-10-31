<div align="center">

# 📅 ReservaYa — Gestor de Reservas

### *Reserva pistas, salas y recursos en un par de clics* ✨

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.x-092E20?logo=django&logoColor=white)
![License](https://img.shields.io/badge/Licencia-MIT-green)
![Tests](https://img.shields.io/badge/tests-9%20passing-brightgreen)

**🎓 Proyecto 4 · Django · Máster Full Stack — *Conquer Blocks***

</div>

---

## 🎯 ¿Qué es?

**ReservaYa** es una aplicación web hecha con **Django** para reservar *recursos* (pistas deportivas 🎾⚽, salas de reuniones 💼…) con un **calendario interactivo** de disponibilidad.

## 🌟 Funcionalidades

| | Característica | Detalle |
|---|---|---|
| 📆 | **Calendario de disponibilidad** | Vista mensual con colores *(🟢 libre · 🟡 casi lleno · 🔴 completo)* y turnos por día cargados con **JavaScript (fetch)** sin recargar la página |
| 🚫 | **Sin solapamientos** | Validación en servidor dentro de una **transacción** con bloqueo del recurso, para evitar *dobles reservas* |
| 🔁 | **Reservas recurrentes** | Repite una reserva hasta **9 semanas** más. Es *todo o nada*: si una fecha falla, no se crea ninguna |
| ❌ | **Cancelación** | Cancela una reserva o **toda la serie futura** |
| 📧 | **Notificaciones** | Emails de confirmación y cancelación *(por consola en desarrollo)* |
| 🛠️ | **Panel de gestión** | Estadísticas, filtro por recurso y cancelación de reservas, solo para **staff** |
| 🔐 | **Usuarios** | Registro, login y logout |

## 🧱 Modelos

- 🏟️ **Resource** — nombre, descripción, capacidad, emoji y duración del turno
- 🕘 **Availability** — horario de apertura por *día de la semana* y recurso
- 🎟️ **Booking** — reserva con inicio/fin, estado y `recurrence_id` para las series
- 👤 **User** — el usuario integrado de Django

## 🚀 Puesta en marcha local

```bash
cd booking-system-django

# 1️⃣ Entorno virtual e instalación
python -m venv venv
venv\Scripts\activate        # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# 2️⃣ Base de datos y datos de ejemplo
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser

# 3️⃣ ¡A rodar!
python manage.py runserver
```

Abre 👉 **http://127.0.0.1:8000/** y gestiona recursos y horarios desde **/admin/** 🛠️

## 🧪 Tests

```bash
python manage.py test
```

Cubren *solapamientos*, *series recurrentes*, *horarios*, *cancelaciones* y *permisos* ✅

## 🐍 Despliegue gratuito en PythonAnywhere

Usa SQLite (sin Docker) y los estáticos los sirve **WhiteNoise**, así que no hace falta configurar *Static files* en la pestaña Web.

1. Crea una cuenta *Beginner* en [pythonanywhere.com](https://www.pythonanywhere.com) y abre una consola **Bash**.
2. Clona el repositorio y crea el entorno (Python **3.12 o superior**, requerido por Django 6):
   ```bash
   git clone https://github.com/valentinoaguiarhirales1-art/Proyecto-GR-TAREA.git
   mkvirtualenv --python=python3.13 myenv
   cd Proyecto-GR-TAREA/booking-system-django && pip install -r requirements.txt
   ```
3. Prepara la base de datos y el administrador:
   ```bash
   export DEBUG=0 SECRET_KEY=cualquier-valor ALLOWED_HOSTS='*'
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   python manage.py seed_demo   # opcional: recursos de ejemplo
   ```
4. Pestaña **Web** → *Add a new web app* → *Manual configuration* → misma versión de Python. En **Virtualenv** pon `/home/TU_USUARIO/.virtualenvs/myenv`.
5. Abre el *WSGI configuration file*, borra todo y pega [pythonanywhere_wsgi.py](booking-system-django/pythonanywhere_wsgi.py) cambiando `TU_USUARIO` y `SECRET_KEY` (la ruta ya apunta a `Proyecto-GR-TAREA/booking-system-django`).
6. Pulsa **Reload** y abre `https://TU_USUARIO.pythonanywhere.com` desde cualquier navegador, también el del móvil 📱.

> 🔄 Para actualizar: `git pull`, `python manage.py migrate` y **Reload**. En la cuenta gratuita hay que pulsar *Run until 3 months from today* en la pestaña Web de vez en cuando para que no expire.

## ☁️ Despliegue alternativo en un droplet con Docker

Incluye **Docker Compose**, **PostgreSQL** y **Caddy** (HTTPS automático). Desde `booking-system-django/`:

```bash
cp .env.example .env        # edita dominio, SECRET_KEY y contraseñas (¡no lo subas a Git!)
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Apunta antes el registro DNS **A** de tu dominio a la IP del droplet y abre los puertos **80** y **443**. Las migraciones y los estáticos se aplican al arrancar.

## 🗂️ Estructura

```
booking-system-django/
├── config/      ⚙️ Ajustes y URLs del proyecto
├── reservas/    📦 App: modelos, servicios (lógica de reservas), vistas, tests
└── templates/   🎨 Plantillas HTML
```

## 📄 Licencia

Distribuido bajo licencia **MIT** 💚 — consulta el archivo [LICENSE](LICENSE).

<div align="center">

*Hecho con 💜 y mucho ☕*

</div>
