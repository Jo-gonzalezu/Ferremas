document.addEventListener('DOMContentLoaded', () => {
    // Detectar si estamos en una página con formulario de login
    const form = document.querySelector('#login-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const correo = document.querySelector('#email').value;
            const contraseña = document.querySelector('#password').value;

            const data = { correo, contraseña };

            try {
                const response = await fetch('/login', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Login exitoso! 🎉',
                        text: result.message
                    }).then(() => {
                        window.location.href = '/home';  // Redirige a la página de productos
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error 😿',
                        text: result.message
                    });
                }

            } catch (err) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error de red 😿',
                    text: 'No se pudo conectar con el servidor'
                });
            }
        });
    }

    // Detectar si estamos en la página de productos (home)
    const productosLista = document.getElementById('productos-lista');
    if (productosLista) {
        cargarProductos();  // Función para cargar los productos
    }

    actualizarContadorCarrito();
});

function mostrarCarrito() {
    document.getElementById('cart-sidebar').classList.add('show');
    document.getElementById('cart-overlay').classList.add('show');
    cargarCarrito();
}
function ocultarCarrito() {
    document.getElementById('cart-sidebar').classList.remove('show');
    document.getElementById('cart-overlay').classList.remove('show');
}


async function cargarProductos() {
    const productosLista = document.getElementById('productos-lista');
    const response = await fetch('/get_productos/');
    const productos = await response.json();

    productosLista.innerHTML = '';
    productos.forEach(producto => {
        const productoHTML = `
        <div class="col">
            <div class="card h-100">
                <img src="${producto.imagen}" class="card-img-top" alt="${producto.nombre}">
                <div class="card-body">
                    <h5 class="card-title">${producto.nombre} 🛠️</h5>
                    <p class="card-text">${producto.descripcion}</p>
                    <p class="card-text"><strong>$${producto.precio.toFixed(2)}</strong></p>
                    <button class="btn btn-success" onclick="agregarAlCarrito(${producto.id})">Agregar al carrito 🛒</button>
                </div>
            </div>
        </div>`;
        productosLista.innerHTML += productoHTML;
    });
}

async function agregarAlCarrito(productoId) {
    const response = await fetch(`/add_to_cart/${productoId}`, { method: 'POST' });
    const result = await response.json();
    Swal.fire({ icon: 'success', title: '¡Agregado! 🎉', text: result.message });
    actualizarContadorCarrito(result.total_items);
}

async function actualizarContadorCarrito(forzado = null) {
    const contador = document.getElementById('cart-count');
    if (forzado !== null) {
        contador.textContent = forzado;
        return;
    }
    const response = await fetch('/carrito');
    if (response.ok) {
        const texto = await response.text();
        const coincidencias = texto.match(/Cantidad: (\d+)/g);
        const total = coincidencias ? coincidencias.length : 0;
        contador.textContent = total;
    }
}

function limpiarContadorCarrito() {
    const contador = document.getElementById('cart-count');
    if (contador) {
        contador.textContent = '0';  // Reinicia el contador a 0
    }
}

async function reiniciarCarrito() {
    const response = await fetch('/reset_cart');
    if (response.ok) {
        Swal.fire('Carrito reiniciado 🗑️', 'Se ha vaciado el carrito', 'success');
        limpiarContadorCarrito();
        ocultarCarrito();  // Si usas el panel lateral
    }
}



async function cargarCarrito() {
    const response = await fetch('/carrito');
    const texto = await response.text();
    const cartItems = document.getElementById('cart-items');
    const totalElement = document.getElementById('cart-total');

    const parser = new DOMParser();
    const doc = parser.parseFromString(texto, 'text/html');
    const items = doc.querySelectorAll('.list-group-item');
    const total = doc.querySelector('h3')?.textContent?.match(/\d+/g)?.[0] || '0';

    cartItems.innerHTML = '';
    items.forEach(item => {
        const productoId = item.getAttribute('data-id');  // 🔎 Obtenemos el id real
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerHTML = item.innerHTML + ` <button class="btn btn-danger btn-sm float-end" onclick="eliminarDelCarrito(${productoId})">Eliminar 🗑️</button>`;
        cartItems.appendChild(li);
    });
    totalElement.textContent = total;
}

async function eliminarDelCarrito(productoId) {
    if (!productoId) return;
    const response = await fetch(`/remove_from_cart/${productoId}`, { method: 'POST' });
    const result = await response.json();
    Swal.fire('Producto eliminado 🗑️', result.message, 'success');
    cargarCarrito();
    actualizarContadorCarrito();
}


// 🔎 Función para obtener el ID del producto por su nombre (puedes mejorarla si tienes otro identificador)
function obtenerIdPorNombre(nombreProducto) {
    const productos = [
        { id: 1, nombre: "Martillo carpintero" },
        { id: 2, nombre: "Destornillador plano" },
        { id: 3, nombre: "Llave inglesa" },
        // ... completa con tu lista de productos
    ];
    const producto = productos.find(p => p.nombre === nombreProducto);
    return producto ? producto.id : null;
}

function confirmarCompra() {
    Swal.fire('¡Compra confirmada! 🎉', 'Gracias por tu compra', 'success');
    ocultarCarrito();
}