from datetime import datetime
from . import db

class RutaAprendizaje(db.Model):
    __tablename__ = 'rutaaprendizaje'
    
    id_ruta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    nivel = db.Column(db.String(20))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con Modulo (si existe el modelo Modulo)
    modulos = db.relationship("Modulo", back_populates="ruta")

    def __repr__(self):
        return f'<RutaAprendizaje {self.id_ruta}: {self.titulo}>'