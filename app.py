# app.py - VERSIÓN COMPLETA CON SEMANAS 9, 10, 11, 12 Y 13

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

# Configuración de archivos (Semana 12)
DATA_FOLDER = 'data'
TXT_FILE = os.path.join(DATA_FOLDER, 'productos.txt')
JSON_FILE = os.path.join(DATA_FOLDER, 'productos.json')
CSV_FILE = os.path.join(DATA_FOLDER, 'productos.csv')
os.makedirs(DATA_FOLDER, exist_ok=True)

# Inicializar componentes
inventario = Inventario()
db = DatabaseManager()

# ----- FUNCIONES PARA ARCHIVOS (Semana 12) -----
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

# ----- FUNCIONES PARA MYSQL (Semana 13) -----
def conectar_mysql():
    """Conecta a MySQL"""
    try:
        import pymysql
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='proyecto_tienda_tech',
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ Conectado a MySQL correctamente")
        return connection
    except ImportError:
        print("❌ pymysql no instalado. Ejecuta: pip install pymysql")
        return None
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

# ----- RUTAS PÚBLICAS (Semanas 9-10) -----
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

# ----- RUTAS DE AUTENTICACIÓN (Semana 11) -----
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevos usuarios"""
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            fecha = request.form.get('fecha_nacimiento', '').strip()
            
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
            
            # Crear usuario
            usuario = Usuario(None, nombre, email, password, fecha)
            usuario_id = db.insertar_usuario(usuario)
            
            if usuario_id:
                session['usuario_id'] = usuario_id
                session['usuario_nombre'] = usuario.nombre
                session['usuario_email'] = usuario.email
                
                flash(f'¡Bienvenido {usuario.nombre}!', 'success')
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

# ----- RUTAS DEL CARRITO (Semana 11) -----
@app.route('/agregar_al_carrito/<int:producto_id>')
def agregar_al_carrito(producto_id):
    """Agrega un producto al carrito"""
    producto = inventario.obtener_producto_por_id(producto_id)
    
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('inicio'))
    
    if 'carrito' not in session:
        session['carrito'] = {
            'items': {},
            'total': 0,
            'cantidad_items': 0
        }
    
    carrito = session['carrito']
    pid = str(producto_id)
    
    if pid in carrito['items']:
        carrito['items'][pid]['cantidad'] += 1
        carrito['items'][pid]['subtotal'] = carrito['items'][pid]['cantidad'] * producto.precio
    else:
        carrito['items'][pid] = {
            'producto_id': producto_id,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'cantidad': 1,
            'subtotal': producto.precio
        }
    
    total = 0
    cantidad_total = 0
    for item in carrito['items'].values():
        total += item['subtotal']
        cantidad_total += item['cantidad']
    
    carrito['total'] = total
    carrito['cantidad_items'] = cantidad_total
    
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
        pid = str(producto_id)
        
        if pid in carrito['items']:
            if cantidad <= 0:
                del carrito['items'][pid]
                flash('Producto eliminado del carrito', 'success')
            else:
                carrito['items'][pid]['cantidad'] = cantidad
                carrito['items'][pid]['subtotal'] = cantidad * carrito['items'][pid]['precio']
            
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
        pid = str(producto_id)
        
        if pid in carrito['items']:
            del carrito['items'][pid]
            
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

# ----- RUTAS PARA ARCHIVOS (Semana 12) -----
@app.route('/datos')
def ver_datos():
    """Vista principal de gestión de archivos"""
    datos_txt = cargar_desde_txt()
    datos_json = cargar_desde_json()
    datos_csv = cargar_desde_csv()
    
    return render_template('datos.html',
                         datos_txt=datos_txt,
                         datos_json=datos_json,
                         datos_csv=datos_csv)

@app.route('/datos/agregar', methods=['POST'])
def agregar_producto_data():
    """Agrega un producto a todos los formatos de archivo"""
    try:
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio'))
        cantidad = int(request.form.get('cantidad'))
        categoria = request.form.get('categoria')
        descripcion = request.form.get('descripcion', '')
        
        producto_id = int(datetime.now().timestamp())
        
        producto = {
            'id': producto_id,
            'nombre': nombre,
            'precio': precio,
            'cantidad': cantidad,
            'categoria': categoria,
            'descripcion': descripcion
        }
        
        guardar_en_txt(producto)
        guardar_en_json(producto)
        guardar_en_csv(producto)
        
        flash('Producto guardado exitosamente en TXT, JSON y CSV', 'success')
    except Exception as e:
        flash(f'Error al guardar el producto: {str(e)}', 'error')
    
    return redirect(url_for('ver_datos'))

@app.route('/datos/cargar/txt')
def cargar_txt():
    """Muestra datos desde TXT"""
    productos = cargar_desde_txt()
    return render_template('datos_tabla.html', productos=productos, formato='TXT')

@app.route('/datos/cargar/json')
def cargar_json():
    """Muestra datos desde JSON"""
    productos = cargar_desde_json()
    return render_template('datos_tabla.html', productos=productos, formato='JSON')

@app.route('/datos/cargar/csv')
def cargar_csv():
    """Muestra datos desde CSV"""
    productos = cargar_desde_csv()
    return render_template('datos_tabla.html', productos=productos, formato='CSV')

# ----- RUTAS PARA MYSQL (Semana 13) -----
@app.route('/mysql')
def ver_mysql():
    """Muestra productos desde MySQL"""
    conn = conectar_mysql()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM productos")
                productos = cursor.fetchall()
            conn.close()
            return render_template('mysql_datos.html', productos=productos)
        except Exception as e:
            flash(f'Error consultando MySQL: {str(e)}', 'error')
    else:
        flash('No se pudo conectar a MySQL. Verifica que WAMP esté corriendo.', 'error')
    
    return redirect(url_for('inicio'))

@app.route('/mysql/insertar', methods=['GET', 'POST'])
def insertar_mysql():
    """Formulario para insertar producto en MySQL"""
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            precio = float(request.form.get('precio'))
            cantidad = int(request.form.get('cantidad'))
            categoria = request.form.get('categoria')
            descripcion = request.form.get('descripcion', '')
            
            conn = conectar_mysql()
            if conn:
                with conn.cursor() as cursor:
                    sql = "INSERT INTO productos (nombre, precio, cantidad, categoria, descripcion) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (nombre, precio, cantidad, categoria, descripcion))
                    conn.commit()
                conn.close()
                flash('Producto insertado en MySQL correctamente', 'success')
                return redirect(url_for('ver_mysql'))
            else:
                flash('Error conectando a MySQL', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('mysql_form.html')

# ----- MANEJADORES DE ERRORES -----
@app.errorhandler(404)
def page_not_found(e):
    """Página no encontrada"""
    return render_template('404_producto.html', nombre='página'), 404

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Servidor iniciado correctamente")
    print("📱 Accede a: http://127.0.0.1:5000")
    print("📊 Semana 12: http://127.0.0.1:5000/datos")
    print("🗄️ Semana 13: http://127.0.0.1:5000/mysql")
    print("=" * 50)
    app.run(debug=True)