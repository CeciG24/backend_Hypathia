from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import logging

# Configuración de logging (ya definido en el archivo original, incluido aquí para contexto)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from models import db

from models.usuario import Usuario
from datetime import datetime
import re

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/baseHypathia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)  # ← MUY IMPORTANTE

with app.app_context():  # contexto para crear tablas
    db.create_all()

# Lista de roles válidos según el esquema
VALID_ROLES = ["alumno", "docente", "tutor", "mentor", "admin"]

# Crear tablas
with app.app_context():
    db.create_all()

# Validación de email
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'
    return re.match(email_regex, email) is not None

@app.route("/usuarios", methods=["GET"])
def get_usuarios():
    try:
        usuarios = Usuario.query.all()
        return jsonify({
            "usuarios": [{
                "id_usuario": u.id_usuario,
                "nombre": u.nombre,
                "email": u.email,
                "rol": u.rol,
                "fecha_registro": u.fecha_registro.isoformat(),
                "id_preferencia": u.id_preferencia
            } for u in usuarios]
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener usuarios: {str(e)}"}), 500

@app.route("/usuarios/<int:id>", methods=["GET"])
def get_usuario_by_id(id):
    try:
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol,
            "fecha_registro": usuario.fecha_registro.isoformat(),
            "id_preferencia": usuario.id_preferencia
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener usuario: {str(e)}"}), 500

@app.route("/register", methods=["POST"])
def crear_usuario():
    try:
        data = request.get_json()
        # Validar datos obligatorios
        if not data or not all(k in data for k in ("nombre", "email", "contraseña", "rol")):
            return jsonify({"error": "Faltan datos obligatorios: nombre, email, contraseña, rol"}), 400
            # Validar campos obligatorios
        required_fields = ["nombre", "email", "contraseña", "rol"]
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return jsonify({"error": f"Falta o está vacío el campo '{field}'"}), 400

        # Validar email
        if not is_valid_email(data["email"]):
            return jsonify({"error": "Formato de email inválido"}), 400

        # Validar rol
        if data["rol"].lower() not in VALID_ROLES:
            return jsonify({"error": f"Rol inválido. Debe ser uno de: {', '.join(VALID_ROLES)}"}), 400

        # Verificar si el email ya existe
        if Usuario.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "El email ya está registrado"}), 409

        # Encriptar la contraseña
        contraseña_hash = generate_password_hash(data["contraseña"], method="pbkdf2:sha256")

        nuevo_usuario = Usuario(
            nombre=data["nombre"],
            email=data["email"],
            contraseña_hash=contraseña_hash,
            rol=data["rol"].lower(),
            fecha_registro=datetime.utcnow(),
            id_preferencia=data.get("id_preferencia")  # opcional
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
            "message": "Usuario creado con éxito",
            "id_usuario": nuevo_usuario.id_usuario
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear usuario: {str(e)}"}), 500

@app.route("/usuarios/<int:id>", methods=["PUT"])
def update_usuario(id):
    try:
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

        # Actualizar campos si se proporcionan
        if "nombre" in data:
            if not data["nombre"].strip():
                return jsonify({"error": "El nombre no puede estar vacío"}), 400
            usuario.nombre = data["nombre"]

        if "email" in data:
            if not is_valid_email(data["email"]):
                return jsonify({"error": "Formato de email inválido"}), 400
            # Verificar si el nuevo email ya existe
            existing_usuario = Usuario.query.filter_by(email=data["email"]).first()
            if existing_usuario and existing_usuario.id_usuario != id:
                return jsonify({"error": "El email ya está registrado"}), 409
            usuario.email = data["email"]

        if "contraseña" in data:
            if not data["contraseña"].strip():
                return jsonify({"error": "La contraseña no puede estar vacía"}), 400
            usuario.contraseña_hash = generate_password_hash(data["contraseña"],method="pbkdf2:sha256")

        if "rol" in data:
            if data["rol"].lower() not in VALID_ROLES:
                return jsonify({"error": f"Rol inválido. Debe ser uno de: {', '.join(VALID_ROLES)}"}), 400
            usuario.rol = data["rol"].lower()

        if "id_preferencia" in data:
            usuario.id_preferencia = data["id_preferencia"]

        db.session.commit()
        return jsonify({
            "message": "Usuario actualizado con éxito",
            "id_usuario": usuario.id_usuario
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar usuario: {str(e)}"}), 500

@app.route("/usuarios/<int:id>", methods=["DELETE"])
def delete_usuario(id):
    try:
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"message": "Usuario eliminado con éxito"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar usuario: {str(e)}"}), 500


@app.route("/login", methods=["POST"])
def login_usuario():
    try:
        data = request.get_json()
        logger.debug(f"Datos recibidos para login: {data}")

        # Validar datos obligatorios y no vacíos
        required_fields = ["email", "contraseña"]
        if not data or not all(k in data for k in required_fields):
            return jsonify({"error": "Faltan datos obligatorios: email, contraseña"}), 400

        for field in required_fields:
            if not str(data[field]).strip():
                return jsonify({"error": f"El campo '{field}' no puede estar vacío"}), 400

        # Validar email
        if not is_valid_email(data["email"]):
            return jsonify({"error": "Formato de email inválido"}), 400

        # Buscar usuario por email
        usuario = Usuario.query.filter_by(email=data["email"]).first()
        if not usuario:
            logger.debug(f"Usuario no encontrado para email: {data['email']}")
            return jsonify({"error": "Credenciales inválidas"}), 401

        # Verificar contraseña
        if not check_password_hash(usuario.contraseña_hash, data["contraseña"]):
            logger.debug("Contraseña incorrecta")
            return jsonify({"error": "Credenciales inválidas"}), 401

        logger.debug(f"Login exitoso para usuario: {usuario.email}")
        return jsonify({
            "message": "Login exitoso",
            "usuario": {
                "id_usuario": usuario.id_usuario,
                "nombre": usuario.nombre,
                "email": usuario.email,
                "rol": usuario.rol,
                "fecha_registro": usuario.fecha_registro.isoformat(),
                "id_preferencia": usuario.id_preferencia
            }
        }), 200
    except Exception as e:
        logger.error(f"Error al procesar login: {str(e)}")
        return jsonify({"error": f"Error al procesar login: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)


