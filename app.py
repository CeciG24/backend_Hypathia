from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from models.usuario import Usuario

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/baseHypathia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Crear tablas
with app.app_context():
    db.create_all()

@app.route("/usuarios")
def get_usuarios():
    usuarios = Usuario.query.all()
    return { "usuarios": [u.nombre for u in usuarios] }

@app.route("/register", methods=["POST"])
def crear_usuario():
    data = request.get_json()

    # Validar datos obligatorios
    if not data or not all(k in data for k in ("nombre", "email", "contraseña", "rol")):
        return jsonify({"error": "Faltan datos"}), 400

    # Encriptar la contraseña
    contraseña_hash = generate_password_hash(data["contraseña"])

    nuevo_usuario = Usuario(
        nombre=data["nombre"],
        email=data["email"],
        contraseña_hash=contraseña_hash,
        rol=data["rol"],
        id_preferencia=data.get("id_preferencia")  # opcional
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Usuario creado con éxito", "id": nuevo_usuario.id_usuario}), 201


if __name__ == "__main__":
    app.run(debug=True)
