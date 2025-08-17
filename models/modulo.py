from . import db

class Modulo(db.Model):
    __tablename__ = "modulo"

    id_modulo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_ruta = db.Column(db.Integer, db.ForeignKey("rutaaprendizaje.id_ruta"), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    orden = db.Column(db.Integer, nullable=True)

    ruta = db.relationship("RutaAprendizaje", back_populates="modulos")

    def __repr__(self):
        return f"<Modulo {self.titulo} (Ruta {self.id_ruta})>"