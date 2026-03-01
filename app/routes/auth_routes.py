#ESTE ES EL MODULO DE AUTENTICACION, AQUI SE GESTIONAN LAS RUTAS DE REGISTRO Y LOGIN
from flask import Blueprint, render_template, request, redirect, url_for, flash # Importamos herramientas necesarias de Flask
from app import db # Importamos la base de datos
from app.models.usuario import Usuario # Importamos el modelo Usuario

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
    return render_template('registro.html')