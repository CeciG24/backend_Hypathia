<<<<<<< HEAD
from models import db

class Preferencia (db.Model):
=======
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
class preferencias (db.Model):
>>>>>>> 5c996e8b362001d937c81d9fc3ce7c4e4a747824
    __tablename__ = "preferencias"

    id_preferencia = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
