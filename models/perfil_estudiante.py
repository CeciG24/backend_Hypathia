from datetime import datetime
from . import db  # Asumiendo que db está definido en un archivo __init__.py o similar

class PerfilEstudiante(db.Model):
    __tablename__ = 'perfiles_estudiante'
    
    id_perfil = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    perfil_ia = db.Column(db.JSON, nullable=False)  # Almacena el JSON generado por la IA
    fecha_analisis = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relación con el usuario
    usuario = db.relationship('Usuario', backref=db.backref('perfiles', lazy=True))
    
    def __init__(self, id_usuario, perfil_ia):
        self.id_usuario = id_usuario
        self.perfil_ia = perfil_ia
        
    def __repr__(self):
        return f'<PerfilEstudiante {self.id_perfil} - Usuario: {self.id_usuario}>'
    
    def to_dict(self):
        return {
            'id_perfil': self.id_perfil,
            'id_usuario': self.id_usuario,
            'perfil_ia': self.perfil_ia,
            'fecha_analisis': self.fecha_analisis.isoformat()
        }