<<<<<<< HEAD

from datetime import datetime
from . import db
=======
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
>>>>>>> 5c996e8b362001d937c81d9fc3ce7c4e4a747824
class resultado_evaluacion(db.Model):
    __tablename__ = 'resultadoevaluacion'
    
    id_resultado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_eval = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    calificacion = db.Column(db.Numeric(5, 2))
    retroalimentacion_ia = db.Column(db.Text)

    def __repr__(self):
        return f'<resultado_evaluacion {self.id_resultado}>'