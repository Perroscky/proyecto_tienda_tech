# 🖥️ PROYECTO_TIENDA_TECH

Sistema de gestión de inventario para tienda de artículos tecnológicos desarrollado con Flask.

## 📋 DESCRIPCIÓN

Aplicación web completa que permite:
- Visualizar catálogo de productos tecnológicos
- Registrar usuarios con validación de edad (+18)
- Iniciar sesión (email y Facebook simulado)
- Agregar productos al carrito de compras
- Gestionar inventario desde consola
- Persistir datos en TXT, JSON, CSV y SQLite

## 🚀 FUNCIONALIDADES POR SEMANA

### **Semana 09 - Configuración básica y rutas**
- Estructura MVC del proyecto
- Rutas principales: `/`, `/producto/<nombre>`, `/categoria/<tipo>`
- Catálogo inicial con 6 productos tecnológicos
- Diseño CSS con gradientes y responsive

### **Semana 10 - Plantillas dinámicas**
- Herencia con `base.html` (header, navbar, footer)
- Templates: `index.html`, `producto.html`, `categoria.html`
- Contenido dinámico con Jinja2 (`{% for %}`, `{% if %}`)
- Páginas: contacto, about y 404 personalizadas

### **Semana 11 - POO y validación de formularios**
- Clases: `Producto`, `Inventario`, `Usuario`, `Carrito`
- Colecciones: diccionarios, conjuntos (IDs únicos), tuplas (categorías)
- Sistema de autenticación: registro (+18), login, logout
- Carrito de compras: agregar, actualizar, eliminar productos
- Estadísticas de inventario (total, valor, productos por categoría)

### **Semana 12 - Persistencia de datos**
- Archivos locales: `data/productos.txt`, `productos.json`, `productos.csv`
- Base de datos SQLite con tablas: productos, usuarios, carritos
- Rutas de gestión: `/datos` para ver y exportar datos entre formatos
- Funciones: guardar/cargar desde TXT, JSON, CSV y SQLite

### **Semana 13 - Integración con MySQL**
- Configuración de MySQL con WAMP
- Conexión Flask-MySQL usando PyMySQL
- Creación de tablas: usuarios, productos, carritos, ventas
- Operaciones CRUD completas desde la aplicación web
- Migración de datos desde SQLite a MySQL
- Rutas específicas: `/mysql`, `/mysql/insertar`, `/mysql/actualizar`, `/mysql/eliminar`

### **Semana 14 - Sistema de autenticación con Flask-Login** 
- Implementación de **Flask-Login** para manejo de sesiones
- Protección de rutas con `@login_required`
- Mejora en el manejo de sesiones de usuario
- Migración de base de datos MySQL a **Clever Cloud** (nube)
- Conexión exitosa entre Render y Clever Cloud
- Datos sincronizados: 8 productos y 5 usuarios en la nube
- Rutas protegidas: `/datos`, `/mysql`, `/carrito` y todas las de gestión

## **Semana 15 - CRUD completo, estructura por capas y reportes PDF
- Implementación de estructura por capas con carpetas services/, forms/ y reports/
- Desarrollo de CRUD completo para productos: Crear, Leer, Actualizar y Eliminar
- Integración de formularios WTForms con validación de datos
- Creación de servicios de negocio con ProductoService para manejar la lógica de productos
- Generación de reportes en PDF con la librería ReportLab
- Implementación de reporte general con listado completo de productos, totales y valor de inventario
- Desarrollo de reporte de bajo stock para productos con stock ≤ 5 unidades
- Creación de reportes por categoría (computadoras, periféricos, audio, celulares, tablets)
- Adición de filtros avanzados por categoría, stock mínimo y búsqueda por nombre
- Incorporación de indicadores visuales para productos con bajo stock
- Nuevas rutas protegidas: /productos, /productos/nuevo, /productos/editar/<id>, /productos/eliminar/<id>, /productos/reporte

## 🚀 CÓMO EJECUTAR

# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python app.py

# 5. Abrir navegador
http://127.0.0.1:5000

👨‍💻 AUTOR
Luis Samaniego - Proyecto Semanas 09-14