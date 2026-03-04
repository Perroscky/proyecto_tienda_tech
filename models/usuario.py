import re
from datetime import datetime, date

class Usuario:
    """Clase que representa un usuario de la tienda"""
    
    usuarios_registrados = set()
    
    def __init__(self, id, nombre, email, password, fecha_nacimiento, proveedor="email"):
        # Validar email único
        if email in Usuario.usuarios_registrados:
            raise ValueError(f"El email {email} ya está registrado")
        
        # Validar edad (+18)
        if not self.es_mayor_de_edad(fecha_nacimiento):
            raise ValueError("Debes ser mayor de 18 años")
        
        self._id = id
        self._nombre = nombre
        self._email = email
        self._password = f"enc_{password}_2026"  # Simulación
        self._fecha_nacimiento = fecha_nacimiento
        self._proveedor = proveedor
        self._fecha_registro = datetime.now()
        
        Usuario.usuarios_registrados.add(email)
    
    def es_mayor_de_edad(self, fecha_nacimiento):
        if isinstance(fecha_nacimiento, str):
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
        
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        return edad >= 18
    
    def verificar_password(self, password):
        return self._password == f"enc_{password}_2026"
    
    @property
    def nombre(self):
        return self._nombre
    
    @property
    def email(self):
        return self._email
    
    @property
    def proveedor(self):
        return self._proveedor
    
    @staticmethod
    def validar_email(email):
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None