<<<<<<< HEAD
from . import db
=======
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
>>>>>>> 5c996e8b362001d937c81d9fc3ce7c4e4a747824

class Modulo(db.Model):
    __tablename__ = "modulo"

    id_leccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_ruta = db.Column(db.Integer, db.ForeignKey("ruta.id_ruta"), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    orden = db.Column(db.Integer, nullable=True)

    # Relación con Modulo (si existe el modelo Modulo)
    ruta = db.relationship("Ruta", backref="modulo", lazy=True)

    def __repr__(self):
        return f"<Modulo {self.titulo} (Ruta {self.id_ruta})>"