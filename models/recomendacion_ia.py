<<<<<<< HEAD

from datetime import datetime
from . import db
=======
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
>>>>>>> 5c996e8b362001d937c81d9fc3ce7c4e4a747824

class RecomendacionIA(db.Model):
    __tablename__ = 'recomendacionia'
    
    id_reco = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_ruta = db.Column(db.Integer, nullable=False)
    mensaje = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RecomendacionIA {self.id_reco}>'