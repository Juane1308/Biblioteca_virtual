from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
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



def get_autor_desconocido_id() -> int:
    """
    Retorna el AUTOR_ID del autor especial "Desconocido".
    Si no existe, lo crea para poder asignarlo a libros sin autor.

    Esto evita errores de integridad porque LIBRO.AUTOR_ID suele ser NOT NULL.
    """
    autor = Autor.query.filter(Autor.nombre.ilike("desconocido")).first()
    if not autor:
        # Usamos valores "seguros" para los campos requeridos del autor.
        autor = Autor(
            nombre="Desconocido",
            nacionalidad="N/A",
            fecha_nacimiento=datetime(1900, 1, 1),
        )
        db.session.add(autor)
        db.session.commit()

    return autor.AUTOR_ID


# ==================================================
# Helpers
# ==================================================
def _es_admin() -> bool:
    """Retorna True si el usuario logueado tiene rol 'Admin'."""
    try:
        return (
            current_user.is_authenticated
            and current_user.rol is not None
            and (current_user.rol.nombre or "").strip().lower() == "admin"
        )
    except Exception:
        return False


def admin_required(view_func):
    """Protege rutas del admin. Si no es admin, lo manda al inicio."""
    from functools import wraps

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _es_admin():
            flash("Acceso denegado: solo administradores.", "danger")
            return redirect(url_for("main.inicio"))
        return view_func(*args, **kwargs)

    return login_required(wrapper)


# ======================
# DASHBOARD
# ======================
@admin_routes.route("/")
@admin_required
def dashboard():
    return render_template("dashboard.html")

# ==================================================
# ====================== AUTOR =====================
# ==================================================

@admin_routes.route("/autores")
@admin_required
def listar_autores():
    autores = Autor.query.all()
    return render_template("autores/list.html", autores=autores)

@admin_routes.route("/autores/crear", methods=["GET","POST"])
@admin_required
def crear_autor():
    if request.method == "POST":
        nuevo = Autor(
            nombre=request.form["nombre"],
            nacionalidad=request.form.get("nacionalidad"),
            fecha_nacimiento=datetime.strptime(request.form["fecha"], "%Y-%m-%d")
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_autores"))
    return render_template("autores/crear.html")

@admin_routes.route("/autores/editar/<int:id>", methods=["GET","POST"])
@admin_required
def editar_autor(id):
    autor = Autor.query.get_or_404(id)

    if request.method == "POST":
        autor.nombre = request.form["nombre"]
        autor.nacionalidad = request.form.get("nacionalidad")
        autor.fecha_nacimiento = datetime.strptime(request.form["fecha"], "%Y-%m-%d")
        db.session.commit()
        return redirect(url_for("admin_routes.listar_autores"))

    return render_template("autores/editar.html", autor=autor)

@admin_routes.route("/autores/eliminar/<int:id>")
@admin_required
def eliminar_autor(id):
    # Eliminamos un autor de forma segura.
    # Problema típico: si el autor tiene libros (y esos libros tienen préstamos),
    # la BD no deja borrar por restricciones NOT NULL / FK.
    autor = Autor.query.get_or_404(id)

    try:
        # 1) Traer todos los libros del autor
        libros_autor = Libro.query.filter_by(AUTOR_ID=autor.AUTOR_ID).all()

        # 2) Borrar primero los préstamos de esos libros
        for libro in libros_autor:
            Prestamo.query.filter_by(LIBRO_ID=libro.LIBRO_ID).delete()

        # 3) Borrar los libros
        for libro in libros_autor:
            db.session.delete(libro)

        # 4) Borrar el autor
        db.session.delete(autor)
        db.session.commit()
        flash("Autor eliminado correctamente.", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo eliminar el autor. Verifica relaciones en la base de datos.", "error")

    return redirect(url_for("admin_routes.listar_autores"))

# ==================================================
# ====================== LIBRO =====================
# ==================================================

@admin_routes.route("/libros")
@admin_required
def listar_libros():
    libros = Libro.query.all()
    return render_template("libros/list.html", libros=libros)

@admin_routes.route("/libros/crear", methods=["GET","POST"])
@admin_required
def crear_libro():
    autores = Autor.query.all()
    autor_desconocido_id = get_autor_desconocido_id()

    if request.method == "POST":
        autor_id = (request.form.get("autor_id") or "").strip()
        nuevo_autor_nombre = (request.form.get("nuevo_autor_nombre") or "").strip()

        # Si escribió un nuevo autor, lo creamos y lo asignamos al libro
        if nuevo_autor_nombre:
            nuevo_autor = Autor(
                nombre=nuevo_autor_nombre,
                nacionalidad=request.form.get("nuevo_autor_nacionalidad") or "N/A",
                fecha_nacimiento=(
                    datetime.strptime(request.form.get("nuevo_autor_fecha"), "%Y-%m-%d")
                    if request.form.get("nuevo_autor_fecha")
                    else datetime(1900, 1, 1)
                ),
            )
            db.session.add(nuevo_autor)
            db.session.commit()
            autor_id = str(nuevo_autor.AUTOR_ID)

        # Si NO seleccionó autor y NO creó uno nuevo, asignamos "Desconocido"
        if not autor_id:
            autor_id = str(autor_desconocido_id)

        nuevo_libro = Libro(
            titulo=request.form["titulo"],
            isbn=request.form["isbn"],
            AUTOR_ID=int(autor_id),
        )

        db.session.add(nuevo_libro)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_libros"))

    return render_template("libros/crear.html", autores=autores, autor_desconocido_id=autor_desconocido_id)

@admin_routes.route("/libros/editar/<int:id>", methods=["GET","POST"])
@admin_required
def editar_libro(id):
    libro = Libro.query.get_or_404(id)
    autores = Autor.query.all()
    autor_desconocido_id = get_autor_desconocido_id()

    if request.method == "POST":
        libro.titulo = request.form["titulo"]
        libro.isbn = request.form["isbn"]

        autor_id = (request.form.get("autor_id") or "").strip()

        # Si viene vacío, lo marcamos como "Desconocido"
        if not autor_id:
            autor_id = str(autor_desconocido_id)

        libro.AUTOR_ID = int(autor_id)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_libros"))

    return render_template(
        "libros/editar.html",
        libro=libro,
        autores=autores,
        autor_desconocido_id=autor_desconocido_id,
    )

@admin_routes.route("/libros/eliminar/<int:id>")
@admin_required
def eliminar_libro(id):
    # Eliminamos un libro de forma segura:
    # primero borramos préstamos asociados para evitar errores de integridad.
    libro = Libro.query.get_or_404(id)

    try:
        Prestamo.query.filter_by(LIBRO_ID=libro.LIBRO_ID).delete()
        db.session.delete(libro)
        db.session.commit()
        flash("Libro eliminado correctamente.", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo eliminar el libro. Verifica relaciones en la base de datos.", "error")

    return redirect(url_for("admin_routes.listar_libros"))

# ==================================================
# ===================== USUARIO ====================
# ==================================================

@admin_routes.route("/usuarios")
@admin_required
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template("usuarios/list.html", usuarios=usuarios)

@admin_routes.route("/usuarios/crear", methods=["GET", "POST"])
@admin_required
def crear_usuario():
    roles = Rol.query.all()

    if request.method == "POST":
        nuevo = Usuario(
            nombre=request.form["nombre"],
            correo=request.form["correo"],
            password=request.form["password"],
            ROL_ID=request.form.get("rol_id") or None
        )

        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_usuarios"))

    return render_template("usuarios/crear.html", roles=roles)

@admin_routes.route("/usuarios/editar/<int:id>", methods=["GET","POST"])
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    roles = Rol.query.all()

    if request.method == "POST":
        usuario.nombre = request.form["nombre"]
        usuario.correo = request.form["correo"]

        # Si el password viene vacío, no lo tocamos
        password = request.form.get("password", "").strip()
        if password:
            usuario.password = password

        usuario.ROL_ID = request.form.get("rol_id") or None

        db.session.commit()
        return redirect(url_for("admin_routes.listar_usuarios"))

    return render_template("usuarios/editar.html", usuario=usuario, roles=roles)

@admin_routes.route("/usuarios/eliminar/<int:id>")
@admin_required
def eliminar_usuario(id):
    # Eliminamos un usuario de forma segura:
    # primero borramos sus préstamos para evitar FK/NOT NULL en prestamo.USUARIO_ID
    usuario = Usuario.query.get_or_404(id)

    try:
        Prestamo.query.filter_by(USUARIO_ID=usuario.id).delete()
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuario eliminado correctamente.", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo eliminar el usuario. Verifica relaciones en la base de datos.", "error")

    return redirect(url_for("admin_routes.listar_usuarios"))

# ==================================================
# ==================== PRESTAMO ====================
# ==================================================

@admin_routes.route("/prestamos")
@admin_required
def listar_prestamos():
    prestamos = Prestamo.query.all()
    return render_template("prestamos/list.html", prestamos=prestamos)

@admin_routes.route("/prestamos/crear", methods=["GET", "POST"])
@admin_required
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

@admin_routes.route("/prestamos/editar/<int:id>", methods=["GET","POST"])
@admin_required
def editar_prestamo(id):
    prestamo = Prestamo.query.get_or_404(id)
    usuarios = Usuario.query.all()
    libros = Libro.query.all()

    if request.method == "POST":
        prestamo.USUARIO_ID = request.form["usuario_id"]
        prestamo.LIBRO_ID = request.form["libro_id"]
        prestamo.fecha_prestamo = datetime.strptime(request.form["fecha_prestamo"], "%Y-%m-%d")
        prestamo.fecha_devolucion = datetime.strptime(request.form["fecha_devolucion"], "%Y-%m-%d")
        prestamo.estado = True if request.form.get("estado") == "1" else False
        db.session.commit()
        return redirect(url_for("admin_routes.listar_prestamos"))

    return render_template("prestamos/editar.html", prestamo=prestamo, usuarios=usuarios, libros=libros)

@admin_routes.route("/prestamos/eliminar/<int:id>")
@admin_required
def eliminar_prestamo(id):
    prestamo = Prestamo.query.get_or_404(id)
    db.session.delete(prestamo)
    db.session.commit()
    return redirect(url_for("admin_routes.listar_prestamos"))

# ==================================================
# ======================== ROL =====================
# ==================================================

@admin_routes.route("/roles")
@admin_required
def listar_roles():
    roles = Rol.query.all()
    return render_template("roles/list.html", roles=roles)

@admin_routes.route("/roles/crear", methods=["GET", "POST"])
@admin_required
def crear_rol():
    if request.method == "POST":
        nuevo = Rol(nombre=request.form["nombre"])
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_roles"))

    return render_template("roles/crear.html")

@admin_routes.route("/roles/editar/<int:id>", methods=["GET","POST"])
@admin_required
def editar_rol(id):
    rol = Rol.query.get_or_404(id)

    if request.method == "POST":
        rol.nombre = request.form["nombre"]
        db.session.commit()
        return redirect(url_for("admin_routes.listar_roles"))

    return render_template("roles/editar.html", rol=rol)

@admin_routes.route("/roles/eliminar/<int:id>")
@admin_required
def eliminar_rol(id):
    # Eliminamos un rol de forma segura.
    # Problema típico: si hay usuarios con este rol, la BD no deja borrar.
    rol = Rol.query.get_or_404(id)

    # No permitir borrar el rol "Usuario" (lo usamos como rol default del sistema)
    if rol.nombre and rol.nombre.lower() == "usuario":
        flash("No se puede eliminar el rol 'Usuario' porque es el rol por defecto.", "error")
        return redirect(url_for("admin_routes.listar_roles"))

    try:
        # Buscar/crear rol Usuario para reasignar
        rol_usuario = Rol.query.filter(Rol.nombre.ilike("usuario")).first()
        if not rol_usuario:
            rol_usuario = Rol(nombre="Usuario")
            db.session.add(rol_usuario)
            db.session.commit()

        # Reasignar usuarios que tengan este rol
        usuarios_con_rol = Usuario.query.filter_by(ROL_ID=rol.ROL_ID).all()
        for u in usuarios_con_rol:
            u.ROL_ID = rol_usuario.ROL_ID

        # Ahora sí borrar el rol
        db.session.delete(rol)
        db.session.commit()
        flash("Rol eliminado correctamente.", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo eliminar el rol. Verifica relaciones en la base de datos.", "error")

    return redirect(url_for("admin_routes.listar_roles"))
