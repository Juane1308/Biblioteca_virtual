from flask import Blueprint, render_template# Importamos Blueprint para organizar rutas, render_template para mostrar vistas
from flask_login import login_required, current_user # Importamos herramientas de Flask-Login para proteger rutas y acceder al usuario actual
from app.models.libro import Libro  # Importamos el modelo de Libro para mostrar libros en la vista principal

main_routes = Blueprint('main', __name__)

# Ruta de inicio, accesible para todos
@main_routes.route("/")
def inicio():
    return render_template("inicio.html")

# Ruta principal, solo para usuarios autenticados
@main_routes.route("/main")
@login_required
def principal():

     # Consultamos todos los libros registrados
    libros = Libro.query.all()
    # Enviamos la lista a la plantilla
    return render_template("main.html", libros=libros)

# Ruta para mostrar detalles de un libro específico, solo para usuarios autenticados
@main_routes.route("/libro/<int:libro_id>")
@login_required
def book_detail(libro_id):
    
    libro = Libro.query.get_or_404(libro_id)
    
    return render_template("book_detail.html", libro=libro)

