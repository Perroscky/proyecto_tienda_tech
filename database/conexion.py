# database/conexion.py
"""
CONEXIÓN A MYSQL - Versión para Clever Cloud y Local
"""

import pymysql
from pymysql import Error
import os

class MySQLConnection:
    """
    Clase que maneja la conexión a MySQL.
    - En LOCAL: usa WAMP (root/contraseña vacía)
    - En RENDER: usa Clever Cloud (variables de entorno)
    """
    
    def __init__(self):
        """Configura la conexión según el entorno"""
        
        # Detectar si estamos en Render (producción)
        if os.environ.get('RENDER'):
            # 🔥 MODO PRODUCCIÓN - Usar Clever Cloud
            print("🌐 Modo PRODUCCIÓN: Conectando a Clever Cloud...")
            
            # Obtener variables de entorno (las configuraremos en Render)
            self.config = {
                'host': os.environ.get('CLEVER_MYSQL_HOST'),
                'user': os.environ.get('CLEVER_MYSQL_USER'),
                'password': os.environ.get('CLEVER_MYSQL_PASSWORD'),
                'database': os.environ.get('CLEVER_MYSQL_DATABASE'),
                'port': int(os.environ.get('CLEVER_MYSQL_PORT', 3306)),
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor
            }
            
            # Verificar que todas las variables existen
            for key, value in self.config.items():
                if key != 'port' and value is None:
                    raise ValueError(f"❌ Variable de entorno {key} no está definida en Render")
            
        else:
            # 🔥 MODO DESARROLLO LOCAL - Usar WAMP (contraseña vacía)
            print("💻 Modo DESARROLLO LOCAL: Conectando a WAMP...")
            self.config = {
                'host': 'localhost',
                'user': 'root',
                'password': '123456',  # 🔥
                'database': 'proyecto_tienda_tech',
                'port': 3306,
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor
            }
        
        self.connection = None
        print(f"📋 Conectando a: {self.config['host']}/{self.config['database']}")
    
    def conectar(self):
        """Establece la conexión con MySQL"""
        try:
            self.connection = pymysql.connect(**self.config)
            print("✅ Conexión exitosa a MySQL")
            return self.connection
        except Error as e:
            print(f"❌ Error de conexión: {e}")
            return None
    
    def cerrar(self):
        """Cierra la conexión"""
        if self.connection:
            self.connection.close()
            print("🔒 Conexión cerrada")
    
    def ejecutar_query(self, query, params=None, fetch=False):
        """
        Ejecuta una consulta SQL
        
        Args:
            query (str): Consulta SQL
            params (tuple): Parámetros para la consulta
            fetch (bool): True para SELECT, False para INSERT/UPDATE/DELETE
        
        Returns:
            - Si fetch=True: Lista de resultados
            - Si fetch=False: ID del último insert o None
        """
        cursor = None
        try:
            # Conectar si no hay conexión
            if not self.connection:
                self.conectar()
            
            if not self.connection:
                return None
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                # Para consultas SELECT
                resultados = cursor.fetchall()
                return resultados
            else:
                # Para INSERT, UPDATE, DELETE
                self.connection.commit()
                return cursor.lastrowid
                
        except Error as e:
            print(f"❌ Error en consulta: {e}")
            print(f"   Query: {query}")
            print(f"   Params: {params}")
            
            if not fetch:
                self.connection.rollback()
            return None
            
        finally:
            if cursor:
                cursor.close()
    
    def __enter__(self):
        """Permite usar 'with' - contexto de entrada"""
        self.conectar()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Permite usar 'with' - contexto de salida"""
        self.cerrar()