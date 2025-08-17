from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash



from models import db
from models.usuario import Usuario
from models.ruta_aprendizaje import RutaAprendizaje
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
            usuario.contraseña_hash = generate_password_hash(data["contraseña"])

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
        return jsonify({"message": "Usuario eliminado con éxito"}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar usuario: {str(e)}"}), 500

#CRUD rutas de aprendizaje

@app.route("/rutas-aprendizaje", methods=['GET'])
def get_rutas():
    try:
        rutas = RutaAprendizaje.query.all()
        
        # Mejor estructuración de los datos
        rutas_data = [
            {
                "id": ruta.id_ruta,
                "titulo": ruta.titulo,
                "descripcion": ruta.descripcion,
                "nivel": ruta.nivel,
                "fecha_creacion": ruta.fecha_creacion.isoformat() if ruta.fecha_creacion else None
            }
            for ruta in rutas
        ]
        
        return jsonify({
            "success": True,
            "data": rutas_data,
            "count": len(rutas_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/rutas-aprendizaje", methods=["POST"])
def post_ruta():
    try:
        data = request.get_json()
        # Validar datos obligatorios
        if not data or not all(k in data for k in ("titulo", "descripcion", "nivel")):
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        nueva_ruta = RutaAprendizaje(
            titulo=data["titulo"],
            descripcion=data["descripcion"],
            nivel=data["nivel"],
            fecha_creacion=datetime.utcnow()
        )

        db.session.add(nueva_ruta)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "titulo": nueva_ruta.titulo,
            "message": "Ruta de aprendizaje creada exitosamente",
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route("/rutas-aprendizaje/<int:id>", methods=["PUT"])
def update_ruta(id):
    try:
        ruta = RutaAprendizaje.query.get(id)
        if not ruta:
            return jsonify({"error": "Ruta no encontrado"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

        # Actualizar campos si se proporcionan
        if "titulo" in data:
            if not data["titulo"].strip():
                return jsonify({"error": "El titulo no puede estar vacío"}), 400
            ruta.titulo = data["titulo"]

        if "descripcion" in data:
            ruta.descripcion = data["descripcion"]

        if "nivel" in data:
            ruta.nivel = data["nivel"]

        db.session.commit()
        return jsonify({
            "message": "Ruta actualizada con éxito",
            "id_ruta": ruta.id_ruta
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar ruta de aprendizaje: {str(e)}"}), 500
    
@app.route("/rutas-aprendizaje/<int:id>", methods=["DELETE"])
def delete_ruta(id):
    try:
        ruta = RutaAprendizaje.query.get(id)
        if not ruta:
            return jsonify({"error": "Ruta no encontrada"}), 404

        db.session.delete(ruta)
        db.session.commit()
        return jsonify({"message": "Ruta eliminado con éxito"}), 202
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar ruta: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(debug=True)