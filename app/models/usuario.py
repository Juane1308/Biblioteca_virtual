from app import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    fecha_registro = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # Foreign Key hacia Rol
    ROL_ID = db.Column(
        db.Integer,
        db.ForeignKey('rol.ROL_ID')
    )

    # Relación: un usuario puede tener muchos préstamos
    prestamos = db.relationship(
        'Prestamo',
        backref='usuario',
        lazy=True
    )

    def __repr__(self):
        return f'<Usuario {self.nombre}>'