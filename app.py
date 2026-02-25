# app.py

from flask import Flask, render_template
from models.inventario import Inventario
from database.db_manager import DatabaseManager

app = Flask(__name__)

# Base de datos simulada de productos (se mantiene para migración)
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

# Inicializar el inventario (se carga automáticamente desde la BD)
inventario = Inventario()

# Opcional: Migrar datos iniciales si la BD está vacía
def verificar_y_migrar_datos():
    """Verifica si hay datos en la BD y migra los iniciales si es necesario"""
    db = DatabaseManager("proyecto_tienda_tech.db")
    productos = db.obtener_todos_productos()
    
    if not productos:
        print("🔄 Base de datos vacía. Migrando productos iniciales...")
        db.migrar_productos_iniciales()
        # Recargar inventario después de la migración
        global inventario
        inventario = Inventario()
        print("✅ Migración completada. Productos disponibles en la tienda.")
    else:
        print(f"✅ Base de datos con {len(productos)} productos cargados.")

# Ejecutar verificación al iniciar
verificar_y_migrar_datos()

# Ruta principal
@app.route('/')
def inicio():
    # Obtener todos los productos del inventario
    productos = inventario.obtener_todos()
    
    # Convertir a formato para la plantilla
    productos_template = {}
    for prod in productos:
        # Usar el nombre como clave para mantener compatibilidad con plantillas existentes
        key = prod.nombre.lower().replace(' ', '_').replace('"', '').replace("'", '')
        productos_template[key] = {
            'nombre': prod.nombre,
            'precio': f"${prod.precio:.2f}",
            'stock': 'Disponible' if prod.cantidad > 5 else 'Stock Limitado' if prod.cantidad > 0 else 'Agotado',
            'descripcion': prod.descripcion
        }
    
    return render_template('index.html', productos=productos_template)

# Ruta dinámica para productos
@app.route('/producto/<nombre>')
def producto(nombre):
    # Buscar el producto por nombre (búsqueda aproximada)
    nombre_lower = nombre.lower().replace('_', ' ')
    productos_encontrados = inventario.buscar_productos(nombre_lower)
    
    if productos_encontrados:
        prod = productos_encontrados[0]  # Tomar el primero encontrado
        prod_dict = {
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

# Ruta para categorías
@app.route('/categoria/<tipo>')
def categoria(tipo):
    categorias_validas = Inventario.CATEGORIAS_VALIDAS
    tipo_lower = tipo.lower()
    
    if tipo_lower in categorias_validas:
        # Obtener productos de esa categoría
        productos_categoria = inventario.obtener_por_categoria(tipo_lower)
        return render_template('categoria.html', tipo=tipo_lower, 
                             productos=productos_categoria, 
                             hay_productos=len(productos_categoria) > 0)
    else:
        return render_template('404_categoria.html', tipo=tipo), 404

# Ruta de contacto
@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

# Ruta acerca de
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    print("🚀 Iniciando proyecto_tienda_tech...")
    app.run(debug=True)