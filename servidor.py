from flask import render_template,Flask, jsonify, request, Response
from functools import wraps

app = Flask(__name__)

# Base de datos simulada
base_datos = {
    "usuarios": [
        {"id": 1, "nombre": "Juan"},
        {"id": 2, "nombre": "María"}
    ]
}

# Función para verificar la autenticación básica (se aplica a todas las rutas excepto agregar_usuario)
def verificar_autenticacion(func):
    @wraps(func)
    def decorador(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != 'admin' or auth.password != 'admin':
            # Si no se autentica correctamente, se devuelve 401 (no autorizado)
            return Response('Acceso no autorizado', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return func(*args, **kwargs)
    return decorador

# Ruta para obtener los usuarios
@app.route('/usuarios', methods=['GET'])
@verificar_autenticacion
def obtener_usuarios():
    return jsonify(base_datos["usuarios"])

# Ruta para registrar un nuevo usuario
@app.route('/usuarios', methods=['POST'])
@verificar_autenticacion
def registrar_usuario():
    try:
        nuevo_usuario = request.get_json()


        # Validar que el nombre no este vacio
        if not nuevo_usuario or 'nombre' not in nuevo_usuario or not nuevo_usuario['nombre'].strip():
            return jsonify({"error": "El nombre es requerido y no puede estar vacío"}), 400
        # Validar longitud del nombre
        if len(nuevo_usuario['nombre']) < 2 or len(nuevo_usuario['nombre']) > 50:
            return jsonify({"error": "El nombre debe tener entre 2 y 50 caracteres"}), 400
        
        # Validar que el nombre no contenga números o caracteres inválidos
        import re
        if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚ\\s]+$", nuevo_usuario['nombre']):
            return jsonify({"error": "El nombre solo puede contener letras y espacios"}), 400
        
        # Genera un nuevo ID para el usuario de manera más robusta
        nuevo_id = max(usuario['id'] for usuario in base_datos["usuarios"]) + 1
        nuevo_usuario["id"] = nuevo_id
        base_datos["usuarios"].append(nuevo_usuario)

        return jsonify(nuevo_usuario), 201
    except Exception as e:
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@app.route('/')
@verificar_autenticacion
def index():
    return render_template('index.html')

@app.route('/usuarios/<int:id>', methods=['GET'])
@verificar_autenticacion
def obtener_usuario(id):
    for usuario in base_datos["usuarios"]:
        if usuario["id"] == id:
            return jsonify(usuario)
    return jsonify({"error": "Usuario no encontrado"}), 404

@app.route('/usuarios/<int:id>', methods=['DELETE'])
@verificar_autenticacion
def eliminar_usuario(id):
    global base_datos
    usuario_a_eliminar = next((u for u in base_datos["usuarios"] if u["id"] == id), None)
    if usuario_a_eliminar:
        base_datos["usuarios"].remove(usuario_a_eliminar)
        return jsonify({"mensaje": f"Usuario con ID {id} eliminado correctamente"}), 200
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
if __name__ == '__main__':
    app.run(port=5000)

@app.route('/usuarios/<int:usuario_id>', methods=['GET'])
@verificar_autenticacion
def buscar_id(usuario_id):
    usuario = next((u for u in base_datos["usuarios"] if u["id"] == usuario_id), None)
    if usuario:
        return jsonify(usuario)
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404


