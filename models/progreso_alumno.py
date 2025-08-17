<<<<<<< HEAD

from datetime import datetime
from . import db
=======
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
>>>>>>> 5c996e8b362001d937c81d9fc3ce7c4e4a747824

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