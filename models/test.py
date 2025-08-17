from . import db
from datetime import datetime

class Test(db.Model):
    __tablename__ = 'Test'
    
    id_test = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    resultados_vocacional = db.Column(db.JSON)
    resultados_emocional = db.Column(db.JSON)
    resultados_inteligencia = db.Column(db.JSON)
    fecha_realizacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relación con la tabla usuarios
    usuario = db.relationship('Usuario', backref=db.backref('tests', lazy=True, cascade='all, delete-orphan'))
    
    def __init__(self, id_usuario, resultados_vocacional=None, resultados_emocional=None, resultados_inteligencia=None):
        self.id_usuario = id_usuario
        self.resultados_vocacional = resultados_vocacional
        self.resultados_emocional = resultados_emocional
        self.resultados_inteligencia = resultados_inteligencia
        
    def __repr__(self):
        return f'<Test {self.id_test} - Usuario: {self.id_usuario}>'
    
    def to_dict(self):
        return {
            'id_test': self.id_test,
            'id_usuario': self.id_usuario,
            'resultados_vocacional': self.resultados_vocacional,
            'resultados_emocional': self.resultados_emocional,
            'resultados_inteligencia': self.resultados_inteligencia,
            'fecha_realizacion': self.fecha_realizacion.isoformat()
        }