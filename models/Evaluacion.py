

from datetime import datetime
from . import db
=======
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
>>>>>>> 5c996e8b362001d937c81d9fc3ce7c4e4a747824

class Evaluacion(db.Model):
    __tablename__ = 'evaluacion'
    
    id_eval = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_modulo = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    preguntas = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Evaluacion {self.id_eval}>'