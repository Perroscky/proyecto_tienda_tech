# test_clever.py
"""
Script para probar la conexión a Clever Cloud
Ejecutar: python test_clever.py
"""

from database.conexion import MySQLConnection
import sys

def main():
    print("=" * 60)
    print("🔍 PROBANDO CONEXIÓN A MYSQL")
    print("=" * 60)
    
    # Crear conexión
    print("\n📌 Creando conexión...")
    db = MySQLConnection()
    conn = db.conectar()
    
    if not conn:
        print("\n❌ NO SE PUDO CONECTAR")
        print("\nPosibles causas:")
        print("1. WAMP no está corriendo (icono verde)")
        print("2. Credenciales incorrectas")
        print("3. Base de datos 'proyecto_tienda_tech' no existe")
        sys.exit(1)
    
    print("\n✅ CONEXIÓN EXITOSA")
    
    # Obtener información
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION() as version")
        version = cursor.fetchone()
        print(f"\n📌 Versión MySQL: {version}")
        
        cursor.execute("SELECT DATABASE() as db")
        db_name = cursor.fetchone()
        print(f"📌 Base de datos: {db_name}")
        
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        print(f"\n📌 Tablas encontradas: {len(tablas)}")
        
        if tablas:
            for tabla in tablas:
                print(f"   - {tabla}")
    
    db.cerrar()
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    main()