from flask import Blueprint, render_template# Importamos Blueprint para organizar rutas, render_template para mostrar vistas
from flask_login import login_required, current_user # Importamos herramientas de Flask-Login para proteger rutas y acceder al usuario actual

main_routes = Blueprint('main', __name__)

# Ruta de inicio, accesible para todos
@main_routes.route("/")
def inicio():
    return render_template("inicio.html")

# Ruta principal, solo para usuarios autenticados
@main_routes.route("/main")
@login_required
def principal():
    return render_template("main.html")

