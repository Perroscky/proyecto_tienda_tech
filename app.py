from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.inventario import Inventario
from models.usuario import Usuario
from models.carrito import Carrito
from database.db_manager import DatabaseManager

app = Flask(__name__)
app.secret_key = 'clave_secreta_proyecto_tienda_tech'

# Inicializar
inventario = Inventario()
db = DatabaseManager()

# Crear tablas adicionales
db.crear_tabla_usuarios()
db.crear_tabla_carrito()

# ----- RUTAS DE AUTENTICACIÓN -----
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            password = request.form['password']
            fecha = request.form['fecha_nacimiento']
            
            if not Usuario.validar_email(email):
                flash('Email no válido', 'error')
                return render_template('registro.html')
            
            if db.obtener_usuario_por_email(email):
                flash('Email ya registrado', 'error')
                return render_template('registro.html')
            
            usuario = Usuario(None, nombre, email, password, fecha)
            usuario_id = db.insertar_usuario(usuario)
            
            session['usuario_id'] = usuario_id
            session['usuario_nombre'] = nombre
            
            db.crear_carrito(usuario_id)
            flash(f'¡Bienvenido {nombre}!', 'success')
            return redirect(url_for('inicio'))
            
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        data = db.obtener_usuario_por_email(email)
        
        if data:
            usuario = Usuario(data[0], data[1], data[2], password, data[4])
            if usuario.verificar_password(password):
                session['usuario_id'] = data[0]
                session['usuario_nombre'] = data[1]
                flash(f'¡Bienvenido {data[1]}!', 'success')
                return redirect(url_for('inicio'))
        
        flash('Email o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/registro/facebook')
def registro_facebook():
    flash('Registro con Facebook (simulado)', 'info')
    return redirect(url_for('registro'))

@app.route('/login/facebook')
def login_facebook():
    flash('Login con Facebook (simulado)', 'info')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('inicio'))

# ----- RUTAS DEL CARRITO -----
@app.route('/agregar_al_carrito/<int:producto_id>')
def agregar_al_carrito(producto_id):
    producto = inventario.obtener_producto_por_id(producto_id)
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('inicio'))
    
    if 'carrito' not in session:
        session['carrito'] = Carrito(session.get('usuario_id')).to_dict()
    
    carrito = Carrito(session.get('usuario_id'))
    for item_id, item in session['carrito'].get('items', {}).items():
        prod = inventario.obtener_producto_por_id(int(item['producto_id']))
        if prod:
            carrito.agregar_item(prod, item['cantidad'])
    
    carrito.agregar_item(producto)
    session['carrito'] = carrito.to_dict()
    
    flash(f'{producto.nombre} agregado al carrito', 'success')
    return redirect(url_for('ver_carrito'))

@app.route('/carrito')
def ver_carrito():
    if 'carrito' not in session:
        session['carrito'] = Carrito(session.get('usuario_id')).to_dict()
    return render_template('carrito.html')

@app.route('/actualizar_carrito/<int:producto_id>', methods=['POST'])
def actualizar_carrito(producto_id):
    cantidad = int(request.form['cantidad'])
    
    if 'carrito' in session:
        carrito = Carrito(session.get('usuario_id'))
        for item_id, item in session['carrito'].get('items', {}).items():
            prod = inventario.obtener_producto_por_id(int(item['producto_id']))
            if prod:
                carrito.agregar_item(prod, item['cantidad'])
        
        if cantidad > 0:
            prod = inventario.obtener_producto_por_id(producto_id)
            if prod:
                carrito.agregar_item(prod, cantidad)
        else:
            carrito.quitar_item(producto_id)
        
        session['carrito'] = carrito.to_dict()
    
    return redirect(url_for('ver_carrito'))

@app.route('/eliminar_del_carrito/<int:producto_id>')
def eliminar_del_carrito(producto_id):
    if 'carrito' in session:
        carrito = Carrito(session.get('usuario_id'))
        for item_id, item in session['carrito'].get('items', {}).items():
            prod = inventario.obtener_producto_por_id(int(item['producto_id']))
            if prod:
                carrito.agregar_item(prod, item['cantidad'])
        
        carrito.quitar_item(producto_id)
        session['carrito'] = carrito.to_dict()
        flash('Producto eliminado', 'success')
    
    return redirect(url_for('ver_carrito'))

@app.route('/finalizar_compra')
def finalizar_compra():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión', 'error')
        return redirect(url_for('login'))
    
    flash('¡Compra realizada!', 'success')
    session.pop('carrito', None)
    return redirect(url_for('inicio'))

# ----- RUTAS EXISTENTES -----
@app.route('/')
def inicio():
    productos = inventario.obtener_todos()
    prod_dict = {}
    for p in productos:
        key = p.nombre.lower().replace(' ', '_')
        prod_dict[key] = {
            'id': p.id,
            'nombre': p.nombre,
            'precio': f"${p.precio:.2f}",
            'stock': 'Disponible' if p.cantidad > 5 else 'Stock Limitado',
            'descripcion': p.descripcion
        }
    return render_template('index.html', productos=prod_dict)

@app.route('/producto/<nombre>')
def producto(nombre):
    nombre = nombre.lower().replace('_', ' ')
    encontrados = inventario.buscar_productos(nombre)
    
    if encontrados:
        p = encontrados[0]
        return render_template('producto.html', prod={
            'nombre': p.nombre,
            'precio': f"${p.precio:.2f}",
            'stock': 'Disponible' if p.cantidad > 5 else 'Stock Limitado',
            'descripcion': p.descripcion,
            'id': p.id
        })
    return render_template('404_producto.html', nombre=nombre), 404

@app.route('/categoria/<tipo>')
def categoria(tipo):
    if tipo in Inventario.CATEGORIAS_VALIDAS:
        productos = inventario.obtener_por_categoria(tipo)
        return render_template('categoria.html', tipo=tipo, 
                             productos=productos, hay_productos=len(productos)>0)
    return render_template('404_categoria.html', tipo=tipo), 404

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)