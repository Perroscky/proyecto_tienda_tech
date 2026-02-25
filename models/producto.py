# models/producto.py

class Producto:
    """
    Clase que representa un producto tecnológico en la tienda.
    Atributos: id, nombre, precio, cantidad, categoria, descripcion
    """
    
    # Conjunto para almacenar IDs únicos (ejemplo de uso de SET)
    ids_utilizados = set()
    
    def __init__(self, id, nombre, precio, cantidad, categoria, descripcion=""):
        """
        Constructor de la clase Producto
        """
        # Validar que el ID sea único usando el conjunto
        if id in Producto.ids_utilizados:
            raise ValueError(f"El ID {id} ya está siendo utilizado por otro producto")
        
        self._id = id
        self._nombre = nombre
        self._precio = precio
        self._cantidad = cantidad
        self._categoria = categoria
        self._descripcion = descripcion
        
        # Agregar ID al conjunto de IDs utilizados
        Producto.ids_utilizados.add(id)
    
    # Getters y Setters (encapsulamiento)
    @property
    def id(self):
        return self._id
    
    @property
    def nombre(self):
        return self._nombre
    
    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor.strip()) == 0:
            raise ValueError("El nombre no puede estar vacío")
        self._nombre = valor
    
    @property
    def precio(self):
        return self._precio
    
    @precio.setter
    def precio(self, valor):
        if valor <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        self._precio = valor
    
    @property
    def cantidad(self):
        return self._cantidad
    
    @cantidad.setter
    def cantidad(self, valor):
        if valor < 0:
            raise ValueError("La cantidad no puede ser negativa")
        self._cantidad = valor
    
    @property
    def categoria(self):
        return self._categoria
    
    @categoria.setter
    def categoria(self, valor):
        self._categoria = valor
    
    @property
    def descripcion(self):
        return self._descripcion
    
    @descripcion.setter
    def descripcion(self, valor):
        self._descripcion = valor
    
    def to_dict(self):
        """
        Convierte el objeto Producto a diccionario para la BD y templates
        """
        return {
            'id': self._id,
            'nombre': self._nombre,
            'precio': self._precio,
            'cantidad': self._cantidad,
            'categoria': self._categoria,
            'descripcion': self._descripcion
        }
    
    def __str__(self):
        """
        Representación en string del producto
        """
        return f"ID: {self._id} | {self._nombre} - ${self._precio:.2f} | Stock: {self._cantidad}"
    
    def __repr__(self):
        return f"Producto(id={self._id}, nombre={self._nombre})"