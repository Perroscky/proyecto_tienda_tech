# database/conexion.py
"""
Configuración de conexión a MySQL usando root con contraseña
"""

import pymysql
from pymysql import Error

class MySQLConnection:
    """Clase para manejar la conexión a MySQL con root"""
    
    def __init__(self):
        """Configuración de conexión con root"""
        self.config = {
            'host': 'localhost',
            'user': 'root',              # Usuario root
            'password': '123456',         # 🔥 Tu contraseña
            'database': 'proyecto_tienda_tech',
            'port': 3306,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.connection = None
    
    def conectar(self):
        """Establece conexión con MySQL"""
        try:
            self.connection = pymysql.connect(**self.config)
            print("✅ Conectado a MySQL correctamente")
            return self.connection
        except Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            return None
    
    def cerrar(self):
        """Cierra la conexión"""
        if self.connection:
            self.connection.close()
            print("🔒 Conexión cerrada")
    
    def ejecutar_query(self, query, params=None, fetch=False):
        """Ejecuta una consulta SQL"""
        cursor = None
        try:
            if not self.connection:
                self.conectar()
            
            if not self.connection:
                return None
                
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                resultado = cursor.fetchall()
                return resultado
            else:
                self.connection.commit()
                return cursor.lastrowid
                
        except Error as e:
            print(f"❌ Error en consulta: {e}")
            if not fetch:
                self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    def __enter__(self):
        self.conectar()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()