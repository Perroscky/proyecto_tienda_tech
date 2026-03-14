# migrar_datos_clever.py
"""
SCRIPT PARA MIGRAR DATOS DE WAMP A CLEVER CLOUD
VERSIÓN CORREGIDA - Manejo correcto de IDs de usuarios
"""

from database.conexion import MySQLConnection as LocalConnection
import pymysql

def main():
    print("=" * 60)
    print("🚀 MIGRANDO DATOS A CLEVER CLOUD")
    print("=" * 60)
    
    # --------------------------------------------
    # PASO 1: Conectar a base de datos local (WAMP)
    # --------------------------------------------
    print("\n📌 Conectando a WAMP (local)...")
    local = LocalConnection()
    local.conectar()
    
    if not local.connection:
        print("❌ No se pudo conectar a WAMP")
        print("   Verifica que WAMP esté corriendo (icono verde)")
        return
    
    print("✅ Conectado a WAMP correctamente")
    
    # --------------------------------------------
    # PASO 2: Conectar a Clever Cloud
    # --------------------------------------------
    print("\n📌 Conectando a Clever Cloud...")
    
    CLEVER_CONFIG = {
        'host': 'bept0vtgcu5nz0xzcgol-mysql.services.clever-cloud.com',
        'user': 'ubtgm9wmyvdrvplt',
        'password': 'lbubp7zT64xQizwtzbih',
        'database': 'bept0vtgcu5nz0xzcgol',
        'port': 3306,
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    try:
        clever = pymysql.connect(**CLEVER_CONFIG)
        print("✅ Conectado a Clever Cloud correctamente")
    except Exception as e:
        print(f"❌ Error conectando a Clever Cloud: {e}")
        local.cerrar()
        return
    
    # --------------------------------------------
    # PASO 3: Migrar productos (YA FUNCIONA)
    # --------------------------------------------
    print("\n📌 Obteniendo productos de WAMP...")
    productos = local.ejecutar_query("SELECT * FROM productos", fetch=True)
    
    if not productos:
        print("⚠️ No hay productos en WAMP para migrar")
    else:
        print(f"✅ Encontrados {len(productos)} productos en WAMP")
        
        print("\n📌 Insertando productos en Clever Cloud...")
        insertados = 0
        
        with clever.cursor() as cursor:
            for prod in productos:
                try:
                    cursor.execute("""
                        INSERT INTO productos 
                        (id, nombre, precio, cantidad, categoria, descripcion) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        prod['id'],
                        prod['nombre'],
                        prod['precio'],
                        prod['cantidad'],
                        prod['categoria'],
                        prod.get('descripcion', '')
                    ))
                    print(f"  ✅ Producto {prod['id']}: {prod['nombre']}")
                    insertados += 1
                except Exception as e:
                    print(f"  ❌ Error con producto {prod['id']}: {e}")
            
            clever.commit()
        
        print(f"\n✅ {insertados} productos migrados correctamente")
    
    # --------------------------------------------
    # PASO 4: Migrar usuarios (CORREGIDO)
    # --------------------------------------------
    print("\n📌 Obteniendo usuarios de WAMP...")
    
    # En SQLite la columna puede ser 'id' o 'id_usuario'
    # Vamos a obtener los nombres de las columnas primero
    columnas_usuarios = local.ejecutar_query("PRAGMA table_info(usuarios)", fetch=True)
    nombres_columnas = [col['name'] for col in columnas_usuarios]
    print(f"📋 Columnas en tabla usuarios local: {nombres_columnas}")
    
    usuarios = local.ejecutar_query("SELECT * FROM usuarios", fetch=True)
    
    if not usuarios:
        print("ℹ️ No hay usuarios para migrar")
    else:
        print(f"✅ Encontrados {len(usuarios)} usuarios en WAMP")
        
        # Determinar cómo se llama la columna ID
        if 'id' in nombres_columnas:
            id_col = 'id'
        elif 'id_usuario' in nombres_columnas:
            id_col = 'id_usuario'
        else:
            id_col = None
            print("⚠️ No se encontró columna de ID en usuarios")
        
        insertados_usuarios = 0
        
        with clever.cursor() as cursor:
            for user in usuarios:
                try:
                    # Obtener email (puede ser 'email' o 'mail')
                    email = user.get('email') or user.get('mail') or ''
                    
                    # Verificar si ya existe
                    cursor.execute("SELECT id_usuario FROM usuarios WHERE mail = %s", (email,))
                    existe = cursor.fetchone()
                    
                    if not existe and id_col:
                        cursor.execute("""
                            INSERT INTO usuarios 
                            (id_usuario, nombre, mail, password, fecha_nacimiento, proveedor, rol) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            user[id_col],
                            user['nombre'],
                            email,
                            user['password'],
                            user['fecha_nacimiento'],
                            user.get('proveedor', 'email'),
                            user.get('rol', 'cliente')
                        ))
                        print(f"  ✅ Usuario: {email}")
                        insertados_usuarios += 1
                    else:
                        if existe:
                            print(f"  ⏩ Usuario {email} ya existe")
                            
                except Exception as e:
                    print(f"  ❌ Error con usuario {user.get('email', 'desconocido')}: {e}")
            
            clever.commit()
        
        print(f"\n✅ {insertados_usuarios} usuarios migrados correctamente")
    
    # --------------------------------------------
    # PASO 5: Verificar resultados
    # --------------------------------------------
    print("\n📌 Verificando datos en Clever Cloud...")
    
    with clever.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM productos")
        total_productos = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        total_usuarios = cursor.fetchone()
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   Productos en Clever Cloud: {total_productos['total']}")
    print(f"   Usuarios en Clever Cloud: {total_usuarios['total']}")
    
    # --------------------------------------------
    # Cerrar conexiones
    # --------------------------------------------
    local.cerrar()
    clever.close()
    
    print("\n" + "=" * 60)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    main()