from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models.autor import Autor
from app.models.libro import Libro
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.prestamo import Prestamo
from datetime import datetime

admin_routes = Blueprint(
    "admin_routes",
    __name__,
    template_folder="../templates/admin"
)

# ======================
# DASHBOARD
# ======================
@admin_routes.route("/")
def dashboard():
    return render_template("dashboard.html")

# ==================================================
# ====================== AUTOR =====================
# ==================================================

@admin_routes.route("/autores")
def listar_autores():
    autores = Autor.query.all()
    return render_template("autores/list.html", autores=autores)

@admin_routes.route("/autores/crear", methods=["GET","POST"])
def crear_autor():
    if request.method == "POST":
        nuevo = Autor(
            nombre=request.form["nombre"],
            nacionalidad=request.form["nacionalidad"],
            fecha_nacimiento=datetime.strptime(request.form["fecha"], "%Y-%m-%d")
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_autores"))
    return render_template("autores/crear.html")

@admin_routes.route("/autores/eliminar/<int:id>")
def eliminar_autor(id):
    autor = Autor.query.get_or_404(id)
    db.session.delete(autor)
    db.session.commit()
    return redirect(url_for("admin_routes.listar_autores"))

# ==================================================
# ====================== LIBRO =====================
# ==================================================

# Listar libros con su autor
@admin_routes.route("/libros")
def listar_libros():
    libros = Libro.query.all()
    return render_template("libros/list.html", libros=libros)

#crear libro con opción a crear autor nuevo si no existe
@admin_routes.route("/libros/crear", methods=["GET","POST"])
def crear_libro():
    autores = Autor.query.all()

    if request.method == "POST":

        autor_id = request.form.get("autor_id")
        nuevo_autor_nombre = request.form.get("nuevo_autor_nombre")

        # Si escribió un nuevo autor, lo creamos
        if nuevo_autor_nombre:
            nuevo_autor = Autor(
                nombre=nuevo_autor_nombre,
                nacionalidad=request.form.get("nuevo_autor_nacionalidad"),
                fecha_nacimiento=datetime.strptime(
                    request.form.get("nuevo_autor_fecha"),
                    "%Y-%m-%d"
                ) if request.form.get("nuevo_autor_fecha") else None
            )

            db.session.add(nuevo_autor)
            db.session.commit()

            autor_id = nuevo_autor.AUTOR_ID

        # Validación: debe existir un autor
        if not autor_id:
            return "Debe seleccionar o crear un autor"

        nuevo_libro = Libro(
            titulo=request.form["titulo"],
            isbn=request.form["isbn"],
            AUTOR_ID=autor_id
        )

        db.session.add(nuevo_libro)
        db.session.commit()

        return redirect(url_for("admin_routes.listar_libros"))

    return render_template("libros/crear.html", autores=autores)

# Eliminar libro
@admin_routes.route("/libros/eliminar/<int:id>")
def eliminar_libro(id):
    libro = Libro.query.get_or_404(id)
    db.session.delete(libro)
    db.session.commit()
    return redirect(url_for("admin_routes.listar_libros"))

# ==================================================
# ===================== USUARIO ====================
# ==================================================

@admin_routes.route("/usuarios")
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template("usuarios/list.html", usuarios=usuarios)

@admin_routes.route("/usuarios/crear", methods=["GET", "POST"])
def crear_usuario():
    roles = Rol.query.all()

    if request.method == "POST":
        nuevo = Usuario(
            nombre=request.form["nombre"],
            correo=request.form["correo"],
            password=request.form["password"],
            ROL_ID=request.form["rol_id"]
        )

        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_usuarios"))

    return render_template("usuarios/crear.html", roles=roles)

@admin_routes.route("/usuarios/eliminar/<int:id>")
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for("admin_routes.listar_usuarios"))

# ==================================================
# ==================== PRESTAMO ====================
# ==================================================

@admin_routes.route("/prestamos")
def listar_prestamos():
    prestamos = Prestamo.query.all()
    return render_template("prestamos/list.html", prestamos=prestamos)

@admin_routes.route("/prestamos/crear", methods=["GET", "POST"])
def crear_prestamo():
    usuarios = Usuario.query.all()
    libros = Libro.query.all()

    if request.method == "POST":
        nuevo = Prestamo(
            USUARIO_ID=request.form["usuario_id"],
            LIBRO_ID=request.form["libro_id"],
            fecha_prestamo=datetime.strptime(request.form["fecha_prestamo"], "%Y-%m-%d"),
            fecha_devolucion=datetime.strptime(request.form["fecha_devolucion"], "%Y-%m-%d"),
            estado=True
        )

        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_prestamos"))

    return render_template("prestamos/crear.html", usuarios=usuarios, libros=libros)

@admin_routes.route("/prestamos/eliminar/<int:id>")
def eliminar_prestamo(id):
    prestamo = Prestamo.query.get_or_404(id)
    db.session.delete(prestamo)
    db.session.commit()
    return redirect(url_for("admin_routes.listar_prestamos"))

# ==================================================
# ======================== ROL =====================
# ==================================================

@admin_routes.route("/roles")
def listar_roles():
    roles = Rol.query.all()
    return render_template("roles/list.html", roles=roles)

@admin_routes.route("/roles/crear", methods=["GET", "POST"])
def crear_rol():
    if request.method == "POST":
        nuevo = Rol(nombre=request.form["nombre"])
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_roles"))

    return render_template("roles/crear.html")

@admin_routes.route("/roles/eliminar/<int:id>")
def eliminar_rol(id):
    rol = Rol.query.get_or_404(id)
    db.session.delete(rol)
    db.session.commit()
    return redirect(url_for("admin_routes.listar_roles"))