from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Importo el modelo de Usuario para que SQLAlchemy lo reconozca y pueda crear la tabla correspondiente en la base de datos.
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.main_routes import main_routes
    app.register_blueprint(main_routes)

  

    with app.app_context():
        
        from app.models.usuario import Usuario
        from app.models.autor import Autor
        from app.models.libro import Libro
        from app.models.prestamo import Prestamo
        from app.models.rol import Rol

        db.create_all()

    return app
