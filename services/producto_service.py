# services/producto_service.py
from database.conexion import MySQLConnection

class ProductoService:
    """Servicio para gestionar productos (CRUD)"""
    
    def obtener_todos(self):
        """Obtener todos los productos desde MySQL"""
        try:
            db = MySQLConnection()
            conn = db.conectar()
            if not conn:
                print("❌ No se pudo conectar a MySQL")
                return []
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM productos ORDER BY id")
                productos = cursor.fetchall()
            conn.close()
            
            print(f"✅ Productos obtenidos: {len(productos)}")
            return productos
        except Exception as e:
            print(f"❌ Error obteniendo productos: {e}")
            return []
    
    def obtener_por_id(self, id):
        """Obtener producto por ID"""
        try:
            db = MySQLConnection()
            conn = db.conectar()
            if not conn:
                return None
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
                producto = cursor.fetchone()
            conn.close()
            return producto
        except Exception as e:
            print(f"❌ Error obteniendo producto {id}: {e}")
            return None
    
    def crear(self, datos):
        """Crear un nuevo producto"""
        try:
            db = MySQLConnection()
            conn = db.conectar()
            if not conn:
                return None
            
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO productos (nombre, precio, cantidad, categoria, descripcion)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    datos['nombre'],
                    datos['precio'],
                    datos['cantidad'],
                    datos['categoria'],
                    datos.get('descripcion', '')
                ))
                conn.commit()
                nuevo_id = cursor.lastrowid
            conn.close()
            return nuevo_id
        except Exception as e:
            print(f"❌ Error creando producto: {e}")
            return None
    
    def actualizar(self, id, datos):
        """Actualizar un producto existente"""
        try:
            db = MySQLConnection()
            conn = db.conectar()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                sql = """
                    UPDATE productos 
                    SET nombre=%s, precio=%s, cantidad=%s, categoria=%s, descripcion=%s
                    WHERE id=%s
                """
                cursor.execute(sql, (
                    datos['nombre'],
                    datos['precio'],
                    datos['cantidad'],
                    datos['categoria'],
                    datos.get('descripcion', ''),
                    id
                ))
                conn.commit()
                actualizados = cursor.rowcount
            conn.close()
            return actualizados > 0
        except Exception as e:
            print(f"❌ Error actualizando producto {id}: {e}")
            return False
    
    def eliminar(self, id):
        """Eliminar un producto"""
        try:
            db = MySQLConnection()
            conn = db.conectar()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
                conn.commit()
                eliminados = cursor.rowcount
            conn.close()
            return eliminados > 0
        except Exception as e:
            print(f"❌ Error eliminando producto {id}: {e}")
            return False
    
    def obtener_por_categoria(self, categoria):
        """Obtener productos por categoría"""
        try:
            db = MySQLConnection()
            conn = db.conectar()
            if not conn:
                return []
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM productos WHERE categoria = %s ORDER BY id", (categoria,))
                productos = cursor.fetchall()
            conn.close()
            return productos
        except Exception as e:
            print(f"❌ Error obteniendo productos por categoría: {e}")
            return []
    
    def obtener_con_bajo_stock(self, limite=5):
        """Obtener productos con stock bajo"""
        try:
            db = MySQLConnection()
            conn = db.conectar()
            if not conn:
                return []
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM productos WHERE cantidad <= %s ORDER BY cantidad", (limite,))
                productos = cursor.fetchall()
            conn.close()
            return productos
        except Exception as e:
            print(f"❌ Error obteniendo productos con bajo stock: {e}")
            return []
    
    def buscar(self, termino):
        """Buscar productos por nombre"""
        try:
            db = MySQLConnection()
            conn = db.conectar()
            if not conn:
                return []
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM productos WHERE nombre LIKE %s ORDER BY id", (f'%{termino}%',))
                productos = cursor.fetchall()
            conn.close()
            return productos
        except Exception as e:
            print(f"❌ Error buscando productos: {e}")
            return []
    
    def obtener_estadisticas(self):
        """Obtener estadísticas del inventario"""
        try:
            db = MySQLConnection()
            conn = db.conectar()
            if not conn:
                return {'total': 0, 'valor_total': 0, 'productos_por_categoria': {}}
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM productos")
                total = cursor.fetchone()
                
                cursor.execute("SELECT SUM(precio * cantidad) as valor_total FROM productos")
                valor = cursor.fetchone()
                
                cursor.execute("SELECT categoria, COUNT(*) as cantidad FROM productos GROUP BY categoria")
                categorias = cursor.fetchall()
            conn.close()
            
            productos_por_categoria = {}
            for cat in categorias:
                productos_por_categoria[cat['categoria']] = cat['cantidad']
            
            return {
                'total': total['total'] if total else 0,
                'valor_total': valor['valor_total'] if valor and valor['valor_total'] else 0,
                'productos_por_categoria': productos_por_categoria
            }
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {'total': 0, 'valor_total': 0, 'productos_por_categoria': {}}