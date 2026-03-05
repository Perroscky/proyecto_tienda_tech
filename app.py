# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.inventario import Inventario
from models.usuario import Usuario
from database.db_manager import DatabaseManager
import os
import json
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_proyecto_tienda_tech'
app.config['SESSION_TYPE'] = 'filesystem'

# Configuración de archivos para persistencia (Semana 12)
DATA_FOLDER = 'data'
TXT_FILE = os.path.join(DATA_FOLDER, 'productos.txt')
JSON_FILE = os.path.join(DATA_FOLDER, 'productos.json')
CSV_FILE = os.path.join(DATA_FOLDER, 'productos.csv')

# Crear carpeta data si no existe
os.makedirs(DATA_FOLDER, exist_ok=True)

# Inicializar componentes
inventario = Inventario()
db = DatabaseManager()

# Crear tablas necesarias
try:
    db.crear_tabla_usuarios()
    db.crear_tabla_carrito()
    print("✅ Tablas creadas/verificadas correctamente")
except Exception as e:
    print(f"⚠️ Error al crear tablas: {e}")

# ----- FUNCIONES PARA MANEJO DE TXT -----
def guardar_en_txt(producto):
    """Guarda un producto en archivo TXT"""
    try:
        with open(TXT_FILE, 'a', encoding='utf-8') as f:
            linea = f"{producto['id']}|{producto['nombre']}|{producto['precio']}|{producto['cantidad']}|{producto['categoria']}|{producto['descripcion']}\n"
            f.write(linea)
    except Exception as e:
        print(f"Error guardando en TXT: {e}")

def cargar_desde_txt():
    """Carga productos desde archivo TXT"""
    productos = []
    try:
        if os.path.exists(TXT_FILE):
            with open(TXT_FILE, 'r', encoding='utf-8') as f:
                for linea in f:
                    partes = linea.strip().split('|')
                    if len(partes) >= 5:
                        producto = {
                            'id': int(partes[0]),
                            'nombre': partes[1],
                            'precio': float(partes[2]),
                            'cantidad': int(partes[3]),
                            'categoria': partes[4],
                            'descripcion': partes[5] if len(partes) > 5 else ''
                        }
                        productos.append(producto)
    except Exception as e:
        print(f"Error cargando TXT: {e}")
    return productos

# ----- FUNCIONES PARA MANEJO DE JSON -----
def guardar_en_json(producto):
    """Guarda un producto en archivo JSON"""
    try:
        productos = cargar_desde_json()
        productos.append(producto)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(productos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando en JSON: {e}")

def cargar_desde_json():
    """Carga productos desde archivo JSON"""
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando JSON: {e}")
    return []

# ----- FUNCIONES PARA MANEJO DE CSV -----
def guardar_en_csv(producto):
    """Guarda un producto en archivo CSV"""
    try:
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['id', 'nombre', 'precio', 'cantidad', 'categoria', 'descripcion'])
            writer.writerow([
                producto['id'],
                producto['nombre'],
                producto['precio'],
                producto['cantidad'],
                producto['categoria'],
                producto['descripcion']
            ])
    except Exception as e:
        print(f"Error guardando en CSV: {e}")

def cargar_desde_csv():
    """Carga productos desde archivo CSV"""
    productos = []
    try:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    producto = {
                        'id': int(row['id']),
                        'nombre': row['nombre'],
                        'precio': float(row['precio']),
                        'cantidad': int(row['cantidad']),
                        'categoria': row['categoria'],
                        'descripcion': row['descripcion']
                    }
                    productos.append(producto)
    except Exception as e:
        print(f"Error cargando CSV: {e}")
    return productos

# ----- FUNCIONES PARA MANEJO DE SQLITE -----
def guardar_en_sqlite(producto):
    """Guarda un producto en SQLite usando db_manager"""
    try:
        # Verificar si el producto ya existe
        existe = db.obtener_producto_por_id(producto['id'])
        if not existe:
            from models.producto import Producto
            nuevo_producto = Producto(
                id=producto['id'],
                nombre=producto['nombre'],
                precio=producto['precio'],
                cantidad=producto['cantidad'],
                categoria=producto['categoria'],
                descripcion=producto['descripcion']
            )
            db.insertar_producto(nuevo_producto)
    except Exception as e:
        print(f"Error guardando en SQLite: {e}")

def cargar_desde_sqlite():
    """Carga productos desde SQLite"""
    productos = []
    try:
        data = db.obtener_todos_productos()
        for prod in data:
            producto = {
                'id': prod[0],
                'nombre': prod[1],
                'precio': prod[2],
                'cantidad': prod[3],
                'categoria': prod[4],
                'descripcion': prod[5] if len(prod) > 5 else ''
            }
            productos.append(producto)
    except Exception as e:
        print(f"Error cargando SQLite: {e}")
    return productos

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
    """Página de contacto"""
    return render_template('contacto.html')

@app.route('/about')
def about():
    """Página acerca de"""
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
            
            # Verificar si el email ya existe
            if db.obtener_usuario_por_email(email):
                flash('Este email ya está registrado', 'error')
                return render_template('registro.html')
            
            # Crear usuario (validación de edad dentro de la clase)
            usuario = Usuario(None, nombre, email, password, fecha)
            usuario_id = db.insertar_usuario(usuario)
            
            if usuario_id:
                session['usuario_id'] = usuario_id
                session['usuario_nombre'] = nombre
                session['usuario_email'] = email
                
                flash(f'¡Bienvenido {nombre}!', 'success')
                return redirect(url_for('inicio'))
            else:
                flash('Error al crear el usuario', 'error')
                
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
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email y contraseña son obligatorios', 'error')
            return render_template('login.html')
        
        usuario_data = db.obtener_usuario_por_email(email)
        
        if usuario_data:
            # Verificar contraseña
            if usuario_data[3] == f"enc_{password}_2026":
                session['usuario_id'] = usuario_data[0]
                session['usuario_nombre'] = usuario_data[1]
                session['usuario_email'] = usuario_data[2]
                
                flash(f'¡Bienvenido {usuario_data[1]}!', 'success')
                return redirect(url_for('inicio'))
        
        flash('Email o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('inicio'))

# ----- RUTAS DEL CARRITO -----
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
    
    # Aquí iría la lógica para procesar la compra
    flash('¡Compra realizada con éxito!', 'success')
    session.pop('carrito', None)
    return redirect(url_for('inicio'))

# ----- RUTAS PARA PERSISTENCIA (Semana 12) -----

@app.route('/datos')
def ver_datos():
    """Vista principal de gestión de datos"""
    # Cargar datos desde archivos
    datos_txt = cargar_desde_txt()
    datos_json = cargar_desde_json()
    datos_csv = cargar_desde_csv()
    datos_sqlite = cargar_desde_sqlite()
    
    return render_template('datos.html',
                         datos_txt=datos_txt,
                         datos_json=datos_json,
                         datos_csv=datos_csv,
                         datos_sqlite=datos_sqlite)

@app.route('/datos/agregar', methods=['POST'])
def agregar_producto_data():
    """Agrega un producto a todos los formatos"""
    try:
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio'))
        cantidad = int(request.form.get('cantidad'))
        categoria = request.form.get('categoria')
        descripcion = request.form.get('descripcion', '')
        
        # Generar ID único basado en timestamp
        producto_id = int(datetime.now().timestamp())
        
        producto = {
            'id': producto_id,
            'nombre': nombre,
            'precio': precio,
            'cantidad': cantidad,
            'categoria': categoria,
            'descripcion': descripcion
        }
        
        # Guardar en todos los formatos
        guardar_en_txt(producto)
        guardar_en_json(producto)
        guardar_en_csv(producto)
        guardar_en_sqlite(producto)
        
        flash('Producto guardado exitosamente en todos los formatos', 'success')
    except Exception as e:
        flash(f'Error al guardar el producto: {str(e)}', 'error')
    
    return redirect(url_for('ver_datos'))

@app.route('/datos/cargar/txt')
def cargar_txt():
    """Carga y muestra datos TXT"""
    productos = cargar_desde_txt()
    return render_template('datos_tabla.html', productos=productos, formato='TXT')

@app.route('/datos/cargar/json')
def cargar_json():
    """Carga y muestra datos JSON"""
    productos = cargar_desde_json()
    return render_template('datos_tabla.html', productos=productos, formato='JSON')

@app.route('/datos/cargar/csv')
def cargar_csv():
    """Carga y muestra datos CSV"""
    productos = cargar_desde_csv()
    return render_template('datos_tabla.html', productos=productos, formato='CSV')

@app.route('/datos/cargar/sqlite')
def cargar_sqlite():
    """Carga y muestra datos SQLite"""
    productos = cargar_desde_sqlite()
    return render_template('datos_tabla.html', productos=productos, formato='SQLite')

@app.route('/datos/exportar/txt')
def exportar_txt():
    """Exporta productos actuales a TXT"""
    try:
        productos = inventario.obtener_todos()
        with open(TXT_FILE, 'w', encoding='utf-8') as f:
            for p in productos:
                linea = f"{p.id}|{p.nombre}|{p.precio}|{p.cantidad}|{p.categoria}|{p.descripcion}\n"
                f.write(linea)
        flash('Datos exportados a TXT correctamente', 'success')
    except Exception as e:
        flash(f'Error exportando a TXT: {str(e)}', 'error')
    return redirect(url_for('ver_datos'))

@app.route('/datos/exportar/json')
def exportar_json():
    """Exporta productos actuales a JSON"""
    try:
        productos = inventario.obtener_todos()
        data = [p.to_dict() for p in productos]
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        flash('Datos exportados a JSON correctamente', 'success')
    except Exception as e:
        flash(f'Error exportando a JSON: {str(e)}', 'error')
    return redirect(url_for('ver_datos'))

@app.route('/datos/exportar/csv')
def exportar_csv():
    """Exporta productos actuales a CSV"""
    try:
        productos = inventario.obtener_todos()
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre', 'precio', 'cantidad', 'categoria', 'descripcion'])
            for p in productos:
                writer.writerow([p.id, p.nombre, p.precio, p.cantidad, p.categoria, p.descripcion])
        flash('Datos exportados a CSV correctamente', 'success')
    except Exception as e:
        flash(f'Error exportando a CSV: {str(e)}', 'error')
    return redirect(url_for('ver_datos'))

@app.route('/datos/exportar/sqlite')
def exportar_sqlite():
    """Exporta productos actuales a SQLite"""
    try:
        productos = inventario.obtener_todos()
        for p in productos:
            guardar_en_sqlite(p.to_dict())
        flash('Datos exportados a SQLite correctamente', 'success')
    except Exception as e:
        flash(f'Error exportando a SQLite: {str(e)}', 'error')
    return redirect(url_for('ver_datos'))

# ----- MANEJADORES DE ERRORES -----
@app.errorhandler(404)
def page_not_found(e):
    """Página no encontrada"""
    return render_template('404_producto.html', nombre='página'), 404

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Servidor iniciado correctamente")
    print("📱 Accede a: http://127.0.0.1:5000")
    print("📊 Nueva ruta: http://127.0.0.1:5000/datos")
    print("=" * 50)
    app.run(debug=True)