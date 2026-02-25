# models/inventario.py

from models.producto import Producto
from database.db_manager import DatabaseManager # type: ignore
import sqlite3

class Inventario:
    """
    Clase que gestiona el inventario de productos tecnológicos
    usando un diccionario en memoria y sincroniza con SQLite
    """
    
    # Constantes para categorías válidas de tu tienda tech (ejemplo de TUPLA)
    CATEGORIAS_VALIDAS = ('computadoras', 'perifericos', 'audio', 'otros')
    
    def __init__(self):
        """
        Inicializa el inventario con un diccionario vacío y conecta a la BD
        """
        self.productos = {}  # Diccionario: clave=id, valor=objeto Producto
        self.db = DatabaseManager("proyecto_tienda_tech.db")
        self.cargar_desde_bd()
    
    def cargar_desde_bd(self):
        """
        Carga todos los productos desde la base de datos al diccionario
        """
        try:
            productos_bd = self.db.obtener_todos_productos()
            for prod in productos_bd:
                producto = Producto(
                    id=prod[0],
                    nombre=prod[1],
                    precio=prod[2],
                    cantidad=prod[3],
                    categoria=prod[4],
                    descripcion=prod[5] if prod[5] else ""
                )
                self.productos[prod[0]] = producto
            
            print(f"✅ {len(self.productos)} productos cargados desde la BD")
        except Exception as e:
            print(f"Error cargando productos: {e}")
    
    # ----- OPERACIONES CRUD -----
    
    def agregar_producto(self, id, nombre, precio, cantidad, categoria, descripcion=""):
        """
        Agrega un nuevo producto al inventario (en memoria y BD)
        """
        # Validar categoría con la tupla
        if categoria not in self.CATEGORIAS_VALIDAS:
            raise ValueError(f"Categoría no válida. Debe ser una de: {self.CATEGORIAS_VALIDAS}")
        
        # Verificar si el ID ya existe
        if id in self.productos:
            raise ValueError(f"Ya existe un producto con ID {id}")
        
        # Crear el objeto Producto
        nuevo_producto = Producto(id, nombre, precio, cantidad, categoria, descripcion)
        
        # Guardar en base de datos primero
        try:
            self.db.insertar_producto(nuevo_producto)
        except sqlite3.IntegrityError:
            raise ValueError(f"Error: El ID {id} ya existe en la base de datos")
        
        # Si la BD lo acepta, agregar a memoria
        self.productos[id] = nuevo_producto
        return nuevo_producto
    
    def eliminar_producto(self, id):
        """
        Elimina un producto del inventario
        """
        if id not in self.productos:
            return False
        
        # Eliminar de base de datos
        if self.db.eliminar_producto(id):
            # Eliminar del diccionario en memoria
            del self.productos[id]
            # Remover ID del conjunto de IDs utilizados
            if id in Producto.ids_utilizados:
                Producto.ids_utilizados.remove(id)
            return True
        return False
    
    def actualizar_producto(self, id, **kwargs):
        """
        Actualiza los datos de un producto
        kwargs puede incluir: nombre, precio, cantidad, categoria, descripcion
        """
        if id not in self.productos:
            return False
        
        producto = self.productos[id]
        
        # Actualizar en base de datos
        if self.db.actualizar_producto(id, **kwargs):
            # Actualizar en memoria
            if 'nombre' in kwargs:
                producto.nombre = kwargs['nombre']
            if 'precio' in kwargs:
                producto.precio = kwargs['precio']
            if 'cantidad' in kwargs:
                producto.cantidad = kwargs['cantidad']
            if 'categoria' in kwargs:
                producto.categoria = kwargs['categoria']
            if 'descripcion' in kwargs:
                producto.descripcion = kwargs['descripcion']
            
            return True
        return False
    
    def buscar_productos(self, termino):
        """
        Busca productos por nombre (parcial)
        """
        resultados = []
        termino_lower = termino.lower()
        
        for producto in self.productos.values():
            if termino_lower in producto.nombre.lower():
                resultados.append(producto)
        
        return resultados
    
    def obtener_producto_por_id(self, id):
        """
        Obtiene un producto por su ID
        """
        return self.productos.get(id)
    
    def obtener_todos(self):
        """
        Obtiene todos los productos del inventario
        """
        return list(self.productos.values())
    
    def obtener_por_categoria(self, categoria):
        """
        Obtiene productos de una categoría específica
        """
        return [p for p in self.productos.values() if p.categoria == categoria]
    
    def obtener_productos_con_bajo_stock(self, limite=5):
        """
        Obtiene productos con stock menor al límite
        """
        return [p for p in self.productos.values() if p.cantidad <= limite]
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas del inventario
        Devuelve un diccionario con: total_productos, valor_total, productos_por_categoria
        """
        total_productos = len(self.productos)
        valor_total = sum(p.precio * p.cantidad for p in self.productos.values())
        
        # Usando un diccionario para contar por categoría
        productos_por_categoria = {}
        for p in self.productos.values():
            productos_por_categoria[p.categoria] = productos_por_categoria.get(p.categoria, 0) + 1
        
        return {
            'total_productos': total_productos,
            'valor_total': valor_total,
            'productos_por_categoria': productos_por_categoria
        }
    
    def __len__(self):
        """Devuelve la cantidad de productos en el inventario"""
        return len(self.productos)
    
    def __iter__(self):
        """Permite iterar sobre los productos"""
        return iter(self.productos.values())