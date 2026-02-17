from flask import Flask, render_template

app = Flask(__name__)

# Base de datos simulada de productos (sin cambios)
productos_db = {
    'laptop': {
        'nombre': 'Laptop Dell XPS 15',
        'precio': '$1,299',
        'stock': 'Disponible',
        'descripcion': 'Laptop de alto rendimiento con procesador Intel i7, 16GB RAM, 512GB SSD'
    },
    'mouse': {
        'nombre': 'Mouse Logitech MX Master 3',
        'precio': '$99',
        'stock': 'Disponible',
        'descripcion': 'Mouse inalámbrico ergonómico con sensor de alta precisión'
    },
    'teclado': {
        'nombre': 'Teclado Mecánico Corsair K95',
        'precio': '$179',
        'stock': 'Disponible',
        'descripcion': 'Teclado mecánico RGB con switches Cherry MX'
    },
    'monitor': {
        'nombre': 'Monitor LG UltraWide 34"',
        'precio': '$599',
        'stock': 'Disponible',
        'descripcion': 'Monitor ultrawide 21:9, resolución 3440x1440, 144Hz'
    },
    'audifonos': {
        'nombre': 'Audífonos Sony WH-1000XM5',
        'precio': '$399',
        'stock': 'Disponible',
        'descripcion': 'Audífonos inalámbricos con cancelación de ruido activa'
    },
    'webcam': {
        'nombre': 'Webcam Logitech C920',
        'precio': '$79',
        'stock': 'Stock Limitado',
        'descripcion': 'Webcam Full HD 1080p con micrófono estéreo'
    }
}

# Ruta principal
@app.route('/')
def inicio():
    return render_template('index.html', productos=productos_db)

# Ruta dinámica para productos
@app.route('/producto/<nombre>')
def producto(nombre):
    nombre_lower = nombre.lower()
    
    if nombre_lower in productos_db:
        prod = productos_db[nombre_lower]
        return render_template('producto.html', prod=prod)
    else:
        return render_template('404_producto.html', nombre=nombre), 404

# Ruta para categorías
@app.route('/categoria/<tipo>')
def categoria(tipo):
    categorias_validas = ['computadoras', 'perifericos', 'audio']
    tipo_lower = tipo.lower()
    
    if tipo_lower in categorias_validas:
        return render_template('categoria.html', tipo=tipo_lower)
    else:
        return render_template('404_categoria.html', tipo=tipo), 404

# Ruta de contacto
@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

# Ruta acerca de (nueva para la tarea)
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)