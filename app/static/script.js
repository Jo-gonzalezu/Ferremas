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
                        window.location.href = '/inicio';  // Redirige a la página de productos
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

    // Detectar si estamos en la página de productos (inicio)
    const productosLista = document.getElementById('productos-lista');
    if (productosLista) {
        cargarProductos();  // Cargar todos los productos al inicio 

        const buscadorForm = document.getElementById('buscador-form');
        if (buscadorForm) {
            buscadorForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const query = document.getElementById('busqueda').value.trim();
                cargarProductos(query);  // Llamamos la función con el texto de búsqueda 
            });
        }
    }

    actualizarContadorCarrito();
});

// 🌸 Controlar apertura y cierre del panel lateral
document.getElementById('open-left-panel').addEventListener('click', (e) => {
    e.stopPropagation();  // Evitar que se dispare al abrir
    document.getElementById('left-sidebar').classList.add('show');
    document.getElementById('main-content').classList.add('shifted');
});

// Función para cerrar el panel
function cerrarPanelIzquierdo() {
    document.getElementById('left-sidebar').classList.remove('show');
    document.getElementById('main-content').classList.remove('shifted');
}

// Detectar clic fuera del panel para cerrarlo
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('left-sidebar');
    const openButton = document.getElementById('open-left-panel');
    if (sidebar.classList.contains('show') && !sidebar.contains(e.target) && e.target !== openButton) {
        cerrarPanelIzquierdo();
    }
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


async function cargarProductos(query = '') {
    const productosLista = document.getElementById('productos-lista');
    let url = '/get_productos/';  // Por defecto trae todos los productos 
    if (query) {
        url = `/api/buscar_productos?q=${encodeURIComponent(query)}`;
    }

    const response = await fetch(url);
    const productos = await response.json();

    let contenidoHTML = '';

    if (productos.length === 0) {
        contenidoHTML = '<p>No se encontraron productos 😿.</p>';
    } else {
        productos.forEach(producto => {
            const claseSinStock = producto.stock === 0 ? 'sin-stock' : '';
            const botonHTML = producto.stock === 0
                ? `<button class="btn btn-secondary btn-sm w-100 mt-auto" disabled>Sin stock</button>`
                : `<button class="btn btn-success btn-sm w-100 mt-auto" onclick="agregarAlCarrito(${producto.id})">Agregar al carrito 🛒</button>`;

            contenidoHTML += `
            <div class="col">
                <div class="card h-100 shadow-sm ${claseSinStock}" style="max-width: 200px; margin: auto;">
                    <img src="${producto.imagen}" class="card-img-top img-fluid" alt="${producto.nombre}" style="height: 150px; object-fit: contain;">
                    <div class="card-body d-flex flex-column text-center" style="padding: 0.5rem;">
                        <h6 class="card-title" style="font-size: 1rem; font-weight: bold;">${producto.nombre}</h6>
                        <p class="card-text flex-grow-1" style="font-size: 0.9rem;">${producto.descripcion}</p>
                        <p class="card-text" style="font-size: 0.9rem;"><strong>$${producto.precio.toLocaleString('es-CL', { minimumFractionDigits: 0 })} CLP</strong></p>
                        <p class="card-text">Stock: ${producto.stock}</p>
                        ${botonHTML}
                    </div>
                </div>
            </div>
            `;
        });
    }

    productosLista.innerHTML = contenidoHTML;
}



async function agregarAlCarrito(productoId) {
    const response = await fetch(`/add_to_cart/${productoId}`, { method: 'POST' });
    const result = await response.json();
    //Swal.fire({ icon: 'success', title: '¡Agregado! 🎉', text: result.message });
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
    //Swal.fire('Producto eliminado 🗑️', result.message, 'success');
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

async function confirmarCompra() {
    const response = await fetch('/realizar_compra', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ carrito: JSON.parse(sessionStorage.getItem('cart') || '[]') })
    });

    const result = await response.json();
    if (response.ok) {
        Swal.fire('¡Compra confirmada! 🎉', result.message, 'success');
        ocultarCarrito();
        sessionStorage.removeItem('cart');  // Limpiar carrito local
        limpiarContadorCarrito();          // Actualizar contador 
        cargarProductos();
    } else {
        Swal.fire('❌ Error', result.message, 'error');
    }
}

async function agregarStock(productoId) {
    const { value: cantidad } = await Swal.fire({
        title: 'Agregar stock',
        input: 'number',
        inputLabel: 'Cantidad a agregar',
        inputPlaceholder: 'Ingresa cantidad',
        showCancelButton: true
    });
    
    if (cantidad && cantidad > 0) {
        const response = await fetch(`/agregar_stock/${productoId}/${cantidad}`, { method: 'POST' });
        const result = await response.json();
        if (response.ok) {
            Swal.fire('✅ Éxito', result.message, 'success');
            // Actualizar stock en la tarjeta 
            document.getElementById(`stock-${productoId}`).textContent = result.nuevo_stock;
        } else {
            Swal.fire('❌ Error', result.message, 'error');
        }
    }
}

async function eliminarProducto(productoId) {
    const confirm = await Swal.fire({
        title: '¿Estás seguro?',
        text: 'Esta acción eliminará el producto.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    });

    if (confirm.isConfirmed) {
        const response = await fetch(`/eliminar_producto/${productoId}`, { method: 'DELETE' });
        const result = await response.json();
        if (response.ok) {
            Swal.fire('✅ Producto eliminado', result.message, 'success');
            location.reload();  // Recargar la página para actualizar la lista 
        } else {
            Swal.fire('❌ Error', result.message, 'error');
        }
    }
}