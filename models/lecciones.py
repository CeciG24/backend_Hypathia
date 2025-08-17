from . import db


class Leccion(db.Model):
    __tablename__ = "leccion"

    id_leccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_modulo = db.Column(db.Integer, db.ForeignKey("modulo.id_modulo"), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    orden = db.Column(db.Integer, nullable=True)

    # Relación con Modulo (si existe el modelo Modulo)
    modulo = db.relationship("Modulo", backref="lecciones", lazy=True)

    def __repr__(self):
        return f"<Leccion {self.titulo} (Módulo {self.id_modulo})>"