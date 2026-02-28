import os

# Obtenemos la ruta absoluta del directorio raíz del proyecto
# (donde está este archivo config.py)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Clave secreta para sesiones
    SECRET_KEY = 'clave_super_secreta'

    # Construimos una ruta absoluta hacia biblioteca.db
    # Esto garantiza que el archivo se cree exactamente en la raíz del proyecto
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'biblioteca.db')

    # Desactivamos notificaciones innecesarias
    SQLALCHEMY_TRACK_MODIFICATIONS = False