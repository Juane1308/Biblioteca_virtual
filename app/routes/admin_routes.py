"""Rutas del panel de administración.

Este archivo implementa CRUD para las tablas principales.

IMPORTANTE SOBRE ELIMINAR (DELETE)
---------------------------------
Tu BD tiene llaves foráneas con NOT NULL (por ejemplo libro.AUTOR_ID, prestamo.USUARIO_ID,
prestamo.LIBRO_ID). Por eso, si intentas borrar un "padre" que tiene "hijos", SQLite/SQLAlchemy
lanza IntegrityError.

Para que el panel NO "explote" y, además, puedas eliminar sin tener que borrar manualmente
los registros relacionados, aquí aplicamos una política de borrado en cascada *a nivel de código*:

- Eliminar Autor  -> elimina primero Préstamos de sus Libros -> luego Libros -> luego Autor.
- Eliminar Libro  -> elimina primero sus Préstamos -> luego Libro.
- Eliminar Usuario-> elimina primero sus Préstamos -> luego Usuario.
- Eliminar Rol    -> NO borra usuarios; los reasigna al rol "Usuario" y luego borra el rol.
  (Si intentas borrar el rol "Usuario", lo bloqueamos para no dejar el sistema sin rol default.)

Así evitas errores de integridad y mantienes el CRUD funcionando.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.autor import Autor
from app.models.libro import Libro
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.prestamo import Prestamo
from datetime import datetime
from sqlalchemy.exc import IntegrityError

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

@admin_routes.route("/autores/crear", methods=["GET", "POST"])
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

    try:
        # 1) Buscar todos los libros del autor
        libros = Libro.query.filter_by(AUTOR_ID=autor.AUTOR_ID).all()

        # 2) Por cada libro, eliminar primero sus préstamos (FK NOT NULL: prestamo.LIBRO_ID)
        for libro in libros:
            Prestamo.query.filter_by(LIBRO_ID=libro.LIBRO_ID).delete(synchronize_session=False)

        # 3) Eliminar los libros del autor (FK NOT NULL: libro.AUTOR_ID)
        Libro.query.filter_by(AUTOR_ID=autor.AUTOR_ID).delete(synchronize_session=False)

        # 4) Finalmente, eliminar el autor
        db.session.delete(autor)
        db.session.commit()
        flash("Autor eliminado correctamente (y sus libros/préstamos asociados).", "success")
    except IntegrityError:
        # Si algo sale mal, deshacemos la transacción para no dejar la sesión en estado roto.
        db.session.rollback()
        flash("No se pudo eliminar el autor por restricciones de la base de datos.", "error")
    except Exception:
        db.session.rollback()
        flash("Ocurrió un error inesperado al eliminar el autor.", "error")

    return redirect(url_for("admin_routes.listar_autores"))

@admin_routes.route("/autores/editar/<int:id>", methods=["GET", "POST"])
def editar_autor(id):
    autor = Autor.query.get_or_404(id)

    if request.method == "POST":
        autor.nombre = request.form["nombre"]
        autor.nacionalidad = request.form["nacionalidad"]
        autor.fecha_nacimiento = datetime.strptime(request.form["fecha"], "%Y-%m-%d")
        db.session.commit()
        return redirect(url_for("admin_routes.listar_autores"))

    return render_template("autores/editar.html", autor=autor)

# ==================================================
# ====================== LIBRO =====================
# ==================================================

@admin_routes.route("/libros")
def listar_libros():
    libros = Libro.query.all()
    return render_template("libros/list.html", libros=libros)

@admin_routes.route("/libros/crear", methods=["GET", "POST"])
def crear_libro():
    autores = Autor.query.all()

    if request.method == "POST":
        nuevo = Libro(
            titulo=request.form["titulo"],
            isbn=request.form["isbn"],
            AUTOR_ID=request.form["autor_id"]
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_libros"))

    return render_template("libros/crear.html", autores=autores)

@admin_routes.route("/libros/eliminar/<int:id>")
def eliminar_libro(id):
    libro = Libro.query.get_or_404(id)

    try:
        # 1) Eliminar préstamos del libro primero (FK NOT NULL: prestamo.LIBRO_ID)
        Prestamo.query.filter_by(LIBRO_ID=libro.LIBRO_ID).delete(synchronize_session=False)

        # 2) Eliminar el libro
        db.session.delete(libro)
        db.session.commit()
        flash("Libro eliminado correctamente (y sus préstamos asociados).", "success")
    except IntegrityError:
        db.session.rollback()
        flash("No se pudo eliminar el libro por restricciones de la base de datos.", "error")
    except Exception:
        db.session.rollback()
        flash("Ocurrió un error inesperado al eliminar el libro.", "error")

    return redirect(url_for("admin_routes.listar_libros"))

@admin_routes.route("/libros/editar/<int:id>", methods=["GET", "POST"])
def editar_libro(id):
    libro = Libro.query.get_or_404(id)
    autores = Autor.query.all()

    if request.method == "POST":
        libro.titulo = request.form["titulo"]
        libro.isbn = request.form["isbn"]
        libro.AUTOR_ID = request.form["autor_id"]
        db.session.commit()
        return redirect(url_for("admin_routes.listar_libros"))

    return render_template("libros/editar.html", libro=libro, autores=autores)

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
        # Si el formulario no trae rol_id (o viene vacío), asignamos el rol por defecto "Usuario".
        # Esto ayuda a evitar usuarios sin rol.
        rol_id = (request.form.get("rol_id") or "").strip() or None

        if rol_id is None:
            rol_usuario = Rol.query.filter(db.func.lower(Rol.nombre) == "usuario").first()
            if not rol_usuario:
                rol_usuario = Rol(nombre="Usuario")
                db.session.add(rol_usuario)
                db.session.flush()
            rol_id = str(rol_usuario.ROL_ID)

        nuevo = Usuario(
            nombre=request.form["nombre"],
            correo=request.form["correo"],
            password=request.form["password"],
            ROL_ID=rol_id
        )

        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_routes.listar_usuarios"))

    return render_template("usuarios/crear.html", roles=roles)

@admin_routes.route("/usuarios/eliminar/<int:id>")
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    try:
        # NOTA: En tu modelo Usuario la PK se llama "id" (no USUARIO_ID).
        # Prestamo.USUARIO_ID referencia a usuarios.id

        # 1) Eliminar préstamos del usuario primero (FK NOT NULL: prestamo.USUARIO_ID)
        Prestamo.query.filter_by(USUARIO_ID=usuario.id).delete(synchronize_session=False)

        # 2) Eliminar el usuario
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuario eliminado correctamente (y sus préstamos asociados).", "success")
    except IntegrityError:
        db.session.rollback()
        flash("No se pudo eliminar el usuario por restricciones de la base de datos.", "error")
    except Exception:
        db.session.rollback()
        flash("Ocurrió un error inesperado al eliminar el usuario.", "error")

    return redirect(url_for("admin_routes.listar_usuarios"))

@admin_routes.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    roles = Rol.query.all()

    if request.method == "POST":
        usuario.nombre = request.form["nombre"]
        usuario.correo = request.form["correo"]

        # Si el password viene vacío, no lo tocamos (para no sobreescribirlo)
        password = request.form.get("password", "").strip()
        if password:
            usuario.password = password

        # Mantengo tu lógica: si viene vacío -> None
        usuario.ROL_ID = request.form.get("rol_id") or None

        db.session.commit()
        return redirect(url_for("admin_routes.listar_usuarios"))

    return render_template("usuarios/editar.html", usuario=usuario, roles=roles)

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

    try:
        db.session.delete(prestamo)
        db.session.commit()
        flash("Préstamo eliminado correctamente.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("No se pudo eliminar el préstamo por restricciones de la base de datos.", "error")
    except Exception:
        db.session.rollback()
        flash("Ocurrió un error inesperado al eliminar el préstamo.", "error")

    return redirect(url_for("admin_routes.listar_prestamos"))

@admin_routes.route("/prestamos/editar/<int:id>", methods=["GET", "POST"])
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

    # Por diseño, vamos a mantener un rol "Usuario" como rol por defecto.
    # Si alguien intenta borrar ese rol, lo bloqueamos para no romper el registro/login.
    if rol.nombre.strip().lower() == "usuario":
        flash('No se puede eliminar el rol "Usuario" porque es el rol por defecto.', "error")
        return redirect(url_for("admin_routes.listar_roles"))

    try:
        # 1) Asegurar que exista el rol por defecto "Usuario".
        rol_usuario = Rol.query.filter(db.func.lower(Rol.nombre) == "usuario").first()
        if not rol_usuario:
            rol_usuario = Rol(nombre="Usuario")
            db.session.add(rol_usuario)
            db.session.flush()  # obtiene rol_usuario.ROL_ID sin hacer commit aún

        # 2) Reasignar todos los usuarios que tenían este rol al rol "Usuario".
        Usuario.query.filter_by(ROL_ID=rol.ROL_ID).update(
            {"ROL_ID": rol_usuario.ROL_ID},
            synchronize_session=False
        )

        # 3) Ya sin usuarios apuntándolo, podemos borrar el rol.
        db.session.delete(rol)
        db.session.commit()
        flash("Rol eliminado correctamente (usuarios reasignados a 'Usuario').", "success")
    except IntegrityError:
        db.session.rollback()
        flash("No se pudo eliminar el rol por restricciones de la base de datos.", "error")
    except Exception:
        db.session.rollback()
        flash("Ocurrió un error inesperado al eliminar el rol.", "error")

    return redirect(url_for("admin_routes.listar_roles"))

@admin_routes.route("/roles/editar/<int:id>", methods=["GET", "POST"])
def editar_rol(id):
    rol = Rol.query.get_or_404(id)

    if request.method == "POST":
        rol.nombre = request.form["nombre"]
        db.session.commit()
        return redirect(url_for("admin_routes.listar_roles"))

    return render_template("roles/editar.html", rol=rol)