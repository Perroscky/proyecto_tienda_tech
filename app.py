# app.py - VERSIÓN COMPLETA CON FLASK-LOGIN
# TODAS las funcionalidades anteriores se mantienen

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.inventario import Inventario
from models.usuario import Usuario
from database.db_manager import DatabaseManager
import os
import json
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_proyecto_tienda_tech'

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Ruta para login
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
login_manager.login_message_category = 'info'

# Configuración de archivos (Semana 12)
DATA_FOLDER = 'data'
TXT_FILE = os.path.join(DATA_FOLDER, 'productos.txt')
JSON_FILE = os.path.join(DATA_FOLDER, 'productos.json')
CSV_FILE = os.path.join(DATA_FOLDER, 'productos.csv')
os.makedirs(DATA_FOLDER, exist_ok=True)

# Inicializar componentes
inventario = Inventario()
db = DatabaseManager()

@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la base de datos por su ID"""
    try:
        # Buscar en SQLite
        usuario_data = db.obtener_usuario_por_id(int(user_id))
        if usuario_data:
            return Usuario(
                id=usuario_data[0],
                nombre=usuario_data[1],
                email=usuario_data[2],
                password=usuario_data[3],
                fecha_nacimiento=usuario_data[4]
            )
    except Exception as e:
        print(f"Error cargando usuario: {e}")
    return None

# ----- FUNCIONES PARA ARCHIVOS (Semana 12) -----
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

# ----- FUNCIONES PARA MYSQL (Semana 13) -----
def conectar_mysql():
    """Conecta a MySQL (Clever Cloud o Local)"""
    try:
        from database.conexion import MySQLConnection
        db_mysql = MySQLConnection()
        conn = db_mysql.conectar()
        return conn
    except ImportError:
        print("❌ Error importando MySQLConnection")
        return None
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

# ----- RUTAS PÚBLICAS (Semanas 9-10) -----
@app.route('/')
def inicio():
    """Página principal - Catálogo de productos"""
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
    return render_template('404_categoria.html', tipo=tipo), 404

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ----- RUTAS DE AUTENTICACIÓN (Semana 14 - CON FLASK-LOGIN) -----
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevos usuarios - CON FLASK-LOGIN"""
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
            
            # Crear usuario
            usuario = Usuario(None, nombre, email, password, fecha)
            usuario_id = db.insertar_usuario(usuario)
            
            if usuario_id:
                # Guardar también en MySQL (Clever Cloud)
                try:
                    conn = conectar_mysql()
                    if conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SHOW TABLES LIKE 'usuarios'")
                            if cursor.fetchone():
                                sql = """INSERT INTO usuarios 
                                         (id_usuario, nombre, mail, password, fecha_nacimiento, proveedor) 
                                         VALUES (%s, %s, %s, %s, %s, %s)"""
                                cursor.execute(sql, (
                                    usuario_id,
                                    usuario.nombre,
                                    usuario.email,
                                    usuario.password,
                                    usuario.fecha_nacimiento,
                                    usuario.proveedor
                                ))
                                conn.commit()
                                print("✅ Usuario guardado en MySQL")
                        conn.close()
                except Exception as e:
                    print(f"⚠️ Error guardando en MySQL: {e}")
                
                # 🔥 Iniciar sesión con Flask-Login
                usuario.id = usuario_id
                login_user(usuario)
                
                flash(f'¡Bienvenido {usuario.nombre}!', 'success')
                return redirect(url_for('inicio'))
            else:
                flash('Error al crear el usuario', 'error')
                
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'error')
            print(f"❌ Error: {e}")
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión - CON FLASK-LOGIN"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email y contraseña son obligatorios', 'error')
            return render_template('login.html')
        
        usuario_data = db.obtener_usuario_por_email(email)
        
        if usuario_data:
            # Crear objeto usuario
            usuario = Usuario(
                id=usuario_data[0],
                nombre=usuario_data[1],
                email=usuario_data[2],
                password=usuario_data[3],
                fecha_nacimiento=usuario_data[4]
            )
            
            # Extraer la contraseña original para verificar
            password_original = usuario_data[3].replace('enc_', '').replace('_2026', '')
            if usuario.verificar_password(password_original if password_original else password):
                # 🔥 Iniciar sesión con Flask-Login
                login_user(usuario)
                flash(f'¡Bienvenido {usuario.nombre}!', 'success')
                
                # Redirigir a la página que intentaba acceder
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('inicio'))
        
        flash('Email o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión - CON FLASK-LOGIN"""
    logout_user()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('inicio'))

# ----- RUTAS DEL CARRITO (Semana 11) - PROTEGIDAS -----
@app.route('/agregar_al_carrito/<int:producto_id>')
@login_required
def agregar_al_carrito(producto_id):
    """Agrega un producto al carrito - SOLO USUARIOS AUTENTICADOS"""
    producto = inventario.obtener_producto_por_id(producto_id)
    
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('inicio'))
    
    if 'carrito' not in session:
        session['carrito'] = {'items': {}, 'total': 0, 'cantidad_items': 0}
    
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
    
    total = sum(item['subtotal'] for item in carrito['items'].values())
    cantidad_total = sum(item['cantidad'] for item in carrito['items'].values())
    carrito['total'] = total
    carrito['cantidad_items'] = cantidad_total
    
    session['carrito'] = carrito
    session.modified = True
    
    flash(f'{producto.nombre} agregado al carrito', 'success')
    return redirect(url_for('ver_carrito'))

@app.route('/carrito')
@login_required
def ver_carrito():
    """Ver el contenido del carrito - SOLO USUARIOS AUTENTICADOS"""
    if 'carrito' not in session:
        session['carrito'] = {'items': {}, 'total': 0, 'cantidad_items': 0}
    return render_template('carrito.html', carrito=session['carrito'])

@app.route('/actualizar_carrito/<int:producto_id>', methods=['POST'])
@login_required
def actualizar_carrito(producto_id):
    """Actualizar cantidad de un producto - SOLO USUARIOS AUTENTICADOS"""
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
            
            total = sum(item['subtotal'] for item in carrito['items'].values())
            cantidad_total = sum(item['cantidad'] for item in carrito['items'].values())
            carrito['total'] = total
            carrito['cantidad_items'] = cantidad_total
            session['carrito'] = carrito
            session.modified = True
    
    return redirect(url_for('ver_carrito'))

@app.route('/eliminar_del_carrito/<int:producto_id>')
@login_required
def eliminar_del_carrito(producto_id):
    """Eliminar un producto del carrito - SOLO USUARIOS AUTENTICADOS"""
    if 'carrito' in session:
        carrito = session['carrito']
        pid = str(producto_id)
        
        if pid in carrito['items']:
            del carrito['items'][pid]
            
            total = sum(item['subtotal'] for item in carrito['items'].values())
            cantidad_total = sum(item['cantidad'] for item in carrito['items'].values())
            carrito['total'] = total
            carrito['cantidad_items'] = cantidad_total
            session['carrito'] = carrito
            session.modified = True
            flash('Producto eliminado del carrito', 'success')
    
    return redirect(url_for('ver_carrito'))

@app.route('/finalizar_compra')
@login_required
def finalizar_compra():
    """Finalizar la compra - SOLO USUARIOS AUTENTICADOS"""
    if 'carrito' not in session or not session['carrito'].get('items'):
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('ver_carrito'))
    
    flash('¡Compra realizada con éxito!', 'success')
    session.pop('carrito', None)
    return redirect(url_for('inicio'))

# ----- RUTAS PARA ARCHIVOS (Semana 12) -----
@app.route('/datos')
@login_required
def ver_datos():
    """Vista principal de gestión de archivos - SOLO USUARIOS AUTENTICADOS"""
    datos_txt = cargar_desde_txt()
    datos_json = cargar_desde_json()
    datos_csv = cargar_desde_csv()
    return render_template('datos.html',
                         datos_txt=datos_txt,
                         datos_json=datos_json,
                         datos_csv=datos_csv)

@app.route('/datos/agregar', methods=['POST'])
@login_required
def agregar_producto_data():
    """Agrega un producto a archivos - SOLO USUARIOS AUTENTICADOS"""
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
        flash('Producto guardado en TXT, JSON y CSV', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('ver_datos'))

@app.route('/datos/cargar/txt')
@login_required
def cargar_txt():
    productos = cargar_desde_txt()
    return render_template('datos_tabla.html', productos=productos, formato='TXT')

@app.route('/datos/cargar/json')
@login_required
def cargar_json():
    productos = cargar_desde_json()
    return render_template('datos_tabla.html', productos=productos, formato='JSON')

@app.route('/datos/cargar/csv')
@login_required
def cargar_csv():
    productos = cargar_desde_csv()
    return render_template('datos_tabla.html', productos=productos, formato='CSV')

@app.route('/datos/exportar/txt')
@login_required
def exportar_txt():
    try:
        productos = inventario.obtener_todos()
        with open(TXT_FILE, 'w', encoding='utf-8') as f:
            for p in productos:
                linea = f"{p.id}|{p.nombre}|{p.precio}|{p.cantidad}|{p.categoria}|{p.descripcion}\n"
                f.write(linea)
        flash('Datos exportados a TXT', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('ver_datos'))

@app.route('/datos/exportar/json')
@login_required
def exportar_json():
    try:
        productos = inventario.obtener_todos()
        data = [p.to_dict() for p in productos]
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        flash('Datos exportados a JSON', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('ver_datos'))

@app.route('/datos/exportar/csv')
@login_required
def exportar_csv():
    try:
        productos = inventario.obtener_todos()
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nombre', 'precio', 'cantidad', 'categoria', 'descripcion'])
            for p in productos:
                writer.writerow([p.id, p.nombre, p.precio, p.cantidad, p.categoria, p.descripcion])
        flash('Datos exportados a CSV', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('ver_datos'))

# ----- RUTAS PARA MYSQL (Semana 13) -----
@app.route('/mysql')
@login_required
def ver_mysql():
    """Muestra productos desde MySQL - SOLO USUARIOS AUTENTICADOS"""
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
        flash('No se pudo conectar a MySQL', 'error')
    return redirect(url_for('inicio'))

@app.route('/mysql/insertar', methods=['GET', 'POST'])
@login_required
def insertar_mysql():
    """Formulario para insertar producto en MySQL - SOLO USUARIOS AUTENTICADOS"""
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
                flash('Producto insertado en MySQL', 'success')
                return redirect(url_for('ver_mysql'))
            else:
                flash('Error conectando a MySQL', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('mysql_form.html')

@app.route('/mysql/actualizar/<int:id>', methods=['POST'])
@login_required
def actualizar_mysql(id):
    try:
        precio = float(request.form.get('precio'))
        cantidad = int(request.form.get('cantidad'))
        conn = conectar_mysql()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE productos SET precio=%s, cantidad=%s WHERE id=%s", (precio, cantidad, id))
                conn.commit()
            conn.close()
            flash('Producto actualizado en MySQL', 'success')
        else:
            flash('Error conectando a MySQL', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('ver_mysql'))

@app.route('/mysql/eliminar/<int:id>')
@login_required
def eliminar_mysql(id):
    try:
        conn = conectar_mysql()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM productos WHERE id=%s", (id,))
                conn.commit()
            conn.close()
            flash('Producto eliminado de MySQL', 'success')
        else:
            flash('Error conectando a MySQL', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('ver_mysql'))

# ----- RUTA DE PRUEBA PARA VERIFICAR CONEXIÓN -----
@app.route('/test-db')
def test_db():
    """Ruta para verificar qué base de datos se está usando"""
    try:
        from database.conexion import MySQLConnection
        db_mysql = MySQLConnection()
        conn = db_mysql.conectar()
        
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT DATABASE() as db, VERSION() as version, USER() as user")
                info = cursor.fetchone()
            conn.close()
            
            return f"""
            <div style="padding:20px; font-family:Arial; max-width:600px; margin:50px auto; background:white; border-radius:15px;">
                <h2 style="color:#667eea;">🔍 Información de Base de Datos</h2>
                <p><strong>Modo:</strong> {"PRODUCCIÓN (Clever Cloud)" if os.environ.get('RENDER') else "DESARROLLO (Local)"}</p>
                <p><strong>Base de datos:</strong> {info['db']}</p>
                <p><strong>Usuario:</strong> {info['user']}</p>
                <p><strong>Versión MySQL:</strong> {info['version']}</p>
                <p><a href="/" style="color:#667eea;">← Volver a inicio</a></p>
            </div>
            """
        else:
            return "<h2>❌ No conectado a MySQL</h2>"
    except Exception as e:
        return f"<h2>❌ Error: {str(e)}</h2>"

# ----- MANEJADORES DE ERRORES -----
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_producto.html', nombre='página'), 404

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Servidor iniciado correctamente")
    print("📱 Accede a: http://127.0.0.1:5000")
    print("📊 Semana 12: http://127.0.0.1:5000/datos")
    print("🗄️ Semana 13: http://127.0.0.1:5000/mysql")
    print("🔍 Test DB: http://127.0.0.1:5000/test-db")
    print("=" * 50)
    app.run(debug=True)