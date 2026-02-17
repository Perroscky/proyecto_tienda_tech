# 🛒 Tienda Tech Online

Tienda online de productos tecnológicos desarrollada con Flask.

## 📋 Descripción

Sistema de e-commerce para venta de productos de tecnología con catálogo dinámico y rutas personalizadas.

## 🚀 Características

- Catálogo de productos con detalles
- Rutas dinámicas por producto
- Categorías de productos
- Información de contacto
- Diseño responsive

## 📦 Instalación

1. Crear entorno virtual: python -m venv venv

2. Activar entorno virtual: venv\Scripts\activate

3. Instalar dependencias: pip install -r requirements.txt

4. Ejecutar la aplicación: python app.py

5. Abrir en navegador: `http://127.0.0.1:5000`

## 🌐 Rutas Disponibles

- `/` - Página principal con catálogo
- `/producto/<nombre>` - Detalles de producto específico
  - Ejemplos: `/producto/laptop`, `/producto/mouse`, `/producto/teclado`
- `/categoria/<tipo>` - Productos por categoría
- `/contacto` - Información de contacto
- `/about` - Información sobre la tienda

## 📝 Actualizaciones del Proyecto

### Semana 9 (Proyecto Inicial)
- Creación de la aplicación Flask
- Implementación de rutas principales
- Base de datos simulada de productos
- Diseño CSS personalizado
- Catálogo de 6 productos tecnológicos

### Semana 10 (Plantillas con Herencia)
- Implementación de plantillas dinámicas con Jinja2
- Creación de plantilla base (base.html) con header, navbar y footer
- Separación de estructura y contenido usando {% block content %}
- Nuevas páginas creadas:
  - about.html - Página "Acerca de" con información de la empresa
  - producto.html - Vista detallada de productos
  - categoria.html - Filtrado por categoría
  - contacto.html - Información de contacto
  - Páginas de error 404 personalizadas
- Código más limpio y mantenible
- Todas las rutas ahora usan render_template()

## Elaborado

Alumno: Luis Samaniego - Proyecto Flask