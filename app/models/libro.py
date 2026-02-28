from app import db

class Libro(db.Model):
    __tablename__ = 'libro'

    LIBRO_ID = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.Integer, unique=True, nullable=False)

    AUTOR_ID = db.Column(
        db.Integer,
        db.ForeignKey('autor.AUTOR_ID'),
        nullable=False
    )

    # Relación con Prestamo
    prestamos = db.relationship('Prestamo', backref='libro', lazy=True)

    def __repr__(self):
        return f'<Libro {self.titulo}>'