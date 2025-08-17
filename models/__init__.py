from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from .usuario import Usuario
from .preferencias import Preferencia
from .ruta_aprendizaje import RutaAprendizaje
from .recomendacion_ia import RecomendacionIA
from .lecciones import Leccion
from .Evaluacion import Evaluacion
from .resultado_evaluacion import resultado_evaluacion
from .progreso_alumno import Progreso_alumno
from .pdfleccion import PDFLeccion
from .modulo import Modulo
from .test import Test
from .perfil_estudiante import PerfilEstudiante