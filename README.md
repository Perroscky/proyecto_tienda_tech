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

1. Crear entorno virtual:
   python -m venv venv

2. Activar entorno virtual:
   Windows: venv\Scripts\activate

3. Instalar dependencias:

   pip install -r requirements.txt

4. Ejecutar la aplicación:

   python app.py

5. Abrir en navegador: `http://127.0.0.1:5000`

## 🌐 Rutas Disponibles

- `/` - Página principal con catálogo
- `/producto/<nombre>` - Detalles de producto específico
  - Ejemplos: `/producto/laptop`, `/producto/mouse`, `/producto/teclado`
- `/categoria/<tipo>` - Productos por categoría
- `/contacto` - Información de contacto

## Elaborado

Alumno: Luis Samaniego - Proyecto Flask