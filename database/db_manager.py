# database/db_manager.py

import sqlite3
import os

class DatabaseManager:
    """
    Clase para manejar todas las operaciones con SQLite
    para la tienda proyecto_tienda_tech
    """
    
    def __init__(self, db_name="proyecto_tienda_tech.db"):
        """
        Constructor: establece la conexión y crea las tablas si no existen
        """
        # Obtener la ruta absoluta para la base de datos
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), db_name)
        self.crear_tablas()
        self.crear_tabla_usuarios()
        self.crear_tabla_carrito()
    
    def get_connection(self):
        """
        Obtiene una conexión a la base de datos
        """
        return sqlite3.connect(self.db_path)
    
    def crear_tablas(self):
        """
        Crea las tablas necesarias si no existen
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de productos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    cantidad INTEGER NOT NULL,
                    categoria TEXT NOT NULL,
                    descripcion TEXT
                )
            ''')
            
            # Índice para búsquedas rápidas por nombre
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_productos_nombre 
                ON productos(nombre)
            ''')
            
            conn.commit()
            print("✅ Tabla de productos creada/verificada correctamente")
    
    def crear_tabla_usuarios(self):
        """Crea la tabla de usuarios en la base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    fecha_nacimiento TEXT NOT NULL,
                    proveedor TEXT DEFAULT 'email',
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("✅ Tabla 'usuarios' creada/verificada")
    
    def crear_tabla_carrito(self):
        """Crea las tablas relacionadas con el carrito"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de carritos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS carritos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT DEFAULT 'activo',
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            ''')
            
            # Tabla de items del carrito
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS carrito_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    carrito_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (carrito_id) REFERENCES carritos(id),
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            ''')
            
            conn.commit()
            print("✅ Tablas de carrito creadas/verificadas")
    
    # ----- MÉTODOS PARA PRODUCTOS -----
    def insertar_producto(self, producto):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO productos (id, nombre, precio, cantidad, categoria, descripcion)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                producto.id,
                producto.nombre,
                producto.precio,
                producto.cantidad,
                producto.categoria,
                producto.descripcion
            ))
            conn.commit()
            return cursor.lastrowid
    
    def obtener_todos_productos(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM productos ORDER BY id')
            return cursor.fetchall()
    
    def obtener_producto_por_id(self, id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM productos WHERE id = ?', (id,))
            return cursor.fetchone()
    
    def obtener_productos_por_nombre(self, nombre):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM productos WHERE nombre LIKE ?', (f'%{nombre}%',))
            return cursor.fetchall()
    
    def obtener_productos_por_categoria(self, categoria):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM productos WHERE categoria = ?', (categoria,))
            return cursor.fetchall()
    
    # ----- MÉTODOS PARA USUARIOS -----
    def insertar_usuario(self, usuario):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (nombre, email, password, fecha_nacimiento, proveedor)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                usuario.nombre,
                usuario.email,
                usuario.password,
                usuario.fecha_nacimiento if isinstance(usuario.fecha_nacimiento, str) 
                    else usuario.fecha_nacimiento.strftime("%Y-%m-%d"),
                usuario.proveedor
            ))
            conn.commit()
            return cursor.lastrowid
    
    def obtener_usuario_por_email(self, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            return cursor.fetchone()
    
    def obtener_usuario_por_id(self, id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
            return cursor.fetchone()
    
    def crear_carrito(self, usuario_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO carritos (usuario_id, estado)
                VALUES (?, 'activo')
            ''', (usuario_id,))
            conn.commit()
            return cursor.lastrowid