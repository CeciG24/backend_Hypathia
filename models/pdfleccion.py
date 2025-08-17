from datetime import datetime
from . import db

class PDFLeccion(db.Model):
    __tablename__ = 'pdfleccion'
    
    id_pdf = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_leccion = db.Column(db.Integer, nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    url_pdf = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PDFLeccion {self.id_pdf}>'