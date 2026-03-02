from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# ==========================================================
# Inicializamos las extensiones (se usan en toda la app)
# ==========================================================
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth_routes.login"  # ajusta si tu endpoint de login tiene otro nombre


# ==========================================================
# Función obligatoria para Flask-Login
# Flask-Login guarda el id del usuario en la sesión.
# Aquí le decimos cómo cargarlo desde la BD.
# ==========================================================
@login_manager.user_loader
def load_user(user_id):
    from app.models.usuario import Usuario
    return Usuario.query.get(int(user_id))


# ==========================================================
# Seeder / Inicialización de datos mínimos
# - Crea roles base (Usuario, Admin)
# - Crea usuario admin por defecto (si no existe)
# ==========================================================
def crear_roles_y_admin_por_defecto():
    """
    Este método se ejecuta al iniciar la app (después de db.create_all()).

    ¿Qué hace?
    1) Verifica si existe el rol "Usuario". Si no existe, lo crea.
    2) Verifica si existe el rol "Admin". Si no existe, lo crea.
    3) Verifica si existe un usuario admin por correo. Si no existe, lo crea y le asigna el rol Admin.

    Importante:
    - No duplica datos porque siempre consulta antes de insertar.
    """

    # Importaciones aquí adentro para evitar imports circulares
    from app.models.rol import Rol
    from app.models.usuario import Usuario

    # ---------- 1) Rol Usuario (rol por defecto para registros) ----------
    rol_usuario = Rol.query.filter(Rol.nombre.ilike("usuario")).first()
    if not rol_usuario:
        rol_usuario = Rol(nombre="Usuario")
        db.session.add(rol_usuario)
        db.session.commit()

    # ---------- 2) Rol Admin ----------
    rol_admin = Rol.query.filter(Rol.nombre.ilike("admin")).first()
    if not rol_admin:
        rol_admin = Rol(nombre="Admin")
        db.session.add(rol_admin)
        db.session.commit()

    # ---------- 3) Usuario Admin por defecto ----------
    # Puedes cambiar el correo y contraseña por los que quieras
    admin_existente = Usuario.query.filter_by(correo="admin@admin.com").first()
    if not admin_existente:
        nuevo_admin = Usuario(
            nombre="Administrador",
            correo="admin@admin.com",
            password="admin123",     # ⚠️ si luego quieres lo hasheamos
            ROL_ID=rol_admin.ROL_ID  # Asignamos rol Admin
        )
        db.session.add(nuevo_admin)
        db.session.commit()


# ==========================================================
# Factory: crea y configura la app
# ==========================================================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializamos extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)

    # ======================================================
    # Importación de BLUEPRINTS (rutas)
    # ======================================================
    from app.routes.main_routes import main_routes
    from app.routes.auth_routes import auth_routes
    from app.routes.admin_routes import admin_routes

    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(admin_routes, url_prefix="/admin")

    # ======================================================
    # Importación de MODELOS + creación de tablas
    # ======================================================
    with app.app_context():
        # Importamos modelos para que SQLAlchemy registre las tablas
        from app.models.usuario import Usuario  # noqa: F401
        from app.models.autor import Autor      # noqa: F401
        from app.models.libro import Libro      # noqa: F401
        from app.models.prestamo import Prestamo  # noqa: F401
        from app.models.rol import Rol          # noqa: F401

        # Crea el archivo .db con todas las tablas si no existe
        db.create_all()

        # Crea roles base + admin por defecto (si no existen)
        crear_roles_y_admin_por_defecto()

    return app