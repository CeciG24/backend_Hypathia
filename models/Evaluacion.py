
from datetime import datetime
from . import db

class Evaluacion(db.Model):
    __tablename__ = 'evaluacion'
    
    id_eval = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_modulo = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    preguntas = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Evaluacion {self.id_eval}>'