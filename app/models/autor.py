from app import db #Importo la base de datos para definir el modelo de Autor

class Autor(db.Model):
    __tablename__ = 'autor'

    AUTOR_ID = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nacionalidad = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.Date)

    # Relación: un autor puede tener muchos libros
    libros = db.relationship('Libro', backref='autor', lazy=True)

    def __repr__(self):
        return f'<Autor {self.nombre}>'