#ESTE ES EL MODULO DE AUTENTICACION, AQUI SE GESTIONAN LAS RUTAS DE REGISTRO Y LOGIN
from flask import Blueprint, render_template, request, redirect, url_for, flash # Importamos herramientas necesarias de Flask
from flask_login import login_user, logout_user # Importamos funciones de Flask-Login para gestionar sesiones
from app.models.usuario import Usuario # Importamos el modelo de Usuario para interactuar con la base de datos
from app import db # Importamos la base de datos


# Creamos el Blueprint de autenticación
auth_routes = Blueprint('auth', __name__)


# Ruta para registrar usuarios
@auth_routes.route('/registro', methods=['GET', 'POST'])
def registro():

    # Si el formulario fue enviado
    if request.method == 'POST':

        # Capturamos los datos del formulario
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')

        # Verificamos si el correo ya existe
        usuario_existente = Usuario.query.filter_by(correo=correo).first()

        if usuario_existente:
            flash("El correo ya está registrado", "danger")
            return redirect(url_for('auth.registro'))

        # Creamos nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password=password  # Luego encriptaremos
        )

        # Guardamos en la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Usuario registrado correctamente", "success")
        return redirect(url_for('main.inicio'))

    # Si es GET, mostramos el formulario en la vista 'registro.html'
    return render_template('sign_up.html')

# ********Ruta para iniciar sesión***********
@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    # Si el formulario fue enviado
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        # Buscamos el usuario por correo
        usuario = Usuario.query.filter_by(correo=correo).first()

        # Verificamos si el usuario existe y la contraseña es correcta
        if usuario and usuario.password == password:
            login_user(usuario)
            return redirect(url_for("main.principal"))# Redirigimos a la página principal después de iniciar sesión
        else:
            flash("Credenciales incorrectas")# Mostramos un mensaje de error si las credenciales son incorrectas
    
    return render_template("login.html")

# ********Ruta para cerrar sesión***********
@auth_routes.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.inicio"))