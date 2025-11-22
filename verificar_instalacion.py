"""
Script de Verificación de Instalación
Sistema de Gestión de Biblioteca UFT

Este script verifica que todos los componentes necesarios
estén instalados y configurados correctamente.
"""

import os
import sys
import sqlite3

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"  ✅ {text}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"  ❌ {text}")

def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"  ⚠️  {text}")

def verificar_python():
    """Verifica la versión de Python"""
    print_header("🐍 Verificando Python")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 11:
        print_success(f"Python {version_str} instalado correctamente")
        return True
    elif version.major == 3 and version.minor >= 8:
        print_warning(f"Python {version_str} detectado (se recomienda 3.11+)")
        return True
    else:
        print_error(f"Python {version_str} es demasiado antiguo")
        print("  Se requiere Python 3.11 o superior")
        return False

def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    print_header("📁 Verificando Archivos del Proyecto")
    
    archivos_requeridos = {
        'biblioteca.db.sql': 'Script SQL de creación de base de datos',
        'crear_db.py': 'Script de creación de BD',
        'streamlit_semana6.py': 'Aplicación principal Streamlit',
        'requirements.txt': 'Lista de dependencias',
        'README.md': 'Documentación del proyecto'
    }
    
    todos_presentes = True
    
    for archivo, descripcion in archivos_requeridos.items():
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            print_success(f"{archivo:30} ({size:,} bytes) - {descripcion}")
        else:
            print_error(f"{archivo:30} - FALTA")
            todos_presentes = False
    
    return todos_presentes

def verificar_base_datos():
    """Verifica la base de datos y su contenido"""
    print_header("🗄️  Verificando Base de Datos")
    
    if not os.path.exists('biblioteca.db'):
        print_error("biblioteca.db NO EXISTE")
        print("  Ejecuta: python crear_db.py")
        return False
    
    try:
        conn = sqlite3.connect('biblioteca.db')
        cursor = conn.cursor()
        
        # Verificar tablas principales
        tablas_esperadas = {
            'USUARIO': 'Usuarios del sistema',
            'LIBRO': 'Catálogo de libros',
            'EJEMPLAR': 'Copias físicas',
            'PRESTAMO': 'Historial de préstamos',
            'RESERVA': 'Reservas de libros',
            'MULTA': 'Multas por atrasos',
            'DEPARTAMENTO': 'Departamentos',
            'PERSONAL': 'Personal de biblioteca'
        }
        
        print("\n  📊 Tablas y registros:")
        todas_ok = True
        
        for tabla, descripcion in tablas_esperadas.items():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                if count > 0:
                    print_success(f"{tabla:15} {count:3} registros - {descripcion}")
                else:
                    print_warning(f"{tabla:15} {count:3} registros (vacía)")
            except sqlite3.OperationalError:
                print_error(f"{tabla:15} NO EXISTE")
                todas_ok = False
        
        # Verificar vistas
        print("\n  👁️  Vistas:")
        vistas_esperadas = [
            'v_prestamos_activos',
            'v_multas_pendientes',
            'v_kpi_ranking_libros',
            'v_kpi_ranking_usuarios',
            'v_disponibilidad_ejemplares'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        vistas_existentes = [row[0] for row in cursor.fetchall()]
        
        for vista in vistas_esperadas:
            if vista in vistas_existentes:
                print_success(f"{vista}")
            else:
                print_error(f"{vista} NO EXISTE")
                todas_ok = False
        
        # Verificar triggers
        print("\n  ⚡ Triggers:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        triggers = [row[0] for row in cursor.fetchall()]
        
        if len(triggers) > 0:
            for trigger in triggers:
                print_success(f"{trigger}")
        else:
            print_warning("No hay triggers configurados")
        
        # Verificar índices
        print("\n  🔍 Índices:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indices = [row[0] for row in cursor.fetchall()]
        
        if len(indices) > 0:
            print_success(f"{len(indices)} índices creados")
        else:
            print_warning("No hay índices personalizados")
        
        conn.close()
        return todas_ok
        
    except Exception as e:
        print_error(f"Error al verificar base de datos: {e}")
        return False

def verificar_dependencias():
    """Verifica las dependencias de Python"""
    print_header("📦 Verificando Dependencias Python")
    
    dependencias = {
        'streamlit': '1.28.0',
        'pandas': '2.1.0',
        'plotly': '5.17.0'
    }
    
    todas_instaladas = True
    
    for modulo, version_esperada in dependencias.items():
        try:
            mod = __import__(modulo)
            version_instalada = getattr(mod, '__version__', 'desconocida')
            print_success(f"{modulo:15} {version_instalada:10} instalado")
        except ImportError:
            print_error(f"{modulo:15} NO INSTALADO")
            todas_instaladas = False
    
    if not todas_instaladas:
        print("\n  💡 Para instalar dependencias faltantes:")
        print("     pip install -r requirements.txt")
    
    return todas_instaladas

def verificar_codigo():
    """Verifica que el código principal se pueda importar"""
    print_header("🐍 Verificando Código Python")
    
    try:
        # Intentar importar el módulo principal
        import streamlit_semana6
        print_success("streamlit_semana6.py se puede importar sin errores")
        return True
    except ImportError as e:
        print_error(f"Error al importar streamlit_semana6.py:")
        print(f"       {str(e)}")
        return False
    except Exception as e:
        print_error(f"Error en el código:")
        print(f"       {str(e)}")
        return False

def test_conexion_bd():
    """Prueba realizar una consulta simple"""
    print_header("🧪 Probando Conexión y Consultas")
    
    if not os.path.exists('biblioteca.db'):
        print_error("No se puede probar: biblioteca.db no existe")
        return False
    
    try:
        conn = sqlite3.connect('biblioteca.db')
        cursor = conn.cursor()
        
        # Prueba 1: Contar usuarios
        cursor.execute("SELECT COUNT(*) FROM USUARIO")
        usuarios = cursor.fetchone()[0]
        print_success(f"Consulta SELECT: {usuarios} usuarios encontrados")
        
        # Prueba 2: Vista compleja
        cursor.execute("SELECT COUNT(*) FROM v_prestamos_activos")
        prestamos = cursor.fetchone()[0]
        print_success(f"Vista compleja: {prestamos} préstamos activos")
        
        # Prueba 3: Join
        cursor.execute("""
            SELECT COUNT(*) 
            FROM PRESTAMO p 
            JOIN USUARIO u ON p.rut_usuario = u.rut
        """)
        joins = cursor.fetchone()[0]
        print_success(f"Query con JOIN: {joins} registros")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Error en consultas: {e}")
        return False

def mostrar_resumen(resultados):
    """Muestra un resumen final de la verificación"""
    print_header("📊 RESUMEN DE VERIFICACIÓN")
    
    total = len(resultados)
    exitosos = sum(1 for r in resultados.values() if r)
    fallidos = total - exitosos
    
    print(f"\n  Total de verificaciones: {total}")
    print(f"  ✅ Exitosas: {exitosos}")
    print(f"  ❌ Fallidas: {fallidos}")
    
    porcentaje = (exitosos / total) * 100
    
    print("\n" + "=" * 60)
    
    if porcentaje == 100:
        print("  🎉 ¡PERFECTO! Todo está configurado correctamente")
        print("  ✅ El sistema está listo para usar")
        print("\n  Para iniciar la aplicación ejecuta:")
        print("     streamlit run streamlit_semana6.py")
        return True
    elif porcentaje >= 80:
        print("  ⚠️  CASI LISTO - Algunos componentes opcionales faltan")
        print("  ✅ El sistema debería funcionar")
        print("\n  Revisa los errores anteriores si tienes problemas")
        return True
    else:
        print("  ❌ NO LISTO - Faltan componentes críticos")
        print("  ⚠️  Revisa los errores anteriores y corrige antes de continuar")
        print("\n  Pasos recomendados:")
        if not resultados.get('dependencias', False):
            print("     1. pip install -r requirements.txt")
        if not resultados.get('base_datos', False):
            print("     2. python crear_db.py")
        return False

def main():
    """Función principal"""
    print("\n" + "🔍 " * 20)
    print("  VERIFICACIÓN DE INSTALACIÓN")
    print("  Sistema de Gestión de Biblioteca UFT")
    print("🔍 " * 20)
    
    resultados = {}
    
    # Ejecutar todas las verificaciones
    resultados['python'] = verificar_python()
    resultados['archivos'] = verificar_archivos()
    resultados['base_datos'] = verificar_base_datos()
    resultados['dependencias'] = verificar_dependencias()
    resultados['codigo'] = verificar_codigo()
    resultados['consultas'] = test_conexion_bd()
    
    # Mostrar resumen
    exito = mostrar_resumen(resultados)
    
    print("\n" + "=" * 60)
    print()
    
    # Código de salida
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()