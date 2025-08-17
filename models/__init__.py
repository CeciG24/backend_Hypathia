from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from .usuario import Usuario
from .preferencias import Preferencia
