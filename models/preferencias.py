
from . import db
from datetime import datetime

class Preferencia (db.Model):

    __tablename__ = "preferencias"

    id_preferencia = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
