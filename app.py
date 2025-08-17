from flask import Flask, request, jsonify,request
from flask_cors import CORS
from werkzeug.security import generate_password_hash,check_password_hash
import logging
import google.generativeai as genai
import json
app = Flask(__name__)
from flask_login import LoginManager, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_usuario'  # Nombre exacto del endpoint
app.config['SECRET_KEY'] = 'hsgdahjowuw123' 

# Configura tu user_loader (necesitas un modelo Usuario)
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

CORS(app)

# Configuración de logging (ya definido en el archivo original, incluido aquí para contexto)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


from models import db
from models.usuario import Usuario
from models.test import Test
from models.ruta_aprendizaje import RutaAprendizaje
from models.perfil_estudiante import PerfilEstudiante
from datetime import datetime
import re

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
    

@app.route("/login", methods=["POST"],endpoint='login_usuario')
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
    
@app.route("/save-results", methods=["POST"])
@login_required
def save_test_results():
    try:
        # Obtener el ID del usuario autenticado directamente
        user_id = 2
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Datos requeridos"}), 400
            
        new_test = Test(
            id_usuario=user_id,  # Usamos current_user.id
            resultados_vocacional=data.get('intereses'),
            resultados_emocional=data.get('emocional'),
            resultados_inteligencia=data.get('gardner')
        )
        
        db.session.add(new_test)
        db.session.commit()
        
        return jsonify({
            "message": "Test guardado",
            "test_id": new_test.id_test
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Configura tu clave de API de Gemini
# ¡Importante! Guarda tu clave en un lugar seguro (variables de entorno)
# En este ejemplo, la pongo directamente para que veas el código completo
API_KEY = "AIzaSyCPsyWhUw7t9WCUSRg5zzqQyje8Tizou2E"
genai.configure(api_key=API_KEY)

@app.route("/analizar-perfil-inicial", methods=["POST"])
@login_required
def analizar_perfil_inicial():
    try:
        # Obtener datos del JSON
        data = request.get_json()
        
        # Validación básica
        if not data or not all(k in data for k in ("test_vocacional", "test_emocional", "test_inteligencia")):
            return jsonify({"error": "Faltan datos de los tests"}), 400
            
        # Usuario autenticado (no necesitamos recibir id_usuario)
        id_usuario = current_user.id
        
        # Crear prompt para Gemini AI
        prompt = f"""
        Analiza en profundidad los siguientes resultados de tests de un estudiante y genera un perfil detallado EN FORMATO JSON VÁLIDO (sin comentarios adicionales):

        ### Datos de entrada:
        1. TEST VOCACIONAL (Escala 1-5):
        {json.dumps(data['test_vocacional'], indent=2)}

        2. TEST EMOCIONAL (Escala 1-5):
        {json.dumps(data['test_emocional'], indent=2)}

        3. TEST DE INTELIGENCIAS MÚLTIPLES (Verdadero/Falso):
        {json.dumps(data['test_inteligencia'], indent=2)}

        ### Instrucciones para el análisis:
        - **Sé específico**: Evita frases genéricas como "se requiere más información".
        - **Relaciona características**: Ej: "Su alta puntuación en preguntas lógicas (vocacional 4/5) y facilidad para matemáticas (inteligencia verdadero) sugiere aptitud para ingenierías".
        - **Usa esta estructura exacta** (elimina la sección de explicaciones):

        {{
        "resumen_perfil": "2-3 oraciones destacando rasgos clave",
        "ruta_aprendizaje": "Carrera/área específica (ej: 'Ingeniería en Sistemas', 'Diseño Gráfico')",
        "fortalezas": [
            "Habilidad 1 (basada en datos concretos)",
            "Habilidad 2 (ej: 'Pensamiento lógico' por X puntuación)"
        ],
        "areas_desarrollar": [
            "Área 1 (ej: 'Trabajo en equipo' por baja puntuación en Y)",
            "Área 2"
        ],
        "estilo_aprendizaje": "Visual/Auditivo/Kinestésico (justificado con datos)",
        "tipo_tutoria": "Recomendación concreta (ej: 'Tutor técnico en programación')"
        }}

        ### Ejemplo de respuesta esperada (para guiarte):
        {{
        "resumen_perfil": "Estudiante con marcado perfil lógico-matemático (vocacional 4.5/5 en preguntas técnicas) y alta inteligencia espacial (test inteligencia 90% verdadero en preguntas visuales), pero con dificultades en gestión emocional (test emocional 2/5 en preguntas de estrés).",
        "ruta_aprendizaje": "Ingeniería en Inteligencia Artificial",
        "fortalezas": [
            "Resolución de problemas complejos (vocacional 5/5 en lógica)",
            "Orientación al detalle (inteligencia 100% verdadero en preguntas de patrones)"
        ],
        "areas_desarrollar": [
            "Gestión del estrés (emocional 1.8/5 en preguntas de ansiedad)",
            "Trabajo colaborativo (vocacional 2/5 en preguntas sociales)"
        ],
        "estilo_aprendizaje": "Visual (por alta puntuación en ejercicios gráficos del test inteligencia)",
        "tipo_tutoria": "Tutor especializado en proyectos de IA con enfoque en manejo de presión"
            }}
        """
        
        # Llamada a Gemini
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Procesamiento de la respuesta
        try:
            perfil_ia = response.text.strip()
            # Limpieza si la respuesta viene con markdown
            if perfil_ia.startswith('```json'):
                perfil_ia = perfil_ia[7:-3].strip()
            perfil_ia_json = json.loads(perfil_ia)
        except json.JSONDecodeError as e:
            return jsonify({"error": "La IA no generó un JSON válido", "respuesta_ia": response.text}), 500

        # Guardar en base de datos
        nuevo_perfil = PerfilEstudiante(
            id_usuario=id_usuario,
            perfil_ia=perfil_ia_json
        )
        
        db.session.add(nuevo_perfil)
        db.session.commit()
        
        return jsonify({
            "message": "Perfil generado con éxito",
            "perfil": nuevo_perfil.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)

