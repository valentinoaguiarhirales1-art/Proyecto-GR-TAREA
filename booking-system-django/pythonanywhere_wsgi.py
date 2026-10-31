# Plantilla para el "WSGI configuration file" de PythonAnywhere (pestaña Web).
# Borra el contenido original, pega esto y cambia TU_USUARIO y la clave secreta.
import os
import sys

path = '/home/TU_USUARIO/Proyecto-GR-TAREA/booking-system-django'  # carpeta donde está manage.py
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DEBUG'] = '0'
os.environ['SECRET_KEY'] = 'CAMBIA-ESTO-por-una-clave-larga-y-aleatoria'
os.environ['ALLOWED_HOSTS'] = 'TU_USUARIO.pythonanywhere.com'
os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://TU_USUARIO.pythonanywhere.com'
# La cuenta gratuita bloquea el SMTP externo: los emails se escriben en el log.
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.console.EmailBackend'
# PythonAnywhere ya fuerza HTTPS y envía X-Forwarded-Proto.
os.environ['SECURE_SSL_REDIRECT'] = '1'

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
