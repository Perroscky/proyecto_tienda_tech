from flask import Flask, render_template

app = Flask(__name__)

# Base de datos simulada de productos
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
        return f'''
        <html>
        <head>
            <title>{prod['nombre']}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px;
                    margin: 0;
                }}
                .producto-detalle {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }}
                h1 {{
                    color: #667eea;
                    margin-bottom: 20px;
                }}
                .precio {{
                    font-size: 2em;
                    color: #764ba2;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .stock {{
                    display: inline-block;
                    padding: 8px 20px;
                    background: #28a745;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                }}
                .descripcion {{
                    margin: 20px 0;
                    line-height: 1.6;
                    color: #555;
                }}
                .btn {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }}
                .btn:hover {{
                    background: #764ba2;
                }}
            </style>
        </head>
        <body>
            <div class="producto-detalle">
                <h1>🛒 {prod['nombre']}</h1>
                <div class="precio">{prod['precio']}</div>
                <span class="stock">✓ {prod['stock']}</span>
                <p class="descripcion">{prod['descripcion']}</p>
                <a href="/" class="btn">← Volver a la tienda</a>
            </div>
        </body>
        </html>
        '''
    else:
        return f'''
        <html>
        <head>
            <title>Producto no encontrado</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px;
                    text-align: center;
                }}
                .error {{
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    max-width: 500px;
                    margin: 100px auto;
                }}
                h1 {{ color: #e74c3c; }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>❌ Producto no encontrado</h1>
                <p>El producto "{nombre}" no existe en nuestro catálogo.</p>
                <a href="/">Ver todos los productos</a>
            </div>
        </body>
        </html>
        '''

# Ruta para categorías
@app.route('/categoria/<tipo>')
def categoria(tipo):
    categorias_validas = ['computadoras', 'perifericos', 'audio']
    
    if tipo.lower() in categorias_validas:
        return f'''
        <html>
        <head>
            <title>Categoría: {tipo.capitalize()}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                }}
                h1 {{ color: #667eea; }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📦 Categoría: {tipo.capitalize()}</h1>
                <p>Explora nuestros productos de {tipo}</p>
                <a href="/">← Volver</a>
            </div>
        </body>
        </html>
        '''
    else:
        return f'Categoría "{tipo}" no encontrada. <a href="/">Volver</a>'

# Ruta de contacto
@app.route('/contacto')
def contacto():
    return '''
    <html>
    <head>
        <title>Contacto</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 15px;
            }
            h1 { color: #667eea; }
            .info { margin: 20px 0; line-height: 2; }
            a {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📞 Contacto</h1>
            <div class="info">
                <p><strong>Email:</strong> ventas@tiendatech.com</p>
                <p><strong>Teléfono:</strong> +593 99 621 9888</p>
                <p><strong>WhatsApp:</strong> +593 99 621 9688</p>
                <p><strong>Horario:</strong> Lun-Sab 09:00 AM - 18:00 PM</p>
            </div>
            <a href="/">← Volver a la tienda</a>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)