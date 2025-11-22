import sqlite3
import os

# Configuración de archivos
nombre_db = 'biblioteca.db'
archivo_sql = 'biblioteca.db.sql'

print(f"Iniciando proceso de creación para: {nombre_db}...")

# 1. Intentamos leer el script SQL
try:
    with open(archivo_sql, 'r', encoding='utf-8') as archivo:
        script_contenido = archivo.read()
    print(f"Script SQL '{archivo_sql}' cargado correctamente.")
except FileNotFoundError:
    print(f"Error crítico: No encuentro el archivo {archivo_sql} en esta carpeta.")
    exit()

# 2. Conexión y ejecución
try:
    # Conectamos (si no existe, la crea)
    conexion = sqlite3.connect(nombre_db)
    cursor = conexion.cursor()
    
    # Ejecutamos todo el script de una vez
    cursor.executescript(script_contenido)
    conexion.commit()
    
    print("\nBase de datos construida con éxito.")
    print("Se han generado las tablas, vistas y triggers.")
    
    # 3. Verificación rápida de datos
    print("\nResumen de registros insertados:")
    
    # Hago las consultas para ver si hay datos
    tablas = ['USUARIO', 'LIBRO', 'EJEMPLAR', 'PRESTAMO']
    
    for tabla in tablas:
        cantidad = cursor.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
        print(f" - Tabla {tabla}: {cantidad} registros")
    
    print("\n------------------------------------------------")
    print("Proceso finalizado. Para abrir el sistema usa:")
    print("python -m streamlit run streamlit_semana6.py")
    print("------------------------------------------------")
    
except Exception as error:
    print(f"Ocurrió un error inesperado al crear la BD: {error}")
finally:
    # Cerramos la conexión para liberar el archivo
    if 'conexion' in locals():
        conexion.close()