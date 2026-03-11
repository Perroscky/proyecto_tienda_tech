# database/crear_tablas.py
"""
Script para crear todas las tablas necesarias en MySQL
"""

from database.conexion import MySQLConnection

def crear_tablas():
    """Crea las tablas del sistema en MySQL"""
    
    queries = [
        # Tabla usuarios
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            mail VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            fecha_nacimiento DATE NOT NULL,
            proveedor VARCHAR(20) DEFAULT 'email',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # Tabla productos
        """
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(200) NOT NULL,
            precio DECIMAL(10,2) NOT NULL,
            cantidad INT NOT NULL DEFAULT 0,
            categoria VARCHAR(50) NOT NULL,
            descripcion TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # Tabla carritos
        """
        CREATE TABLE IF NOT EXISTS carritos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(20) DEFAULT 'activo',
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # Tabla carrito_items
        """
        CREATE TABLE IF NOT EXISTS carrito_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            carrito_id INT NOT NULL,
            producto_id INT NOT NULL,
            cantidad INT NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (carrito_id) REFERENCES carritos(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # Tabla ventas
        """
        CREATE TABLE IF NOT EXISTS ventas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            total DECIMAL(10,2) NOT NULL,
            fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(20) DEFAULT 'completada',
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # Tabla venta_detalles
        """
        CREATE TABLE IF NOT EXISTS venta_detalles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            venta_id INT NOT NULL,
            producto_id INT NOT NULL,
            cantidad INT NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    ]
    
    print("🚀 Creando tablas en MySQL...")
    print("-" * 40)
    
    db = MySQLConnection()
    db.conectar()
    
    if not db.connection:
        print("❌ No se pudo conectar a MySQL")
        return
    
    for i, query in enumerate(queries):
        try:
            db.ejecutar_query(query)
            print(f"✅ Tabla {i+1} creada/verificada")
        except Exception as e:
            print(f"❌ Error en tabla {i+1}: {e}")
    
    db.cerrar()
    print("🎉 Proceso completado")

def migrar_datos_iniciales():
    """Inserta datos de ejemplo"""
    
    db = MySQLConnection()
    db.conectar()
    
    if not db.connection:
        return
    
    try:
        # Verificar si hay productos
        productos = db.ejecutar_query("SELECT COUNT(*) as total FROM productos", fetch=True)
        
        if productos and productos[0]['total'] == 0:
            productos_iniciales = [
                ('Laptop Dell XPS 15', 1299.00, 10, 'computadoras', 'Laptop de alto rendimiento'),
                ('Mouse Logitech MX Master 3', 99.00, 15, 'perifericos', 'Mouse inalámbrico'),
                ('Teclado Mecánico Corsair K95', 179.00, 8, 'perifericos', 'Teclado RGB'),
                ('Monitor LG UltraWide 34"', 599.00, 5, 'computadoras', 'Monitor ultrawide'),
                ('Audífonos Sony WH-1000XM5', 399.00, 7, 'audio', 'Cancelación de ruido'),
                ('Webcam Logitech C920', 79.00, 12, 'perifericos', 'Webcam Full HD')
            ]
            
            for prod in productos_iniciales:
                query = """
                    INSERT INTO productos (nombre, precio, cantidad, categoria, descripcion)
                    VALUES (%s, %s, %s, %s, %s)
                """
                db.ejecutar_query(query, prod)
            
            print("✅ Productos iniciales insertados")
        else:
            print("ℹ️ Ya existen productos en la base de datos")
            
    except Exception as e:
        print(f"❌ Error insertando datos: {e}")
    
    db.cerrar()

if __name__ == "__main__":
    crear_tablas()
    migrar_datos_iniciales()