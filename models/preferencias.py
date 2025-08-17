from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
class preferencias (db.Model):
    __tablename__ = "preferencias"

    id_preferencia = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)