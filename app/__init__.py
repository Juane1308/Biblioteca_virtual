from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Inicializamos las extensiones
db = SQLAlchemy()
login_manager = LoginManager()

# Función obligatoria para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models.usuario import Usuario
    # user_id llega como string, lo convertimos a int para la consulta
    return Usuario.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializamos las extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    
    # *** IMPORTACIÓN DE BLUEPRINTS ***
    # Traemos las rutas principales y las de autenticación (login)
    from app.routes.main_routes import main_routes
    from app.routes.auth_routes import auth_routes
    from app.routes.admin_routes import admin_routes

    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(admin_routes, url_prefix="/admin")

    # *** IMPORTACIÓN DE MODELOS Y CREACIÓN DE TABLAS ***
    with app.app_context():
        # Importamos todos tus modelos para que SQLAlchemy cree las tablas
        from app.models.usuario import Usuario
        from app.models.autor import Autor
        from app.models.libro import Libro
        from app.models.prestamo import Prestamo
        from app.models.rol import Rol

        # Crea el archivo .db con todas las tablas si no existe
        db.create_all()

    return app