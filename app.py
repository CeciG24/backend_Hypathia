from flask import Flask, request, jsonify,request,send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import logging
import google.generativeai as genai
import json
app = Flask(__name__)
from flask_login import LoginManager, login_required, current_user
import subprocess
import os
import uuid

jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app) # Nombre exacto del endpoint
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
from models.lecciones import Leccion
from models.modulo import Modulo
from models.pdfleccion import PDFLeccion
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

        access_token = create_access_token(identity={
            "id": nuevo_usuario.id_usuario,
            "email": nuevo_usuario.email,
            "rol": nuevo_usuario.rol
        })

        return jsonify({
            "message": "Usuario creado con éxito",
            "id_usuario": nuevo_usuario.id_usuario,
            "token": access_token
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
        nuevo_token = create_access_token(identity=usuario.id_usuario)

        return jsonify({
            "message": "Usuario actualizado con éxito",
            "id_usuario": usuario.id_usuario,
            "token": nuevo_token
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

        NIVELES_PERMITIDOS=['básico', 'intermedio', 'avanzado']
        if data["nivel"] not in NIVELES_PERMITIDOS:
            return jsonify({"error": f"Nivel debe ser uno de: {NIVELES_PERMITIDOS}"}), 400
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

        access_token = create_access_token(identity=usuario.id_usuario)


        return jsonify({
            "message": "Login exitoso",
            "usuario": {
                "token": access_token,
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
        return jsonify({"error": f"Error al procesar login: {str(e)}"}),500
    
# Plantilla LaTeX para el PDF (incluye el nombre del módulo)
LATEX_TEMPLATE = r"""
\documentclass[a4paper,12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[spanish]{babel}
\usepackage{parskip}
\usepackage{geometry}
\geometry{margin=2cm}

\begin{document}

\begin{center}
    \textbf{\Large } \\
    \vspace{0.5cm}
    \textbf{Lección: %s}
\end{center}

%s

\end{document}
"""


@app.route('/generate_pdf/<int:leccion_id>', methods=['GET'])
def generate_pdf(leccion_id):
    # Obtener la lección desde la base de datos
    leccion = Leccion.query.get_or_404(leccion_id)

    # Obtener el nombre del módulo asociado
    modulo = Modulo.query.get(leccion.id_modulo)


    # Generar contenido LaTeX
    title = leccion.titulo
    content = leccion.contenido.replace('\n', '\n\n')  # Asegurar párrafos en LaTeX
    latex_content = LATEX_TEMPLATE % ( title, content)

    # Generar nombre de archivo único
    pdf_filename = f"leccion_{leccion_id}_{uuid.uuid4()}.pdf"
    pdf_filepath = os.path.join(app.config['PDF_UPLOAD_FOLDER'], pdf_filename)
    tex_filepath = os.path.join(app.config['PDF_UPLOAD_FOLDER'], f"leccion_{leccion_id}.tex")

    # Escribir archivo .tex
    with open(tex_filepath, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    # Compilar LaTeX a PDF usando latexmk
    try:
        subprocess.run(['latexmk', '-pdf', '-pdflatex=pdflatex', tex_filepath],
                       cwd=app.config['PDF_UPLOAD_FOLDER'], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Error al generar el PDF'}), 500

    # Limpiar archivos auxiliares
    for ext in ['.aux', '.log', '.out', '.tex', '.fls', '.fdb_latexmk']:
        try:
            os.remove(os.path.join(app.config['PDF_UPLOAD_FOLDER'], f"leccion_{leccion_id}{ext}"))
        except FileNotFoundError:
            pass

    # Guardar metadatos en la base de datos
    pdf_entry = PDFLeccion(
        id_leccion=leccion_id,
        titulo=f"{title}",
        url_pdf=f"/{app.config['PDF_UPLOAD_FOLDER']}/{pdf_filename}"
    )
    db.session.add(pdf_entry)
    db.session.commit()

    # Enviar el PDF al cliente
    return send_file(pdf_filepath, as_attachment=True, download_name=f"{title}.pdf")
    
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

#CRUD modulos
@app.route("/modulos", methods=['GET'])
def get_modulos():
    try:
        modulos = Modulo.query.all()
        
        # Mejor estructuración de los datos
        modulos_data = [
            {
                "id": modulo.id_modulo,
                "id_ruta": modulo.id_modulo,
                "titulo": modulo.titulo,
                "descripcion": modulo.descripcion,
                "orden": modulo.orden
            }
            for modulo in modulos
        ]
        
        return jsonify({
            "success": True,
            "data": modulos_data,
            "count": len(modulos_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/modulos", methods=["POST"])
def post_modulo():
    try:
        data = request.get_json()
        # Validar datos obligatorios
        if not data or not all(k in data for k in (
                "id_ruta",
                "titulo",
                "descripcion",
                "orden")):
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        nuevo_modulo = Modulo(
            id_ruta=data["id_ruta"],
            titulo=data["titulo"],
            descripcion=data["descripcion"],
            orden=data["orden"],
        )

        db.session.add(nuevo_modulo)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "titulo": nuevo_modulo.titulo,
            "message": "Modulo creado exitosamente",
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route("/modulos/<int:id>", methods=["PUT"])
def update_modulo(id):
    try:
        modulo = modulo.query.get(id)
        if not modulo:
            return jsonify({"error": "modulo no encontrada"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

        # Actualizar campos si se proporcionan
        if "id_ruta" in data:
            if not data["id_ruta"].strip():
                return jsonify({"error": "El id_ruta no puede estar vacío"}), 400
            modulo.id_ruta = data["id_ruta"]

        if "titulo" in data:
            if not data["titulo"].strip():
                return jsonify({"error": "El titulo no puede estar vacío"}), 400
            modulo.titulo = data["titulo"]

        if "descripcion" in data:
            modulo.descripcion = data["descripcion"]

        if "orden" in data:
            modulo.orden = data["orden"]

        db.session.commit()
        return jsonify({
            "message": "modulo actualizado con éxito",
            "id_modulo": modulo.id_modulo
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar modulo: {str(e)}"}), 500
    
@app.route("/modulos/<int:id>", methods=["DELETE"])
def delete_modulo(id):
    try:
        modulo = Modulo.query.get(id)
        if not modulo:
            return jsonify({"error": "modulo no encontrado"}), 404

        db.session.delete(modulo)
        db.session.commit()
        return jsonify({"message": "modulo eliminado con éxito"}), 202
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar modulo: {str(e)}"}), 500
    
#CRUD lecciones
@app.route("/lecciones", methods=['GET'])
def get_lecciones():
    try:
        lecciones = Leccion.query.all()
        
        # Mejor estructuración de los datos
        lecciones_data = [
            {
                "id": leccion.id_leccion,
                "id_modulo": leccion.id_modulo,
                "titulo": leccion.titulo,
                "contenido": leccion.contenido,
                "tipo": leccion.tipo,
                "orden": leccion.orden
            }
            for leccion in lecciones
        ]
        
        return jsonify({
            "success": True,
            "data": lecciones_data,
            "count": len(lecciones_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/lecciones", methods=["POST"])
def post_leccion():
    try:
        data = request.get_json()
        # Validar datos obligatorios
        if not data or not all(k in data for k in (
                "id_modulo",
                "titulo",
                "contenido",
                "tipo",
                "orden")):
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        TIPOS_PERMITIDOS=['teórica', 'práctica', 'quiz']
        if data["tipo"] not in TIPOS_PERMITIDOS:
            return jsonify({"error": f"Tipo debe ser uno de: {TIPOS_PERMITIDOS}"}), 400
        
        nueva_leccion = Leccion(
            id_modulo=data["id_modulo"],
            titulo=data["titulo"],
            contenido=data["contenido"],
            tipo=data["tipo"],
            orden=data["orden"],
        )

        db.session.add(nueva_leccion)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "titulo": nueva_leccion.titulo,
            "message": "leccion creada exitosamente",
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route("/lecciones/<int:id>", methods=["PUT"])
def update_leccion(id):
    try:
        leccion = Leccion.query.get(id)
        if not leccion:
            return jsonify({"error": "leccion no encontrada"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

        # Actualizar campos si se proporcionan
        if "id_modulo" in data:
            if not data["id_modulo"].strip():
                return jsonify({"error": "El id_modulo no puede estar vacío"}), 400
            leccion.id_modulo = data["id_modulo"]

        if "titulo" in data:
            if not data["titulo"].strip():
                return jsonify({"error": "El titulo no puede estar vacío"}), 400
            leccion.titulo = data["titulo"]

        if "contenido" in data:
            leccion.contenido = data["contenido"]

        if "tipo" in data:
            leccion.tipo = data["tipo"]

        if "orden" in data:
            leccion.orden = data["orden"]

        db.session.commit()
        return jsonify({
            "message": "leccion actualizada con éxito",
            "id_leccion": leccion.id_leccion
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar leccion: {str(e)}"}), 500
    
@app.route("/lecciones/<int:id>", methods=["DELETE"])
def delete_leccion(id):
    try:
        leccion = Leccion.query.get(id)
        if not leccion:
            return jsonify({"error": "leccion no encontrada"}), 404

        db.session.delete(leccion)
        db.session.commit()
        return jsonify({"message": "leccion eliminada con éxito"}), 202
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar leccion: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
