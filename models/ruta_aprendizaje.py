<<<<<<< HEAD

from datetime import datetime
from . import db
=======
from models import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
>>>>>>> 5c996e8b362001d937c81d9fc3ce7c4e4a747824

class RutaAprendizaje(db.Model):
    __tablename__ = 'rutaaprendizaje'
    
    id_ruta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    nivel = db.Column(db.String(20))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RutaAprendizaje {self.id_ruta}: {self.titulo}>'