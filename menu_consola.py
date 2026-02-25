# menu_consola.py

import os
import sys
from models.inventario import Inventario
from models.producto import Producto

class MenuConsola:
    """
    Menú interactivo para gestionar el inventario de proyecto_tienda_tech
    """
    
    def __init__(self):
        self.inventario = Inventario()
        self.opciones = {
            '1': self.mostrar_productos,
            '2': self.agregar_producto,
            '3': self.eliminar_producto,
            '4': self.actualizar_producto,
            '5': self.buscar_producto,
            '6': self.mostrar_por_categoria,
            '7': self.mostrar_bajo_stock,
            '8': self.mostrar_estadisticas,
            '9': self.salir
        }
    
    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_menu(self):
        """Muestra el menú principal"""
        self.limpiar_pantalla()
        print("=" * 70)
        print(" 🏪 SISTEMA DE GESTIÓN DE INVENTARIO - PROYECTO_TIENDA_TECH")
        print("=" * 70)
        print("\n📋 MENÚ PRINCIPAL:")
        print("  1️⃣  Ver todos los productos")
        print("  2️⃣  Agregar nuevo producto")
        print("  3️⃣  Eliminar producto")
        print("  4️⃣  Actualizar producto")
        print("  5️⃣  Buscar producto por nombre")
        print("  6️⃣  Ver productos por categoría")
        print("  7️⃣  Ver productos con bajo stock")
        print("  8️⃣  Ver estadísticas del inventario")
        print("  9️⃣  Salir")
        print("=" * 70)
    
    def ejecutar(self):
        """Ejecuta el menú principal"""
        while True:
            self.mostrar_menu()
            opcion = input("\n👉 Selecciona una opción (1-9): ").strip()
            
            if opcion in self.opciones:
                self.opciones[opcion]()
                if opcion != '9':
                    input("\n⏎ Presiona Enter para continuar...")
            else:
                print("\n❌ Opción no válida. Intenta de nuevo.")
                input("⏎ Presiona Enter para continuar...")
    
    # ----- MÉTODOS PARA CADA OPCIÓN DEL MENÚ -----
    
    def mostrar_productos(self):
        """Muestra todos los productos del inventario"""
        self.limpiar_pantalla()
        print("📦 LISTADO COMPLETO DE PRODUCTOS - PROYECTO_TIENDA_TECH")
        print("-" * 60)
        
        productos = self.inventario.obtener_todos()
        
        if not productos:
            print("❌ No hay productos en el inventario.")
            return
        
        print(f"Total: {len(productos)} productos\n")
        
        for producto in productos:
            print(f"ID: {producto.id}")
            print(f"📌 Nombre: {producto.nombre}")
            print(f"💰 Precio: ${producto.precio:.2f}")
            print(f"📦 Cantidad: {producto.cantidad}")
            print(f"🏷️ Categoría: {producto.categoria}")
            print(f"📝 Descripción: {producto.descripcion}")
            print("-" * 40)
    
    def agregar_producto(self):
        """Agrega un nuevo producto al inventario"""
        self.limpiar_pantalla()
        print("➕ AGREGAR NUEVO PRODUCTO TECNOLÓGICO")
        print("-" * 40)
        
        try:
            id = int(input("ID del producto: "))
            nombre = input("Nombre del producto: ").strip()
            precio = float(input("Precio del producto: $"))
            cantidad = int(input("Cantidad en stock: "))
            
            print(f"\nCategorías válidas: {Inventario.CATEGORIAS_VALIDAS}")
            categoria = input("Categoría: ").strip().lower()
            
            descripcion = input("Descripción (opcional): ").strip()
            
            producto = self.inventario.agregar_producto(
                id, nombre, precio, cantidad, categoria, descripcion
            )
            
            print(f"\n✅ Producto '{producto.nombre}' agregado exitosamente!")
            
        except ValueError as e:
            print(f"\n❌ Error: {e}")
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
    
    def eliminar_producto(self):
        """Elimina un producto del inventario"""
        self.limpiar_pantalla()
        print("🗑️ ELIMINAR PRODUCTO")
        print("-" * 40)
        
        try:
            id = int(input("ID del producto a eliminar: "))
            
            producto = self.inventario.obtener_producto_por_id(id)
            if not producto:
                print(f"❌ No existe producto con ID {id}")
                return
            
            print(f"\n📌 Producto a eliminar: {producto.nombre}")
            confirmar = input("¿Estás seguro? (s/n): ").strip().lower()
            
            if confirmar == 's':
                if self.inventario.eliminar_producto(id):
                    print(f"✅ Producto eliminado exitosamente!")
                else:
                    print("❌ Error al eliminar el producto")
            else:
                print("Operación cancelada")
                
        except ValueError:
            print("❌ Error: El ID debe ser un número")
    
    def actualizar_producto(self):
        """Actualiza los datos de un producto"""
        self.limpiar_pantalla()
        print("✏️ ACTUALIZAR PRODUCTO")
        print("-" * 40)
        
        try:
            id = int(input("ID del producto a actualizar: "))
            
            producto = self.inventario.obtener_producto_por_id(id)
            if not producto:
                print(f"❌ No existe producto con ID {id}")
                return
            
            print(f"\n📌 Producto actual: {producto.nombre}")
            print("Deja en blanco los campos que no quieras modificar")
            
            datos_actualizados = {}
            
            nombre = input(f"Nuevo nombre [{producto.nombre}]: ").strip()
            if nombre:
                datos_actualizados['nombre'] = nombre
            
            precio_str = input(f"Nuevo precio ${producto.precio:.2f} [$]: ").strip()
            if precio_str:
                datos_actualizados['precio'] = float(precio_str)
            
            cantidad_str = input(f"Nueva cantidad [{producto.cantidad}]: ").strip()
            if cantidad_str:
                datos_actualizados['cantidad'] = int(cantidad_str)
            
            categoria = input(f"Nueva categoría [{producto.categoria}]: ").strip()
            if categoria:
                datos_actualizados['categoria'] = categoria
            
            descripcion = input(f"Nueva descripción [{producto.descripcion}]: ").strip()
            if descripcion:
                datos_actualizados['descripcion'] = descripcion
            
            if datos_actualizados:
                if self.inventario.actualizar_producto(id, **datos_actualizados):
                    print(f"\n✅ Producto actualizado exitosamente!")
                else:
                    print("\n❌ Error al actualizar el producto")
            else:
                print("\nNo se realizaron cambios")
                
        except ValueError as e:
            print(f"❌ Error en los datos: {e}")
    
    def buscar_producto(self):
        """Busca productos por nombre"""
        self.limpiar_pantalla()
        print("🔍 BUSCAR PRODUCTOS")
        print("-" * 40)
        
        termino = input("Ingresa el nombre o parte del nombre a buscar: ").strip()
        
        if not termino:
            print("❌ Debes ingresar un término de búsqueda")
            return
        
        resultados = self.inventario.buscar_productos(termino)
        
        if not resultados:
            print(f"\n❌ No se encontraron productos con '{termino}'")
            return
        
        print(f"\n✅ Se encontraron {len(resultados)} productos:\n")
        
        for producto in resultados:
            print(f"ID: {producto.id} | {producto.nombre} - ${producto.precio:.2f} | Stock: {producto.cantidad}")
    
    def mostrar_por_categoria(self):
        """Muestra productos filtrados por categoría"""
        self.limpiar_pantalla()
        print("🏷️ PRODUCTOS POR CATEGORÍA")
        print("-" * 40)
        
        print(f"Categorías disponibles: {Inventario.CATEGORIAS_VALIDAS}")
        categoria = input("\nIngresa la categoría: ").strip().lower()
        
        if categoria not in Inventario.CATEGORIAS_VALIDAS:
            print(f"❌ Categoría no válida")
            return
        
        productos = self.inventario.obtener_por_categoria(categoria)
        
        if not productos:
            print(f"\n❌ No hay productos en la categoría '{categoria}'")
            return
        
        print(f"\n📦 Productos en '{categoria}':\n")
        
        for producto in productos:
            print(f"ID: {producto.id} | {producto.nombre} - ${producto.precio:.2f} | Stock: {producto.cantidad}")
    
    def mostrar_bajo_stock(self):
        """Muestra productos con bajo stock"""
        self.limpiar_pantalla()
        print("⚠️ PRODUCTOS CON BAJO STOCK")
        print("-" * 40)
        
        limite = 5
        productos = self.inventario.obtener_productos_con_bajo_stock(limite)
        
        if not productos:
            print(f"✅ No hay productos con stock menor o igual a {limite}")
            return
        
        print(f"📦 Productos con stock ≤ {limite}:\n")
        
        for producto in productos:
            print(f"ID: {producto.id} | {producto.nombre} | Stock: {producto.cantidad} | Precio: ${producto.precio:.2f}")
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas del inventario"""
        self.limpiar_pantalla()
        print("📊 ESTADÍSTICAS DEL INVENTARIO - PROYECTO_TIENDA_TECH")
        print("-" * 40)
        
        stats = self.inventario.obtener_estadisticas()
        
        print(f"📦 Total de productos: {stats['total_productos']}")
        print(f"💰 Valor total del inventario: ${stats['valor_total']:.2f}")
        
        print("\n🏷️ Productos por categoría:")
        for categoria, cantidad in stats['productos_por_categoria'].items():
            print(f"   • {categoria}: {cantidad} productos")
    
    def salir(self):
        """Sale del programa"""
        self.limpiar_pantalla()
        print("👋 ¡Gracias por usar el sistema de inventario de proyecto_tienda_tech!")
        print("Hasta luego!")
        sys.exit(0)


if __name__ == "__main__":
    # Crear y ejecutar el menú
    print("🚀 Iniciando Sistema de Gestión de proyecto_tienda_tech...")
    menu = MenuConsola()
    menu.ejecutar()