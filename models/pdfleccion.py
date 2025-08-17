<<<<<<< HEAD

from datetime import datetime
from . import db

=======
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
>>>>>>> 5c996e8b362001d937c81d9fc3ce7c4e4a747824
class PDFLeccion(db.Model):
    __tablename__ = 'pdfleccion'
    
    id_pdf = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_leccion = db.Column(db.Integer, nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    url_pdf = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PDFLeccion {self.id_pdf}>'