# ver_usuarios.py
import sqlite3
import os

print("🔍 VERIFICANDO USUARIOS EN BASE DE DATOS")
print("=" * 50)

# Conectar a SQLite
db_path = os.path.join(os.path.dirname(__file__), 'proyecto_tienda_tech.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar tabla usuarios
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
if cursor.fetchone():
    print("✅ Tabla 'usuarios' existe")
    
    # Contar usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    count = cursor.fetchone()[0]
    print(f"📊 Total usuarios: {count}")
    
    # Listar usuarios
    if count > 0:
        cursor.execute("SELECT id, nombre, email, fecha_registro FROM usuarios")
        usuarios = cursor.fetchall()
        print("\n📋 USUARIOS REGISTRADOS:")
        for u in usuarios:
            print(f"   ID: {u[0]} | Nombre: {u[1]} | Email: {u[2]} | Fecha: {u[3]}")
    else:
        print("❌ No hay usuarios registrados")
else:
    print("❌ Tabla 'usuarios' NO existe")
    print("   Ejecuta database/crear_tablas.py para crearla")

conn.close()