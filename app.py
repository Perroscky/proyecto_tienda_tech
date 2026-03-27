# app.py - VERSIÓN COMPLETA CON SEMANA 15 (CRUD, REPORTES PDF, ESTRUCTURA POR CAPAS)

from flask import send_file # type: ignore
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file # type: ignore
from flask_login import LoginManager, login_user, logout_user, login_required, current_user # type: ignore
from models.inventario import Inventario
from models.usuario import Usuario
from database.db_manager import DatabaseManager
from services.producto_service import ProductoService
from services.reporte_service import ReporteService
from forms.producto_form import ProductoForm, ProductoFiltroForm
import os
import json
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_proyecto_tienda_tech'

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
login_manager.login_message_category = 'info'

# Configuración de archivos
DATA_FOLDER = 'data'
TXT_FILE = os.path.join(DATA_FOLDER, 'productos.txt')
JSON_FILE = os.path.join(DATA_FOLDER, 'productos.json')
CSV_FILE = os.path.join(DATA_FOLDER, 'productos.csv')
os.makedirs(DATA_FOLDER, exist_ok=True)

# Inicializar componentes
inventario = Inventario()
db = DatabaseManager()
producto_service = ProductoService()
reporte_service = ReporteService()

@login_manager.user_loader
def load_user(user_id):
    try:
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
    if current_user.is_authenticated:
        try:
            productos = producto_service.obtener_todos()
            total_productos = len(productos) if productos else 0
            usuarios_data = db.obtener_todos_usuarios()
            total_usuarios = len(usuarios_data) if usuarios_data else 0
            return render_template('dashboard.html', 
                                 total_productos=total_productos,
                                 total_usuarios=total_usuarios)
        except Exception as e:
            print(f"Error cargando dashboard: {e}")
            return render_template('dashboard.html', total_productos=0, total_usuarios=0)
    else:
        return render_template('index.html')

@app.route('/producto/<nombre>')
@login_required
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
    return render_template('404_producto.html', nombre=nombre), 404

@app.route('/categoria/<tipo>')
@login_required
def categoria(tipo):
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

# ----- RUTAS DE AUTENTICACIÓN (Semana 11 y 14) -----
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
                try:
                    conn = conectar_mysql()
                    if conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SHOW TABLES LIKE 'usuarios'")
                            if cursor.fetchone():
                                sql = """INSERT INTO usuarios 
                                         (id_usuario, nombre, mail, password, fecha_nacimiento, proveedor, rol) 
                                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                                cursor.execute(sql, (
                                    usuario_id,
                                    usuario.nombre,
                                    usuario.email,
                                    usuario.password,
                                    usuario.fecha_nacimiento,
                                    usuario.proveedor,
                                    'admin'
                                ))
                                conn.commit()
                                print("✅ Usuario guardado en MySQL")
                        conn.close()
                except Exception as e:
                    print(f"⚠️ Error guardando en MySQL: {e}")
                
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
            usuario = Usuario(
                id=usuario_data[0],
                nombre=usuario_data[1],
                email=usuario_data[2],
                password=usuario_data[3],
                fecha_nacimiento=usuario_data[4]
            )
            
            if usuario.verificar_password(password):
                login_user(usuario)
                flash(f'¡Bienvenido {usuario.nombre}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('inicio'))
        
        flash('Email o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('inicio'))

# ----- RUTAS DEL CARRITO (Semana 11) -----
@app.route('/agregar_al_carrito/<int:producto_id>')
@login_required
def agregar_al_carrito(producto_id):
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
    if 'carrito' not in session:
        session['carrito'] = {'items': {}, 'total': 0, 'cantidad_items': 0}
    return render_template('carrito.html', carrito=session['carrito'])

@app.route('/actualizar_carrito/<int:producto_id>', methods=['POST'])
@login_required
def actualizar_carrito(producto_id):
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

# =====================================================
# NUEVAS RUTAS PARA CRUD Y REPORTES (Semana 15)
# =====================================================

@app.route('/productos')
@login_required
def listar_productos():
    """Listar todos los productos con estadísticas"""
    productos = producto_service.obtener_todos()
    estadisticas = producto_service.obtener_estadisticas()
    form_filtro = ProductoFiltroForm()
    return render_template('productos_lista.html', 
                         productos=productos, 
                         estadisticas=estadisticas,
                         form_filtro=form_filtro)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def producto_nuevo():
    """Crear nuevo producto"""
    form = ProductoForm()
    
    if form.validate_on_submit():
        datos = {
            'nombre': form.nombre.data,
            'precio': form.precio.data,
            'cantidad': form.cantidad.data,
            'categoria': form.categoria.data,
            'descripcion': form.descripcion.data
        }
        nuevo_id = producto_service.crear(datos)
        if nuevo_id:
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('listar_productos'))
        else:
            flash('Error al crear el producto', 'error')
    
    return render_template('producto_form.html', form=form, titulo='Nuevo Producto')

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def producto_editar(id):
    """Editar producto existente"""
    producto = producto_service.obtener_por_id(id)
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('listar_productos'))
    
    form = ProductoForm()
    
    if request.method == 'GET':
        form.nombre.data = producto['nombre']
        form.precio.data = producto['precio']
        form.cantidad.data = producto['cantidad']
        form.categoria.data = producto['categoria']
        form.descripcion.data = producto.get('descripcion', '')
    
    if form.validate_on_submit():
        datos = {
            'nombre': form.nombre.data,
            'precio': form.precio.data,
            'cantidad': form.cantidad.data,
            'categoria': form.categoria.data,
            'descripcion': form.descripcion.data
        }
        if producto_service.actualizar(id, datos):
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('listar_productos'))
        else:
            flash('Error al actualizar el producto', 'error')
    
    return render_template('producto_form.html', form=form, titulo='Editar Producto', producto=producto)

@app.route('/productos/eliminar/<int:id>')
@login_required
def producto_eliminar(id):
    """Eliminar producto"""
    if producto_service.eliminar(id):
        flash('Producto eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar el producto', 'error')
    return redirect(url_for('listar_productos'))

@app.route('/productos/reporte')
@login_required
def generar_reporte_productos():
    """Generar reporte PDF de todos los productos"""
    productos = producto_service.obtener_todos()
    filename, filepath = reporte_service.generar_reporte_productos(productos)
    flash(f'Reporte generado: {filename}', 'success')
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/productos/reporte/bajo-stock')
@login_required
def generar_reporte_bajo_stock():
    """Generar reporte de productos con bajo stock"""
    productos = producto_service.obtener_con_bajo_stock(5)
    if not productos:
        flash('No hay productos con bajo stock', 'info')
        return redirect(url_for('listar_productos'))
    filename, filepath = reporte_service.generar_reporte_bajo_stock(productos)
    flash(f'Reporte generado: {filename}', 'success')
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/productos/reporte/categoria/<categoria>')
@login_required
def generar_reporte_categoria(categoria):
    """Generar reporte por categoría"""
    categorias_validas = ['computadoras', 'perifericos', 'audio', 'celulares', 'tablets', 'otros']
    if categoria not in categorias_validas:
        flash('Categoría no válida', 'error')
        return redirect(url_for('listar_productos'))
    
    productos = producto_service.obtener_por_categoria(categoria)
    if not productos:
        flash(f'No hay productos en la categoría {categoria}', 'info')
        return redirect(url_for('listar_productos'))
    
    filename, filepath = reporte_service.generar_reporte_por_categoria(productos, categoria)
    flash(f'Reporte generado: {filename}', 'success')
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/productos/filtrar', methods=['POST'])
@login_required
def filtrar_productos():
    """Filtrar productos"""
    form = ProductoFiltroForm()
    productos = producto_service.obtener_todos()
    
    if form.buscar.data:
        productos = producto_service.buscar(form.buscar.data)
    
    if form.categoria.data:
        productos = [p for p in productos if p['categoria'] == form.categoria.data]
    
    if form.stock_minimo.data and form.stock_minimo.data > 0:
        productos = [p for p in productos if p['cantidad'] <= form.stock_minimo.data]
    
    estadisticas = producto_service.obtener_estadisticas()
    
    return render_template('productos_lista.html', 
                         productos=productos, 
                         estadisticas=estadisticas,
                         form_filtro=form)

# ----- RUTA DE PRUEBA -----
@app.route('/test-db')
def test_db():
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
    print("📦 Semana 15: http://127.0.0.1:5000/productos")
    print("=" * 50)
    app.run(debug=True)