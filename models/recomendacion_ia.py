from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class RecomendacionIA(db.Model):
    __tablename__ = 'recomendacionia'
    
    id_reco = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_ruta = db.Column(db.Integer, nullable=False)
    mensaje = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RecomendacionIA {self.id_reco}>'