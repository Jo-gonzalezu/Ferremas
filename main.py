from flask import Flask, request, jsonify, Response
import json

app = Flask(__name__)

@app.route("/")
def root():
    return "Api desarrollada en flask para Ferremas"

# Array / Diccionario de tipos de usuario en la web de Ferremas
tipos_usuarios = [
    {"id": 1, "nombre": "Administrador"},
    {"id": 2, "nombre": "Empleado"},
    {"id": 3, "nombre": "Cliente"},
]

# Array / Diccionario de usuarios de Ferremas
usuarios = [
    { "id": 1, "nombre": "Constanza", "apellido_p": "Olivares", "apellido_m": "Leon", "tipo_usuario": "1", "correo": "co.olivaresl@duocuc.cl", "telefono": "9 20370693"},
    { "id": 2, "nombre": "Alan", "apellido_p": "Cruz", "apellido_m": "Baeza", "tipo_usuario": "1", "correo": "ala.cruz@duocuc.cl", "telefono": "9 63506091"},
    { "id": 3, "nombre": "Matías", "apellido_p": "Millaqueo", "apellido_m": "Uribe", "tipo_usuario": "1", "correo": "mat.millaqueo@duocuc.cl", "telefono": "9 37728606"},
    { "id": 4, "nombre": "Jorge", "apellido_p": "González", "apellido_m": "Uribe", "tipo_usuario": "1", "correo": "jo.gonzalezu@duoc.cl", "telefono": "9 62309465"},
]

# Array / Diccionario de productos de Ferremas
productos = [
    {"id": 1, "nombre": "Tornillo", "descripcion": "Es solo un tornillo XD", "imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcThsl8m9Wl6HIwhotCCaqRRiqqWyr3JUqpHFQ&s", "precio": "500", "stock": "10", "categoria": "1"},
    {"id": 2, "nombre": "Tuerca", "descripcion": "Hace juego con el tornillo", "imagen": "https://pernogom.cl/wp-content/uploads/2023/09/tuerca-hex.jpg", "precio": "300", "stock": "15", "categoria": "1"},
    {"id": 3, "nombre": "Destornillador", "descripcion": "Para atornillar", "imagen": "https://aritrans.cl/wp-content/uploads/2022/04/STHT69148.jpg", "precio": "1500", "stock": "5", "categoria": "2"},
]


'''
    GET         -> Obtener información
    POST        -> Crear información
    PUT         -> Actualizar información
    DELETE      -> Borrar información
'''
# Endpoint para obtener todos los tipos de usuarios de la web de Ferremas
@app.route("/get_tiposusuarios/", methods=['GET'])
def get_tipos_usuarios():
    return Response(json.dumps(tipos_usuarios), mimetype='application/json')


# Endpoint para obtener todos los usuarios
@app.route("/get_usuarios/", methods=['GET'])
def get_usuarios():
    return Response(json.dumps(usuarios), mimetype='application/json')


# Endpoint para obtener todos los productos
@app.route("/get_productos/", methods=['GET'])
def get_productos():
    return Response(json.dumps(productos), mimetype='application/json')


# Endpoint para obtener un producto según su id
@app.route("/get_producto/<int:id>", methods=['GET'])
def get_producto(id):
    for producto in productos:
        if id == producto["id"]:
            response = Response(json.dumps(producto), mimetype='application/json')
            return response
    return jsonify({"error": "Producto no encontrado"}), 404


if __name__ =='__main__':
    app.run(debug=True)