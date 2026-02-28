from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
# Importo el modelo de Usuario para que SQLAlchemy lo reconozca y pueda crear la tabla correspondiente en la base de datos.
db = SQLAlchemy() # Inicializamos SQLAlchemy para gestionar la base de datos
login_manager = LoginManager() # Importamos el LoginManager para gestionar la autenticación de usuarios

# Función obligatoria para Flask-Login
# Le dice cómo cargar un usuario desde la base de datos usando su ID
@login_manager.user_loader
def load_user(user_id):
    from app.models.usuario import Usuario
    
    # user_id llega como string, lo convertimos a int
    return Usuario.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    
    #***IMPORTACION DE BLUEPRINTS***
    # Importamos blueprint principal
    from app.routes.main_routes import main_routes
    app.register_blueprint(main_routes)

    # Importamos blueprint de autenticación
    from app.routes.auth_routes import auth_routes
    app.register_blueprint(auth_routes)

    #***IMPORTACION DE MODELOS***
    # Importamos el modelo de Usuario para que SQLAlchemy lo reconozca y pueda crear la tabla correspondiente en la base de datos.
    from app.models.usuario import Usuario

    with app.app_context():
        db.create_all()  
     
    return app


