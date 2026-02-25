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
            
            # Tabla de clientes (opcional para el proyecto)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE,
                    telefono TEXT,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Índice para búsquedas rápidas por nombre
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_productos_nombre 
                ON productos(nombre)
            ''')
            
            conn.commit()
            print("✅ Tablas creadas/verificadas correctamente")
    
    # ----- OPERACIONES CRUD PARA PRODUCTOS -----
    
    def insertar_producto(self, producto):
        """
        Inserta un nuevo producto en la base de datos
        """
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
        """
        Obtiene todos los productos de la base de datos
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM productos ORDER BY id')
            return cursor.fetchall()
    
    def obtener_producto_por_id(self, id):
        """
        Obtiene un producto por su ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM productos WHERE id = ?', (id,))
            return cursor.fetchone()
    
    def obtener_productos_por_nombre(self, nombre):
        """
        Busca productos por nombre (búsqueda parcial)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM productos WHERE nombre LIKE ?', (f'%{nombre}%',))
            return cursor.fetchall()
    
    def obtener_productos_por_categoria(self, categoria):
        """
        Obtiene productos por categoría
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM productos WHERE categoria = ?', (categoria,))
            return cursor.fetchall()
    
    def actualizar_producto(self, id, nombre=None, precio=None, cantidad=None, 
                           categoria=None, descripcion=None):
        """
        Actualiza los datos de un producto
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir la consulta dinámicamente
            updates = []
            valores = []
            
            if nombre is not None:
                updates.append("nombre = ?")
                valores.append(nombre)
            if precio is not None:
                updates.append("precio = ?")
                valores.append(precio)
            if cantidad is not None:
                updates.append("cantidad = ?")
                valores.append(cantidad)
            if categoria is not None:
                updates.append("categoria = ?")
                valores.append(categoria)
            if descripcion is not None:
                updates.append("descripcion = ?")
                valores.append(descripcion)
            
            if not updates:
                return False
            
            valores.append(id)
            query = f"UPDATE productos SET {', '.join(updates)} WHERE id = ?"
            
            cursor.execute(query, valores)
            conn.commit()
            return cursor.rowcount > 0
    
    def eliminar_producto(self, id):
        """
        Elimina un producto por su ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM productos WHERE id = ?', (id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def producto_existe(self, id):
        """
        Verifica si un producto existe en la base de datos
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM productos WHERE id = ?', (id,))
            return cursor.fetchone() is not None
    
    # ----- MÉTODOS PARA MIGRACIÓN DE DATOS INICIALES -----
    
    def migrar_productos_iniciales(self):
        """
        Migra los productos del diccionario actual a la base de datos
        """
        try:
            from app import productos_db
        except ImportError:
            print("No se pudieron importar los productos iniciales")
            return 0
        
        productos_migrados = 0
        for key, data in productos_db.items():
            try:
                # Extraer el precio (eliminar $ y comas)
                precio_str = data['precio'].replace('$', '').replace(',', '')
                precio = float(precio_str)
                
                # Determinar categoría basado en el key
                categoria = self.determinar_categoria(key)
                
                # Determinar cantidad basado en el stock
                cantidad = 10 if data['stock'] == 'Disponible' else 3
                
                # Generar un ID numérico (usando hash)
                id_temp = abs(hash(key)) % 10000
                
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO productos (id, nombre, precio, cantidad, categoria, descripcion)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        id_temp,
                        data['nombre'],
                        precio,
                        cantidad,
                        categoria,
                        data.get('descripcion', '')
                    ))
                    conn.commit()
                    if cursor.rowcount > 0:
                        productos_migrados += 1
            except Exception as e:
                print(f"Error migrando {key}: {e}")
        
        print(f"✅ {productos_migrados} productos migrados a la base de datos")
        return productos_migrados
    
    def determinar_categoria(self, key):
        """
        Determina la categoría basada en el key del producto
        """
        categorias_map = {
            'laptop': 'computadoras',
            'mouse': 'perifericos',
            'teclado': 'perifericos',
            'monitor': 'computadoras',
            'audifonos': 'audio',
            'webcam': 'perifericos'
        }
        return categorias_map.get(key, 'otros')