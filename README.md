# Proyecto Base de Datos: Sistema de Biblioteca UFT
Curso: Bases de Datos - 2025-II

Integrantes:
- Geovanny Moreno Viera
- Sahiam Pérez Hernandez
- Nicolás Piñones Aranguiz

---

## Descripción
Este proyecto implementa un sistema de gestión para una biblioteca universitaria usando Python y SQLite. Permite manejar el flujo completo de préstamos, devoluciones, multas y administración de inventario (libros y ejemplares).

## Requisitos Previos

1. Python
   Es necesario tener instalado Python en versión 3.10, 3.11 o 3.12.
   Nota: Evitar la versión 3.14 (Alpha) porque tiene problemas de compatibilidad con las librerías gráficas usadas.

2. Librerías
   El proyecto utiliza streamlit, pandas y plotly.

---

## Instalación y Ejecución

Para que el proyecto funcione correctamente en Windows, seguir estos pasos en orden desde la terminal (VS Code o CMD):

1. Instalación de dependencias
   Ejecutar este comando para instalar las librerías necesarias. Usamos "python -m" para evitar problemas de rutas en Windows.

   python -m pip install -r requirements.txt

2. Inicialización de la Base de Datos
   Este script crea la base de datos desde cero, carga el esquema y los datos de prueba iniciales. Es necesario ejecutarlo al menos una vez antes de abrir el programa.

   python crear_db.py

3. Ejecución del Programa
   Para abrir la interfaz web, usar el siguiente comando.
   Importante: No usar el botón de "Play" de VS Code, ya que Streamlit requiere ejecutarse como módulo.

   python -m streamlit run streamlit_semana6.py

   Esto abrirá automáticamente el navegador en http://localhost:8501

---

## Estructura de Archivos

- biblioteca.db.sql: Código SQL con la creación de tablas, triggers y vistas.
- crear_db.py: Script de Python que reinicia la base de datos (útil para limpiar datos).
- streamlit_semana6.py: Código principal de la aplicación.
- Uso.txt: Manual de usuario para operar el sistema.