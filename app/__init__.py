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

    from app.models.usuario import Usuario

    """with app.app_context():
        db.create_all()"""

    with app.app_context():
        print("📦 Creando tablas si no existen...")
        db.create_all()    

    return app
