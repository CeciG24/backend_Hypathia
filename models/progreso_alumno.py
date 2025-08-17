
from datetime import datetime
from . import db

class Progreso_alumno(db.Model):
    __tablename__ = 'progresoalumno'
    
    id_progreso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_ruta = db.Column(db.Integer, nullable=False)
    id_modulo = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    calificacion = db.Column(db.Numeric(5, 2))
    fecha_ultimo_intento = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProgresoAlumno {self.id_progreso}>'