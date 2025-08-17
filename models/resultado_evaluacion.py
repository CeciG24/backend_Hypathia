
from datetime import datetime
from . import db
class resultado_evaluacion(db.Model):
    __tablename__ = 'resultadoevaluacion'
    
    id_resultado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_eval = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    calificacion = db.Column(db.Numeric(5, 2))
    retroalimentacion_ia = db.Column(db.Text)

    def __repr__(self):
        return f'<resultado_evaluacion {self.id_resultado}>'