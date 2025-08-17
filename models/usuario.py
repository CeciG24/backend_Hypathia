from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contraseña_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="alumno")
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    id_preferencia = db.Column(db.Integer, db.ForeignKey("preferencias.id_preferencia"), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)  # ← aquí

    # Relación opcional si existe la tabla 'preferencias'
    preferencia = db.relationship("Preferencia", backref="usuario")


    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.email})>"