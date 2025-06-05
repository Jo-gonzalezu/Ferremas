from flask import Flask, render_template, request, jsonify, Response, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import check_password_hash
import json

app = Flask(__name__)
app.secret_key = 'una_clave_secreta_super_segura_'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ferremas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#region MODELOS DE BASE DE DATOS (TABLAS)
# Modelo de tabla tipos de usuario
class TipoUsuario(db.Model):
    __tablename__ = 'tipos_usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

# Modelo de tabla usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_p = db.Column(db.String(100), nullable=False)
    apellido_m = db.Column(db.String(100), nullable=False)
    tipo_usuario = db.Column(db.Integer, db.ForeignKey('tipos_usuarios.id'), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))

# Modelo de tabla tipos de productos
class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)

# Creamos la base de datos
with app.app_context():
    db.create_all()
#endregion




'''
    GET         -> Obtener información
    POST        -> Crear información
    PUT         -> Actualizar información
    DELETE      -> Borrar información
'''

#region APIS, ENDPOINTS
# PATH, URL DE INICIO SESION
@app.route("/")
def root():
    # Consulta todos los productos de la base 
    productos = Producto.query.all()
    
    data = {
        "titulo": "Inicio sesión",
        "productos": productos
    }

    return render_template("login.html", data=data)


@app.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()

    correo = data.get('correo')
    contraseña = data.get('contraseña')

    if not correo or not contraseña:
        return jsonify({'message': 'Correo y contraseña son requeridos 😿'}), 400

    # Consulta SQL
    sql = "SELECT * FROM usuarios WHERE correo = :correo"
    result = db.session.execute(db.text(sql), {'correo': correo}).fetchone()

    if result:
        hash_guardado = result[6]  # Asegúrate que esta sea la columna correcta (contraseña)
        if check_password_hash(hash_guardado, contraseña):
            session['usuario_id'] = result[0]  # id
            session['rol'] = 'usuario'
            return jsonify({
                'message': 'Login exitoso 🎉',
                'usuario': {
                    'id': result[0],
                    'nombre': result[1],
                    'apellido_p': result[2],
                    'apellido_m': result[3],
                    'correo': result[5],
                    'telefono': result[7],
                    'tipo_usuario': result[4]
                }
            }), 200
        else:
            return jsonify({'message': 'Contraseña incorrecta 😿'}), 401
    else:
        return jsonify({'message': 'Correo no encontrado 😿'}), 404



# PATH, URL DE INICIO
@app.route("/inicio")
def dashboard():
    usuario_id = session.get('usuario_id')
    rol = session.get('rol', 'usuario')

    if usuario_id is None and rol != 'invitado':
        return redirect(url_for('root'))

    data_usuario = None
    es_admin = False

    if usuario_id:
        sql = text("SELECT * FROM usuarios WHERE id = :usuario_id")
        result = db.session.execute(sql, {'usuario_id': usuario_id}).fetchone()
        if not result:
            return redirect(url_for('root'))

        data_usuario = {
            'id': result[0],
            'nombre': result[1],
            'apellido_p': result[2],
            'apellido_m': result[3],
            'tipo_usuario': result[4],
            'correo': result[5],
            'contraseña': result[6],
            'telefono': result[7]
        }

        es_admin = data_usuario['tipo_usuario'] == 1
    else:
        # Usuario invitado 
        data_usuario = {
            'nombre': 'Invitado',
            'apellido_p': '',
            'apellido_m': '',
            'tipo_usuario': 'invitado',
            'correo': '',
            'telefono': ''
        }

    data = {
        "titulo": "Dashboard",
        "usuario": data_usuario,
        "es_admin": es_admin
    }

    return render_template("inicio.html", data=data)

@app.route('/invitado', methods=['POST'])
def invitado():
    session['usuario_id'] = None
    session['rol'] = 'invitado'
    return redirect(url_for('dashboard'))  # Asegúrate que la función /inicio se llama dashboard
    # O usa: return redirect('/inicio')  # Funciona si /inicio es tu URL válida




@app.route("/inventario")
def inventario():
    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        return redirect(url_for('root'))

    sql = text("SELECT * FROM usuarios WHERE id = :usuario_id")
    result = db.session.execute(sql, {'usuario_id': usuario_id}).fetchone()
    if not result:
        return redirect(url_for('root'))

    data_usuario = {
        'id': result[0], 'nombre': result[1], 'apellido_p': result[2],
        'apellido_m': result[3], 'tipo_usuario': result[4], 'correo': result[5],
        'contraseña': result[6], 'telefono': result[7]
    }

    # Consulta SQL para obtener todos los productos 
    productos_query = text("SELECT id, nombre, descripcion, imagen, precio, stock, categoria FROM productos")
    productos_result = db.session.execute(productos_query).fetchall()

    # Convertir resultados a lista de diccionarios 
    productos = []
    for p in productos_result:
        productos.append({
            'id': p[0], 'nombre': p[1], 'descripcion': p[2],
            'imagen': p[3], 'precio': p[4], 'stock': p[5], 'categoria': p[6]
        })

    data = {
        "titulo": "Inventario",
        "usuario": data_usuario,
        "modulo": "Inventario",
        "productos": productos
    }

    return render_template("inventario.html", data=data)



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
    sql = text("SELECT * FROM productos")
    result = db.session.execute(sql).fetchall()

    # Convertimos los resultados a una lista de diccionarios 
    productos = []
    for r in result:
        producto = {
            'id': r[0],
            'nombre': r[1],
            'descripcion': r[2],
            'imagen': r[3],
            'precio': r[4],
            'stock': r[5],
            'categoria': r[6]
        }
        productos.append(producto)

    return jsonify(productos)

# Endpoint para buscar productos por el buscador
@app.route('/api/buscar_productos', methods=['GET'])
def buscar_productos():
    texto = request.args.get('q')  # El parámetro de búsqueda 

    if not texto:
        return jsonify({'message': 'Por favor proporciona un texto para buscar '}), 400

    # Consulta SQL usando LIKE para buscar coincidencias 
    sql = text("SELECT * FROM productos WHERE nombre LIKE :texto OR descripcion LIKE :texto")
    result = db.session.execute(sql, {'texto': f'%{texto}%'}).fetchall()

    productos = []
    for r in result:
        producto = {
            'id': r[0],
            'nombre': r[1],
            'descripcion': r[2],
            'imagen': r[3],
            'precio': r[4],
            'stock': r[5],
            'categoria': r[6]
        }
        productos.append(producto)

    return jsonify(productos)

# Endpoint para obtener un producto según su id
@app.route("/get_producto/<int:id>", methods=['GET'])
def get_producto(id):
    for producto in productos:
        if id == producto["id"]:
            response = Response(json.dumps(producto), mimetype='application/json')
            return response
    return jsonify({"error": "Producto no encontrado"}), 404


# CARRITO DE COMPRA JEJE
@app.route('/add_to_cart/<int:producto_id>', methods=['POST'])
def add_to_cart(producto_id):
    
    # Consulta SQL para buscar todos los productos
    sql = text("SELECT * FROM productos WHERE id = :producto_id")
    result = db.session.execute(sql, {'producto_id': producto_id}).fetchone()

    if not result:
        return jsonify({'message': 'Producto no encontrado 😿'}), 404

    # Crear un diccionario del producto 
    producto = {
        'id': result[0],
        'nombre': result[1],
        'descripcion': result[2],
        'imagen': result[3],
        'precio': result[4],
        'stock': result[5],
        'categoria': result[6]
    }

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']

    for item in cart:
        if item['id'] == producto_id:
            item['cantidad'] += 1
            session.modified = True
            total_items = sum(i['cantidad'] for i in cart)
            return jsonify({'message': 'Producto agregado al carrito 🛒', 'total_items': total_items})

    cart.append({
        'id': producto['id'],
        'nombre': producto['nombre'],
        'precio': producto['precio'],
        'imagen': producto['imagen'],
        'cantidad': 1
    })

    session['cart'] = cart
    total_items = sum(i['cantidad'] for i in cart)
    return jsonify({'message': 'Producto agregado al carrito 🛒', 'total_items': total_items})


@app.route('/remove_from_cart/<int:producto_id>', methods=['POST'])
def remove_from_cart(producto_id):
    cart = session.get('cart', [])
    # Filtramos el carrito para quitar el producto con ese ID
    cart = [item for item in cart if item['id'] != producto_id]
    session['cart'] = cart
    session.modified = True
    return jsonify({'message': 'Producto eliminado del carrito 🗑️'})


@app.route('/carrito')
def carrito():
    cart = session.get('cart', [])
    total = sum(item['precio'] * item['cantidad'] for item in cart)
    return render_template('carrito.html', cart=cart, total=total)


@app.route('/reset_cart')
def reset_cart():
    session.pop('cart', None)
    return "Carrito reiniciado"

@app.route('/realizar_compra', methods=['POST'])
def realizar_compra():
    # Si usas session para el carrito
    carrito = session.get('cart', [])

    if not carrito:
        return jsonify({'message': 'El carrito está vacío '}), 400

    try:
        for item in carrito:
            producto_id = item['id']
            cantidad = item['cantidad']

            # Verificar si hay suficiente stock 
            stock_actual = db.session.execute(text("SELECT stock FROM productos WHERE id = :id"), {'id': producto_id}).fetchone()[0]
            if stock_actual < cantidad:
                return jsonify({'message': f'No hay suficiente stock para {item["nombre"]} 😿'}), 400
                
            # Descontar stock 
            db.session.execute(text("UPDATE productos SET stock = stock - :cantidad WHERE id = :id"), {'cantidad': cantidad, 'id': producto_id})
        
        db.session.commit()
        session.pop('cart', None)
        return jsonify({'message': 'Compra realizada con éxito 🎉'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al procesar la compra: {str(e)} 😿'}), 500

@app.route('/agregar_stock/<int:producto_id>/<int:cantidad>', methods=['POST'])
def agregar_stock(producto_id, cantidad):
    sql = text("UPDATE productos SET stock = stock + :cantidad WHERE id = :id")
    db.session.execute(sql, {'cantidad': cantidad, 'id': producto_id})
    db.session.commit()

    # Obtener nuevo stock
    sql_nuevo = text("SELECT stock FROM productos WHERE id = :id")
    nuevo_stock = db.session.execute(sql_nuevo, {'id': producto_id}).fetchone()[0]
    return jsonify({'message': f'Se agregó {cantidad} unidades al stock.', 'nuevo_stock': nuevo_stock})


@app.route('/eliminar_producto/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    sql = text("DELETE FROM productos WHERE id = :id")
    db.session.execute(sql, {'id': producto_id})
    db.session.commit()
    return jsonify({'message': 'Producto eliminado correctamente.'})
#endregion

if __name__ =='__main__':
    app.run(debug=True)