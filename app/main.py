from flask import Flask, render_template, request, jsonify, Response, session
import json

app = Flask(__name__)
app.secret_key = 'una_clave_secreta_super_segura_uwu'

# Array / Diccionario de tipos de usuario en la web de Ferremas
tipos_usuarios = [
    {"id": 1, "nombre": "Administrador"},
    {"id": 2, "nombre": "Empleado"},
    {"id": 3, "nombre": "Cliente"},
]

# Array / Diccionario de usuarios de Ferremas
usuarios = [
    { "id": 1, "nombre": "Constanza", "apellido_p": "Olivares", "apellido_m": "Leon", "tipo_usuario": "1", "correo": "co.olivaresl@duocuc.cl", "contraseña": "123conny", "telefono": "9 20370693"},
    { "id": 2, "nombre": "Alan", "apellido_p": "Cruz", "apellido_m": "Baeza", "tipo_usuario": "1", "correo": "ala.cruz@duocuc.cl", "contraseña": "123alan", "telefono": "9 63506091"},
    { "id": 3, "nombre": "Matías", "apellido_p": "Millaqueo", "apellido_m": "Uribe", "tipo_usuario": "1", "correo": "mat.millaqueo@duocuc.cl", "contraseña": "123matias", "telefono": "9 37728606"},
    { "id": 4, "nombre": "Jorge", "apellido_p": "González", "apellido_m": "Uribe", "tipo_usuario": "1", "correo": "jo.gonzalezu@duoc.cl", "contraseña": "123jorge", "telefono": "9 62309465"},
]

# Array / Diccionario de productos de Ferremas
productos = [
    {"id": 1, "nombre": "Martillo carpintero", "descripcion": "Martillo para trabajos de carpintería", "imagen": "https://rgm.vtexassets.com/arquivos/ids/156235-800-auto?v=638554617786370000&width=800&height=auto&aspect=true", "precio": 2500, "stock": 40, "categoria": "Herramientas"},
    {"id": 2, "nombre": "Destornillador plano", "descripcion": "Destornillador para tornillos planos", "imagen": "https://media.falabella.com/falabellaCL/133814803_01/w=1500,h=1500,fit=pad", "precio": 1500, "stock": 50, "categoria": "Herramientas"},
    {"id": 3, "nombre": "Llave inglesa", "descripcion": "Llave ajustable para tuercas y tornillos", "imagen": "https://pernoval.cl/25803-large_default/llave_inglesa_tubo_36_730011_onsite.webp", "precio": 3500, "stock": 30, "categoria": "Herramientas"},
    {"id": 4, "nombre": "Alicate universal", "descripcion": "Alicate multifuncional", "imagen": "https://www.weitzler.cl/bitobee/wp-content/uploads/2022/11/65002100003.jpg", "precio": 1800, "stock": 35, "categoria": "Herramientas"},
    {"id": 5, "nombre": "Taladro eléctrico", "descripcion": "Taladro para trabajos de perforación", "imagen": "https://media.falabella.com/sodimacCL/7404727_01/w=800,h=800,fit=pad", "precio": 15000, "stock": 20, "categoria": "Herramientas"},
    {"id": 6, "nombre": "Sierra manual", "descripcion": "Sierra para cortar madera y metales", "imagen": "https://m.media-amazon.com/images/I/51MSueHHHqL._AC_UF894,1000_QL80_.jpg", "precio": 4000, "stock": 25, "categoria": "Herramientas"},
    {"id": 7, "nombre": "Cinta métrica", "descripcion": "Cinta para mediciones precisas", "imagen": "https://cdnx.jumpseller.com/my-toolbox-chile/image/42833863/d_nq_np_2x_820651-mlc40854154766_022020-f-8cff2697-107e-4579-baa7-b830d0424250.jpg?1732308296", "precio": 1200, "stock": 60, "categoria": "Medición"},
    {"id": 8, "nombre": "Nivel de burbuja", "descripcion": "Nivel para verificar alineaciones", "imagen": "https://www.demaquinasyherramientas.com/wp-content/uploads/2013/05/nivel-de-burbuja.jpg", "precio": 2200, "stock": 40, "categoria": "Medición"},
    {"id": 9, "nombre": "Juego de llaves Allen", "descripcion": "Llaves para tornillos hexagonales", "imagen": "https://pimdatacdn.bahco.com/media/sub478/16a0151e27fe543f.png", "precio": 1800, "stock": 45, "categoria": "Herramientas"},
    {"id": 10, "nombre": "Broca para metal", "descripcion": "Broca resistente para metales", "imagen": "https://isesacl.vtexassets.com/arquivos/ids/158475/broca_metal_acero_hss_super_alpen_1.jpg?v=637200563366370000", "precio": 800, "stock": 80, "categoria": "Accesorios"},
    {"id": 11, "nombre": "Broca para madera", "descripcion": "Broca especial para madera", "imagen": "https://isesacl.vtexassets.com/arquivos/ids/155792/broca_madera_hss_cv_profi_holz_alpen_1_9.jpg?v=637178017193230000", "precio": 700, "stock": 70, "categoria": "Accesorios"},
    {"id": 12, "nombre": "Caja de herramientas", "descripcion": "Caja organizadora con compartimentos", "imagen": "https://dojiw2m9tvv09.cloudfront.net/40644/product/178262eeaa60843f4935.png", "precio": 5000, "stock": 25, "categoria": "Organización"},
    {"id": 13, "nombre": "Guantes de trabajo", "descripcion": "Guantes resistentes para protección", "imagen": "https://importadoradali.cl/wp-content/uploads/2023/07/Guante-de-trabajo-verde-Pack-12-pares.jpg", "precio": 900, "stock": 100, "categoria": "Protección"},
    {"id": 14, "nombre": "Casco de seguridad", "descripcion": "Casco para protección en obra", "imagen": "https://allstorechile.cl/wp-content/uploads/2024/05/42301023V.jpg", "precio": 3200, "stock": 30, "categoria": "Protección"},
    {"id": 15, "nombre": "Cinta aislante", "descripcion": "Cinta para aislamiento eléctrico", "imagen": "https://cdnx.jumpseller.com/ferreteria-sur/image/7819827/5-rollos-cinta-aislante-pvc-negro-25mx50mm.jpg?1616694599", "precio": 300, "stock": 200, "categoria": "Accesorios"},
    {"id": 16, "nombre": "Corta cartón", "descripcion": "Cúter para cortes precisos", "imagen": "https://www.dateriumsystem.com/appfiles/clientes/308/catalogo/CUTTER-CUCHILLA-FRAGMENTABLE-18-MM-GUIA-METALICA-ALYCO-170814-PRINCIPAL.jpg", "precio": 800, "stock": 50, "categoria": "Herramientas"},
    {"id": 17, "nombre": "Espátula", "descripcion": "Espátula para trabajos de pintura", "imagen": "https://passol.cl/cdn/shop/files/Espatulamangomadera80mm.jpg?v=1730933552&width=1214", "precio": 700, "stock": 60, "categoria": "Pintura"},
    {"id": 18, "nombre": "Rodillo para pintura", "descripcion": "Rodillo para pintar paredes", "imagen": "https://cdnx.jumpseller.com/ferroelectronic/image/55585645/resize/540/600?1729776548", "precio": 1100, "stock": 40, "categoria": "Pintura"},
    {"id": 19, "nombre": "Brocha", "descripcion": "Brocha para detalles de pintura", "imagen": "https://caribebrochasyherramientas.com/wp-content/uploads/2021/09/Bro-prof-4-lat-sin-emp-alta.jpg", "precio": 600, "stock": 50, "categoria": "Pintura"},
    {"id": 20, "nombre": "Lija", "descripcion": "Lija para alisar superficies", "imagen": "https://multimedia.3m.com/mws/media/1026186J/sandpaper-211q-picture.jpg?width=506", "precio": 400, "stock": 100, "categoria": "Pintura"},
    {"id": 21, "nombre": "Disco de corte", "descripcion": "Disco para corte de metales", "imagen": "https://isesacl.vtexassets.com/arquivos/ids/160358/disco_corte_rasta_9in_metal_universal_acero_3215_1.jpg?v=637357997678170000", "precio": 1500, "stock": 35, "categoria": "Accesorios"},
    {"id": 22, "nombre": "Amoladora angular", "descripcion": "Herramienta para cortes y desbastes", "imagen": "https://isesacl.vtexassets.com/arquivos/ids/160358/disco_corte_rasta_9in_metal_universal_acero_3215_1.jpg?v=637357997678170000", "precio": 12000, "stock": 15, "categoria": "Herramientas"},
    {"id": 23, "nombre": "Tornillo 1/2", "descripcion": "Tornillo resistente para estructuras", "imagen": "https://dojiw2m9tvv09.cloudfront.net/44838/product/X_volcanitapuntafinazincado6x15-89789.jpg?1223&time=1747022726", "precio": 500, "stock": 150, "categoria": "Fijación"},
    {"id": 24, "nombre": "Tuerca 1/2", "descripcion": "Tuerca para tornillos de 1/2", "imagen": "https://multistock.com.pe/cdn/shop/products/cara-5_-negro-8x7.8_85691c6d-fb08-4686-a784-8c5f533ef203_1024x.jpg?v=1613499831", "precio": 300, "stock": 200, "categoria": "Fijación"},
    {"id": 25, "nombre": "Arandela", "descripcion": "Arandela para distribuir carga", "imagen": "https://www.dimarine.cl/media/catalog/product/m/a/marcasyamaha9299010200-plateado1jpeg_0.jpg", "precio": 200, "stock": 300, "categoria": "Fijación"},
]

'''
    GET         -> Obtener información
    POST        -> Crear información
    PUT         -> Actualizar información
    DELETE      -> Borrar información
'''
@app.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()

    correo = data.get('correo')
    contraseña = data.get('contraseña')

    if not correo or not contraseña:
        return jsonify({'message': 'Correo y contraseña son requeridos'}), 400

    # Buscar usuario que coincida
    usuario = next((u for u in usuarios if u['correo'] == correo and u['contraseña'] == contraseña), None)

    if usuario:
        session['usuario_id'] = usuario['id'];
        return jsonify({
            'message': 'Login exitoso 🎉',
            'usuario': {
                'id': usuario['id'],
                'nombre': usuario['nombre'],
                'apellido_p': usuario['apellido_p'],
                'apellido_m': usuario['apellido_m'],
                'correo': usuario['correo'],
                'telefono': usuario['telefono'],
                'tipo_usuario': usuario['tipo_usuario']
            }
        }), 200
    else:
        return jsonify({'message': 'Correo o contraseña incorrectos 😿'}), 401

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
    return jsonify(productos)


# Endpoint para obtener un producto según su id
@app.route("/get_producto/<int:id>", methods=['GET'])
def get_producto(id):
    for producto in productos:
        if id == producto["id"]:
            response = Response(json.dumps(producto), mimetype='application/json')
            return response
    return jsonify({"error": "Producto no encontrado"}), 404

# PATH, URL DE INICIO SESION
@app.route("/")
def root():
    
    data = {
        "titulo" : "Inicio sesión",
        "productos" : productos
    }

    return render_template("login.html", data=data)

# PATH, URL DE INICIO
@app.route("/home")
def dashboard():
    usuario_id = session.get('usuario_id')
    if usuario_id is None:
        return redirect(url_for('root'))

    # Buscar el usuario por ID
    data_usuario = next((u for u in usuarios if u['id'] == usuario_id), None)

    data = {
        "titulo": "Dashboard",
        "usuario": data_usuario
    }
    return render_template("home.html", data=data)

# CARRITO DE COMPRA JEJE
@app.route('/add_to_cart/<int:producto_id>', methods=['POST'])
def add_to_cart(producto_id):
    producto = next((p for p in productos if p['id'] == producto_id), None)
    if not producto:
        return jsonify({'message': 'Producto no encontrado 😿'}), 404

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']

    for item in cart:
        if item['id'] == producto_id:
            item['cantidad'] += 1
            session.modified = True
            total_items = sum(i['cantidad'] for i in cart)
            return jsonify({'message': 'Producto agregado al carrito 🛒', 'total_items': total_items})

    # Agregando todos los atributos del objeto para ser utilizados
    cart.append({'id': producto_id, 'nombre': producto['nombre'], 'precio': producto['precio'], 'imagen': producto['imagen'], 'cantidad': 1})

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
    session.pop('cart', None)  # 💡 Elimina solo el carrito
    return "Carrito reiniciado"


if __name__ =='__main__':
    app.run(debug=True)