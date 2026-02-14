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

1. Clonar el repositorio:
```bash
git clone https://github.com/TU-USUARIO/proyecto_tienda_tech.git
cd proyecto_tienda_tech
```

2. Crear entorno virtual:
```bash
python -m venv venv
```

3. Activar entorno virtual:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

5. Ejecutar la aplicación:
```bash
python app.py
```

6. Abrir en navegador: `http://127.0.0.1:5000`

## 🌐 Rutas Disponibles

- `/` - Página principal con catálogo
- `/producto/<nombre>` - Detalles de producto específico
  - Ejemplos: `/producto/laptop`, `/producto/mouse`, `/producto/teclado`
- `/categoria/<tipo>` - Productos por categoría
- `/contacto` - Información de contacto

## 👨‍💻 Autor

Luis Samaniego - Proyecto Flask