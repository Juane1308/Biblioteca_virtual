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


def crear_roles_y_admin_por_defecto():
    """
    Crea datos mínimos si no existen:
    - Rol 'Usuario'
    - Rol 'Admin'
    - Usuario admin por defecto (admin@admin.com / admin123)

    Se ejecuta después de db.create_all().
    No duplica, porque primero consulta.
    """
    from app.models.rol import Rol
    from app.models.usuario import Usuario

    # 1) Crear rol Usuario si no existe
    rol_usuario = Rol.query.filter(Rol.nombre.ilike("usuario")).first()
    if not rol_usuario:
        rol_usuario = Rol(nombre="Usuario")
        db.session.add(rol_usuario)
        db.session.commit()

    # 2) Crear rol Admin si no existe
    rol_admin = Rol.query.filter(Rol.nombre.ilike("admin")).first()
    if not rol_admin:
        rol_admin = Rol(nombre="Admin")
        db.session.add(rol_admin)
        db.session.commit()

    # 3) Crear usuario admin si no existe
    admin_existente = Usuario.query.filter_by(correo="admin@admin.com").first()
    if not admin_existente:
        nuevo_admin = Usuario(
            nombre="Administrador",
            correo="admin@admin.com",
            password="admin123",      # ⚠️ luego la podemos hashear si quieres
            ROL_ID=rol_admin.ROL_ID   # asignamos rol Admin
        )
        db.session.add(nuevo_admin)
        db.session.commit()


# Función para crear la aplicación Flask
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializamos las extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)

    # Si alguien intenta acceder a una ruta protegida sin estar autenticado, redirige al login
    # Ajusta este endpoint si en tu auth_routes el login tiene otro nombre
    login_manager.login_view = "auth_routes.login"

    # ==============================
    # Control de cache (evita que al retroceder se "guarde" la info)
    # ==============================
    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # *** IMPORTACIÓN DE BLUEPRINTS ***
    from app.routes.main_routes import main_routes
    from app.routes.auth_routes import auth_routes
    from app.routes.admin_routes import admin_routes

    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(admin_routes, url_prefix="/admin")

    # *** IMPORTACIÓN DE MODELOS Y CREACIÓN DE TABLAS ***
    with app.app_context():
        # Importamos modelos para que SQLAlchemy registre las tablas
        from app.models.usuario import Usuario  # noqa: F401
        from app.models.autor import Autor      # noqa: F401
        from app.models.libro import Libro      # noqa: F401
        from app.models.prestamo import Prestamo  # noqa: F401
        from app.models.rol import Rol          # noqa: F401

        # Crea el archivo .db con todas las tablas si no existe
        db.create_all()

        # Crea roles base + usuario admin por defecto
        crear_roles_y_admin_por_defecto()

    return app