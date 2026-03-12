# test_usuario.py
from models.usuario import Usuario

print("🔍 Probando clase Usuario...")
print("=" * 40)

try:
    # Crear usuario de prueba
    user = Usuario(None, "Luis Test", "luis@test.com", "123456", "2000-01-01")
    
    print(f"✅ Usuario creado correctamente")
    print(f"   Nombre: {user.nombre}")
    print(f"   Email: {user.email}")
    print(f"   Password: {user.password}")
    print(f"   Verificar '123456': {user.verificar_password('123456')}")
    print(f"   Verificar 'wrong': {user.verificar_password('wrong')}")
    
except Exception as e:
    print(f"❌ Error: {e}")