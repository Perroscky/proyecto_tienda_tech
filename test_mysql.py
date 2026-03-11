# test_mysql.py
from database.conexion import MySQLConnection

print("🔍 Probando conexión a MySQL...")
print("=" * 40)
print(f"📌 Usuario: root")
print(f"📌 Contraseña: 123456")
print("=" * 40)

try:
    db = MySQLConnection()
    if db.conectar():
        print("✅ Conexión establecida correctamente")
        
        # Probar consulta simple
        resultado = db.ejecutar_query("SELECT VERSION() as version", fetch=True)
        if resultado:
            print(f"📌 Versión MySQL: {resultado[0]['version']}")
        
        # Probar creación de base de datos
        db.ejecutar_query("CREATE DATABASE IF NOT EXISTS proyecto_tienda_tech")
        print("✅ Base de datos 'proyecto_tienda_tech' verificada")
        
        db.cerrar()
        print("🎉 Todo funcionando correctamente")
    else:
        print("❌ No se pudo conectar")
        print("\n📌 POSIBLES SOLUCIONES:")
        print("1. Verifica que WAMP esté corriendo (icono verde)")
        print("2. Verifica que la contraseña '123456' sea correcta")
        print("3. Prueba con contraseña vacía en phpMyAdmin")
except Exception as e:
    print(f"❌ Error: {e}")