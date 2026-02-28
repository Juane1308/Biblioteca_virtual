from app import db

class Prestamo(db.Model):
    __tablename__ = 'prestamo'

    PRESTAMO_ID = db.Column(db.Integer, primary_key=True)

    USUARIO_ID = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=False
    )

    LIBRO_ID = db.Column(
        db.Integer,
        db.ForeignKey('libro.LIBRO_ID'),
        nullable=False
    )

    fecha_prestamo = db.Column(db.Date, nullable=False)
    fecha_devolucion = db.Column(db.Date)
    estado = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Prestamo {self.PRESTAMO_ID}>'