# models/usuario.py
"""
Modelo de Usuario con Flask-Login y Werkzeug
Compatibilidad con contraseñas antiguas y nuevas
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime, date

class Usuario(UserMixin):
    """Clase que representa un usuario de la tienda"""
    
    usuarios_registrados = set()
    
    def __init__(self, id, nombre, email, password, fecha_nacimiento, proveedor="email"):
        # Validar email único (solo para nuevos registros)
        if id is None and email in Usuario.usuarios_registrados:
            raise ValueError(f"El email {email} ya está registrado")
        
        # Validar edad (+18) solo para nuevos registros
        if id is None and not self.es_mayor_de_edad(fecha_nacimiento):
            raise ValueError("Debes ser mayor de 18 años")
        
        self.id = id
        self.nombre = nombre
        self.email = email
        
        # 🔥 NUEVO: Cifrado con Werkzeug, pero manteniendo compatibilidad
        if password and not password.startswith('enc_') and not password.startswith('pbkdf2:'):
            self.password = generate_password_hash(password)
        else:
            self.password = password
        
        self.fecha_nacimiento = fecha_nacimiento
        self.proveedor = proveedor
        self.fecha_registro = datetime.now()
        
        if id is None:
            Usuario.usuarios_registrados.add(email)
    
    def get_id(self):
        """Método requerido por Flask-Login"""
        return str(self.id)
    
    def es_mayor_de_edad(self, fecha_nacimiento):
        """Verifica si el usuario es mayor de 18 años"""
        if isinstance(fecha_nacimiento, str):
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
        
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        return edad >= 18
    
    def verificar_password(self, password):
        """
        Verifica la contraseña con compatibilidad hacia atrás
        - Si es formato antiguo (enc_xxx_2026) → verifica directamente
        - Si es formato nuevo (pbkdf2:) → usa Werkzeug
        """
        # Formato antiguo (usuarios existentes)
        if self.password.startswith('enc_') and self.password == f"enc_{password}_2026":
            return True
        
        # Formato nuevo con Werkzeug
        try:
            return check_password_hash(self.password, password)
        except:
            return False
    
    @staticmethod
    def validar_email(email):
        """Valida el formato del email"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def to_dict(self):
        """Convierte el usuario a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'proveedor': self.proveedor,
            'fecha_registro': self.fecha_registro.strftime("%Y-%m-%d %H:%M:%S")
        }