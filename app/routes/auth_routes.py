#ESTE ES EL MODULO DE AUTENTICACION, AQUI SE GESTIONAN LAS RUTAS DE REGISTRO Y LOGIN
from flask import Blueprint, render_template, request, redirect, url_for, flash # Importamos herramientas necesarias de Flask
from app import db # Importamos la base de datos
from app.models.usuario import Usuario # Importamos el modelo Usuario
from app.models.rol import Rol  # Importamos Rol para asignar rol por defecto

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

        # Buscamos (o creamos) el rol por defecto "Usuario".
        # Así, cada registro normal queda con rol Usuario automáticamente.
        rol_usuario = Rol.query.filter(db.func.lower(Rol.nombre) == "usuario").first()

        if not rol_usuario:
            rol_usuario = Rol(nombre="Usuario")
            db.session.add(rol_usuario)
            db.session.flush()  # obtenemos rol_usuario.ROL_ID antes del commit

        # Creamos nuevo usuario con rol por defecto
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password=password,  # Luego encriptaremos
            ROL_ID=rol_usuario.ROL_ID
        )

        # Guardamos en la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Usuario registrado correctamente", "success")
        return redirect(url_for('main.inicio'))

    # Si es GET, mostramos el formulario en la vista 'registro.html'
    return render_template('registro.html')