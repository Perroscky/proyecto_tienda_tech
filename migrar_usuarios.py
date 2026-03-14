# migrar_usuarios.py
"""
SCRIPT PARA MIGRAR SOLO USUARIOS A CLEVER CLOUD
(Los productos ya están migrados)
"""

from database.conexion import MySQLConnection as LocalConnection
import pymysql

def main():
    print("=" * 60)
    print("🚀 MIGRANDO USUARIOS A CLEVER CLOUD")
    print("=" * 60)
    
    # --------------------------------------------
    # Conectar a WAMP (local)
    # --------------------------------------------
    print("\n📌 Conectando a WAMP (local)...")
    local = LocalConnection()
    local.conectar()
    
    if not local.connection:
        print("❌ No se pudo conectar a WAMP")
        return
    
    print("✅ Conectado a WAMP correctamente")
    
    # --------------------------------------------
    # Conectar a Clever Cloud
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
    # Obtener usuarios de WAMP
    # --------------------------------------------
    print("\n📌 Obteniendo usuarios de WAMP...")
    
    # En SQLite no podemos usar PRAGMA, mejor consultamos directamente
    usuarios = local.ejecutar_query("SELECT * FROM usuarios", fetch=True)
    
    if not usuarios:
        print("ℹ️ No hay usuarios para migrar")
    else:
        print(f"✅ Encontrados {len(usuarios)} usuarios en WAMP")
        
        # Mostrar las claves del primer usuario para identificar la estructura
        if usuarios:
            print(f"📋 Estructura de usuario: {list(usuarios[0].keys())}")
        
        insertados = 0
        
        with clever.cursor() as cursor:
            for user in usuarios:
                try:
                    # Determinar el email (puede ser 'email' o 'mail')
                    email = user.get('email') or user.get('mail') or ''
                    if not email:
                        print(f"  ⚠️ Usuario sin email, omitido")
                        continue
                    
                    # Determinar el ID (puede ser 'id' o 'id_usuario')
                    user_id = user.get('id') or user.get('id_usuario')
                    if not user_id:
                        print(f"  ⚠️ Usuario {email} sin ID, omitido")
                        continue
                    
                    # Verificar si ya existe en Clever Cloud
                    cursor.execute("SELECT id_usuario FROM usuarios WHERE mail = %s", (email,))
                    existe = cursor.fetchone()
                    
                    if not existe:
                        cursor.execute("""
                            INSERT INTO usuarios 
                            (id_usuario, nombre, mail, password, fecha_nacimiento, proveedor, rol) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            user_id,
                            user['nombre'],
                            email,
                            user['password'],
                            user['fecha_nacimiento'],
                            user.get('proveedor', 'email'),
                            user.get('rol', 'cliente')
                        ))
                        print(f"  ✅ Usuario: {email}")
                        insertados += 1
                    else:
                        print(f"  ⏩ Usuario {email} ya existe")
                        
                except Exception as e:
                    print(f"  ❌ Error con usuario: {e}")
            
            clever.commit()
        
        print(f"\n✅ {insertados} usuarios migrados correctamente")
    
    # --------------------------------------------
    # Verificar resultados
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
    print("✅ MIGRACIÓN DE USUARIOS COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    main()