# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.inventario import Inventario
from models.usuario import Usuario
from database.db_manager import DatabaseManager
from database.conexion import MySQLConnection
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

os.makedirs(DATA_FOLDER, exist_ok=True)

# Inicializar componentes
inventario = Inventario()
db = DatabaseManager()

try:
    db.crear_tabla_usuarios()
    db.crear_tabla_carrito()
    print("✅ Tablas SQLite creadas/verificadas correctamente")
except Exception as e:
    print(f"⚠️ Error al crear tablas SQLite: {e}")

# ----- FUNCIONES PARA MANEJO DE TXT -----
def guardar_en_txt(producto):
    try:
        with open(TXT_FILE, 'a', encoding='utf-8') as f:
            linea = f"{producto['id']}|{producto['nombre']}|{producto['precio']}|{producto['cantidad']}|{producto['categoria']}|{producto['descripcion']}\n"
            f.write(linea)
    except Exception as e:
        print(f"Error guardando en TXT: {e}")

def cargar_desde_txt():
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
    try:
        productos = cargar_desde_json()
        productos.append(producto)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(productos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando en JSON: {e}")

def cargar_desde_json():
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando JSON: {e}")
    return []

# ----- FUNCIONES PARA MANEJO DE CSV -----
def guardar_en_csv(producto):
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
    try:
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
            
            if db.obtener_usuario_por_email(email):
                flash('Este email ya está registrado', 'error')
                return render_template('registro.html')
            
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
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('inicio'))

# ----- RUTAS DEL CARRITO -----
@app.route('/agregar_al_carrito/<int:producto_id>')
def agregar_al_carrito(producto_id):
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
    producto_id_str = str(producto_id)
    
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
    if 'carrito' not in session:
        session['carrito'] = {
            'items': {},
            'total': 0,
            'cantidad_items': 0
        }
    return render_template('carrito.html', carrito=session['carrito'])

@app.route('/actualizar_carrito/<int:producto_id>', methods=['POST'])
def actualizar_carrito(producto_id):
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
    if 'carrito' in session:
        carrito = session['carrito']
        producto_id_str = str(producto_id)
        
        if producto_id_str in carrito['items']:
            del carrito['items'][producto_id_str]
            
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
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para finalizar la compra', 'error')
        return redirect(url_for('login'))
    
    if 'carrito' not in session or not session['carrito'].get('items'):
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('ver_carrito'))
    
    flash('¡Compra realizada con éxito!', 'success')
    session.pop('carrito', None)
    return redirect(url_for('inicio'))

# ----- RUTAS PARA PERSISTENCIA (Semana 12) -----
@app.route('/datos')
def ver_datos():
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
        guardar_en_sqlite(producto)
        
        flash('Producto guardado exitosamente en todos los formatos', 'success')
    except Exception as e:
        flash(f'Error al guardar el producto: {str(e)}', 'error')
    
    return redirect(url_for('ver_datos'))

@app.route('/datos/cargar/txt')
def cargar_txt():
    productos = cargar_desde_txt()
    return render_template('datos_tabla.html', productos=productos, formato='TXT')

@app.route('/datos/cargar/json')
def cargar_json():
    productos = cargar_desde_json()
    return render_template('datos_tabla.html', productos=productos, formato='JSON')

@app.route('/datos/cargar/csv')
def cargar_csv():
    productos = cargar_desde_csv()
    return render_template('datos_tabla.html', productos=productos, formato='CSV')

@app.route('/datos/cargar/sqlite')
def cargar_sqlite():
    productos = cargar_desde_sqlite()
    return render_template('datos_tabla.html', productos=productos, formato='SQLite')

@app.route('/datos/exportar/txt')
def exportar_txt():
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
    try:
        productos = inventario.obtener_todos()
        for p in productos:
            guardar_en_sqlite(p.to_dict())
        flash('Datos exportados a SQLite correctamente', 'success')
    except Exception as e:
        flash(f'Error exportando a SQLite: {str(e)}', 'error')
    return redirect(url_for('ver_datos'))

# ----- RUTAS PARA MYSQL (Semana 13) -----

@app.route('/test-wamp')
def test_wamp():
    """Ruta para verificar conexión con WAMP"""
    try:
        db = MySQLConnection()
        conn = db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION() as version")
            version = cursor.fetchone()
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()
            db.cerrar()
            
            return f"""
            <div style="padding:20px; font-family:Arial; max-width:600px; margin:50px auto; background:white; border-radius:15px;">
                <h2 style="color:#27ae60;">✅ WAMP funcionando correctamente</h2>
                <p><strong>Versión MySQL:</strong> {version[0] if version else 'Desconocida'}</p>
                <p><strong>Base de datos:</strong> proyecto_tienda_tech</p>
                <p><strong>Tablas encontradas:</strong> {len(tablas)}</p>
                <ul>
                    {''.join([f'<li>{t[0]}</li>' for t in tablas])}
                </ul>
                <p><a href="/" style="color:#667eea;">← Volver a inicio</a></p>
            </div>
            """
        else:
            return """
            <div style="padding:20px; font-family:Arial; max-width:600px; margin:50px auto; background:white; border-radius:15px;">
                <h2 style="color:#e74c3c;">❌ Error de conexión</h2>
                <p>No se pudo conectar a MySQL. Verifica que WAMP esté corriendo (icono verde).</p>
                <p><a href="/" style="color:#667eea;">← Volver a inicio</a></p>
            </div>
            """
    except Exception as e:
        return f"""
        <div style="padding:20px; font-family:Arial; max-width:600px; margin:50px auto; background:white; border-radius:15px;">
            <h2 style="color:#e74c3c;">❌ Error</h2>
            <p>{str(e)}</p>
            <p><a href="/" style="color:#667eea;">← Volver a inicio</a></p>
        </div>
        """

@app.route('/mysql')
def ver_mysql():
    """Muestra productos desde MySQL"""
    try:
        db = MySQLConnection()
        db.conectar()
        productos = db.ejecutar_query("SELECT * FROM productos ORDER BY id", fetch=True)
        db.cerrar()
        return render_template('mysql_datos.html', productos=productos)
    except Exception as e:
        flash(f'Error al cargar datos MySQL: {str(e)}', 'error')
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
            
            db = MySQLConnection()
            db.conectar()
            query = """
                INSERT INTO productos (nombre, precio, cantidad, categoria, descripcion)
                VALUES (%s, %s, %s, %s, %s)
            """
            db.ejecutar_query(query, (nombre, precio, cantidad, categoria, descripcion))
            db.cerrar()
            
            flash('Producto insertado en MySQL correctamente', 'success')
            return redirect(url_for('ver_mysql'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('mysql_form.html')

@app.route('/mysql/actualizar/<int:id>', methods=['POST'])
def actualizar_mysql(id):
    """Actualiza producto en MySQL"""
    try:
        precio = float(request.form.get('precio'))
        cantidad = int(request.form.get('cantidad'))
        
        db = MySQLConnection()
        db.conectar()
        query = "UPDATE productos SET precio=%s, cantidad=%s WHERE id=%s"
        db.ejecutar_query(query, (precio, cantidad, id))
        db.cerrar()
        
        flash('Producto actualizado en MySQL', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('ver_mysql'))

@app.route('/mysql/eliminar/<int:id>')
def eliminar_mysql(id):
    """Elimina producto de MySQL"""
    try:
        db = MySQLConnection()
        db.conectar()
        query = "DELETE FROM productos WHERE id=%s"
        db.ejecutar_query(query, (id,))
        db.cerrar()
        
        flash('Producto eliminado de MySQL', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('ver_mysql'))

# ----- MANEJADORES DE ERRORES -----
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_producto.html', nombre='página'), 404

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Servidor iniciado correctamente")
    print("📱 Accede a: http://127.0.0.1:5000")
    print("🗄️ MySQL: http://127.0.0.1:5000/mysql")
    print("=" * 50)
    app.run(debug=True)