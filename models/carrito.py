class ItemCarrito:
    def __init__(self, producto, cantidad):
        self.producto = producto
        self.cantidad = cantidad
    
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad

class Carrito:
    def __init__(self, usuario_id=None):
        self.usuario_id = usuario_id
        self.items = {}  # Diccionario: id_producto -> ItemCarrito
    
    def agregar_item(self, producto, cantidad=1):
        if producto.id in self.items:
            self.items[producto.id].cantidad += cantidad
        else:
            self.items[producto.id] = ItemCarrito(producto, cantidad)
        return True
    
    def quitar_item(self, producto_id):
        if producto_id in self.items:
            del self.items[producto_id]
            return True
        return False
    
    def obtener_total(self):
        return sum(item.subtotal for item in self.items.values())
    
    def obtener_cantidad_items(self):
        return sum(item.cantidad for item in self.items.values())
    
    def to_dict(self):
        return {
            'usuario_id': self.usuario_id,
            'total': self.obtener_total(),
            'cantidad_items': self.obtener_cantidad_items(),
            'items': {
                str(item.producto.id): {
                    'producto_id': item.producto.id,
                    'nombre': item.producto.nombre,
                    'precio': item.producto.precio,
                    'cantidad': item.cantidad,
                    'subtotal': item.subtotal
                } for item in self.items.values()
            }
        }