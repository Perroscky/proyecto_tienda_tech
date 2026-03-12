# app.py - VERSIÓN COMPLETA Y CORREGIDA

from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.inventario import Inventario
from models.usuario import Usuario
from database.db_manager import DatabaseManager

app = Flask(__name__)
app.secret_key = 'clave_secreta_proyecto_tienda_tech'

# Inicializar componentes
inventario = Inventario()
db = DatabaseManager()

# ----- RUTAS PÚBLICAS -----
@app.route('/')
def inicio():
    """Página principal"""
    productos = inventario.obtener_todos()
    
    productos_template = {}
    for prod in productos:
        key = prod.nombre.lower().replace(' ', '_').replace('"', '').replace("'", '')
        productos_template[key] = {
            'id': prod.id,
            'nombre': prod.nombre,
            'precio': f"${prod.precio:.2f}",
            'stock': 'Disponible' if prod.cantidad > 5 else 'Stock Limitado' if prod.cantidad > 0 else 'Agotado',
            'descripcion': prod.descripcion,
            'cantidad_real': prod.cantidad
        }
    
    return render_template('index.html', productos=productos_template)

@app.route('/producto/<nombre>')
def producto(nombre):
    """Ver detalle de un producto"""
    nombre_lower = nombre.lower().replace('_', ' ')
    productos_encontrados = inventario.buscar_productos(nombre_lower)
    
    if productos_encontrados:
        prod = productos_encontrados[0]
        prod_dict = {
            'id': prod.id,
            'nombre': prod.nombre,
            'precio': f"${prod.precio:.2f}",
            'stock': 'Disponible' if prod.cantidad > 5 else 'Stock Limitado' if prod.cantidad > 0 else 'Agotado',
            'descripcion': prod.descripcion,
            'cantidad': prod.cantidad,
            'categoria': prod.categoria
        }
        return render_template('producto.html', prod=prod_dict)
    else:
        return render_template('404_producto.html', nombre=nombre), 404

@app.route('/categoria/<tipo>')
def categoria(tipo):
    """Ver productos por categoría"""
    categorias_validas = Inventario.CATEGORIAS_VALIDAS
    tipo_lower = tipo.lower()
    
    if tipo_lower in categorias_validas:
        productos_categoria = inventario.obtener_por_categoria(tipo_lower)
        return render_template('categoria.html', tipo=tipo_lower, 
                             productos=productos_categoria, 
                             hay_productos=len(productos_categoria) > 0)
    else:
        return render_template('404_categoria.html', tipo=tipo), 404

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ----- RUTAS DE AUTENTICACIÓN -----
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevos usuarios"""
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            fecha = request.form.get('fecha_nacimiento', '').strip()
            
            # Validaciones
            if not all([nombre, email, password, fecha]):
                flash('Todos los campos son obligatorios', 'error')
                return render_template('registro.html')
            
            if not Usuario.validar_email(email):
                flash('El formato del email no es válido', 'error')
                return render_template('registro.html')
            
            # Crear usuario
            usuario = Usuario(None, nombre, email, password, fecha)
            
            # Guardar en sesión
            session['usuario_id'] = 1  # Temporal
            session['usuario_nombre'] = usuario.nombre
            session['usuario_email'] = usuario.email
            
            flash(f'¡Bienvenido {usuario.nombre}!', 'success')
            return redirect(url_for('inicio'))
                
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'error')
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if email:
            session['usuario_id'] = 1
            session['usuario_nombre'] = email.split('@')[0]
            session['usuario_email'] = email
            flash(f'¡Bienvenido!', 'success')
            return redirect(url_for('inicio'))
        
        flash('Email es obligatorio', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('inicio'))

# ----- RUTAS DEL CARRITO (CORREGIDAS) -----
@app.route('/agregar_al_carrito/<int:producto_id>')
def agregar_al_carrito(producto_id):
    """Agrega un producto al carrito"""
    producto = inventario.obtener_producto_por_id(producto_id)
    
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('inicio'))
    
    # Inicializar carrito si no existe
    if 'carrito' not in session:
        session['carrito'] = {
            'items': {},
            'total': 0,
            'cantidad_items': 0
        }
    
    # Obtener carrito actual
    carrito = session['carrito']
    producto_id_str = str(producto_id)
    
    # Agregar o actualizar producto
    if producto_id_str in carrito['items']:
        carrito['items'][producto_id_str]['cantidad'] += 1
        carrito['items'][producto_id_str]['subtotal'] = carrito['items'][producto_id_str]['cantidad'] * producto.precio
    else:
        carrito['items'][producto_id_str] = {
            'producto_id': producto_id,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'cantidad': 1,
            'subtotal': producto.precio
        }
    
    # Recalcular totales
    total = 0
    cantidad_total = 0
    for item in carrito['items'].values():
        total += item['subtotal']
        cantidad_total += item['cantidad']
    
    carrito['total'] = total
    carrito['cantidad_items'] = cantidad_total
    
    # Guardar en sesión
    session['carrito'] = carrito
    session.modified = True
    
    flash(f'{producto.nombre} agregado al carrito', 'success')
    return redirect(url_for('ver_carrito'))

@app.route('/carrito')
def ver_carrito():
    """Ver el contenido del carrito"""
    if 'carrito' not in session:
        session['carrito'] = {
            'items': {},
            'total': 0,
            'cantidad_items': 0
        }
    return render_template('carrito.html', carrito=session['carrito'])

@app.route('/actualizar_carrito/<int:producto_id>', methods=['POST'])
def actualizar_carrito(producto_id):
    """Actualizar cantidad de un producto en el carrito"""
    cantidad = int(request.form.get('cantidad', 0))
    
    if 'carrito' in session:
        carrito = session['carrito']
        producto_id_str = str(producto_id)
        
        if producto_id_str in carrito['items']:
            if cantidad <= 0:
                del carrito['items'][producto_id_str]
                flash('Producto eliminado del carrito', 'success')
            else:
                carrito['items'][producto_id_str]['cantidad'] = cantidad
                carrito['items'][producto_id_str]['subtotal'] = cantidad * carrito['items'][producto_id_str]['precio']
            
            # Recalcular totales
            total = 0
            cantidad_total = 0
            for item in carrito['items'].values():
                total += item['subtotal']
                cantidad_total += item['cantidad']
            
            carrito['total'] = total
            carrito['cantidad_items'] = cantidad_total
            session['carrito'] = carrito
            session.modified = True
    
    return redirect(url_for('ver_carrito'))

@app.route('/eliminar_del_carrito/<int:producto_id>')
def eliminar_del_carrito(producto_id):
    """Eliminar un producto del carrito"""
    if 'carrito' in session:
        carrito = session['carrito']
        producto_id_str = str(producto_id)
        
        if producto_id_str in carrito['items']:
            del carrito['items'][producto_id_str]
            
            # Recalcular totales
            total = 0
            cantidad_total = 0
            for item in carrito['items'].values():
                total += item['subtotal']
                cantidad_total += item['cantidad']
            
            carrito['total'] = total
            carrito['cantidad_items'] = cantidad_total
            session['carrito'] = carrito
            session.modified = True
            flash('Producto eliminado del carrito', 'success')
    
    return redirect(url_for('ver_carrito'))

@app.route('/finalizar_compra')
def finalizar_compra():
    """Finalizar la compra"""
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para finalizar la compra', 'error')
        return redirect(url_for('login'))
    
    if 'carrito' not in session or not session['carrito'].get('items'):
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('ver_carrito'))
    
    flash('¡Compra realizada con éxito!', 'success')
    session.pop('carrito', None)
    return redirect(url_for('inicio'))

# ----- MANEJADORES DE ERRORES -----
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_producto.html', nombre='página'), 404

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Servidor iniciado correctamente")
    print("📱 Accede a: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)