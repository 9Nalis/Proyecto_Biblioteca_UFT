"""
Proyecto: Sistema de Biblioteca UFT
Asignatura: Base de Datos
Integrantes: [Tu equipo]
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Biblioteca UFT",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para que se vea ordenado (Títulos y tarjetas)
st.markdown("""
    <style>
    .titulo-principal {
        font-size: 2rem;
        color: #1e3a8a;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 2px solid #1e3a8a;
    }
    .tarjeta {
        background-color: #f8fafc;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2563eb;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. CONEXIÓN A BASE DE DATOS
# ---------------------------------------------------------

@st.cache_resource
def conectar_bd():
    """Abre la conexión con el archivo SQLite"""
    try:
        # check_same_thread=False es necesario para que no falle con Streamlit
        return sqlite3.connect('biblioteca.db', check_same_thread=False)
    except Exception as error:
        st.error(f"No se pudo conectar a la base de datos: {error}")
        return None

def ejecutar_sql(consulta, parametros=None, obtener_datos=True):
    """Función para ejecutar cualquier query SQL"""
    conexion = conectar_bd()
    if conexion is None:
        return None
    
    try:
        cursor = conexion.cursor()
        if parametros:
            cursor.execute(consulta, parametros)
        else:
            cursor.execute(consulta)
        
        if obtener_datos:
            return cursor.fetchall()
        else:
            conexion.commit()
            return True
    except Exception as e:
        st.error(f"Error en la consulta SQL: {e}")
        return None

def cargar_dataframe(consulta, columnas=None):
    """Trae datos de la BD y los convierte en una tabla de Pandas"""
    resultados = ejecutar_sql(consulta)
    if resultados:
        return pd.DataFrame(resultados, columns=columnas)
    return pd.DataFrame()

# ---------------------------------------------------------
# 2. FUNCIONES CRUD (Lógica del sistema)
# ---------------------------------------------------------

# --- USUARIOS ---
def insertar_usuario(rut, nombre, correo, direccion, telefono, tipo):
    sql = """INSERT INTO USUARIO (rut, nombre, correo, direccion, telefono, tipo_usuario)
             VALUES (?, ?, ?, ?, ?, ?)"""
    return ejecutar_sql(sql, (rut, nombre, correo, direccion, telefono, tipo), fetch=False)

def obtener_usuarios():
    sql = "SELECT rut, nombre, correo, direccion, telefono, tipo_usuario FROM USUARIO"
    cols = ['RUT', 'Nombre', 'Correo', 'Dirección', 'Teléfono', 'Tipo']
    return cargar_dataframe(sql, cols)

def modificar_usuario(rut, nombre, correo, direccion, telefono, tipo):
    sql = """UPDATE USUARIO SET nombre=?, correo=?, direccion=?, telefono=?, tipo_usuario=?
             WHERE rut=?"""
    return ejecutar_sql(sql, (nombre, correo, direccion, telefono, tipo, rut), fetch=False)

def borrar_usuario(rut):
    sql = "DELETE FROM USUARIO WHERE rut=?"
    return ejecutar_sql(sql, (rut,), fetch=False)

# --- LIBROS ---
def insertar_libro(isbn, titulo, editorial, anio, cat, autor, idioma, pags):
    sql = """INSERT INTO LIBRO (isbn, titulo, editorial, anio, categoria, autor, idioma, num_paginas)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    return ejecutar_sql(sql, (isbn, titulo, editorial, anio, cat, autor, idioma, pags), fetch=False)

def obtener_catalogo():
    sql = "SELECT isbn, titulo, autor, editorial, anio, categoria, idioma, num_paginas FROM LIBRO"
    cols = ['ISBN', 'Título', 'Autor', 'Editorial', 'Año', 'Categoría', 'Idioma', 'Páginas']
    return cargar_dataframe(sql, cols)

def modificar_libro(isbn, titulo, editorial, anio, cat, autor, idioma, pags):
    sql = """UPDATE LIBRO SET titulo=?, editorial=?, anio=?, categoria=?, autor=?, idioma=?, num_paginas=?
             WHERE isbn=?"""
    return ejecutar_sql(sql, (titulo, editorial, anio, cat, autor, idioma, pags, isbn), fetch=False)

def borrar_libro(isbn):
    sql = "DELETE FROM LIBRO WHERE isbn=?"
    return ejecutar_sql(sql, (isbn,), fetch=False)

# --- EJEMPLARES ---
def insertar_ejemplar(isbn, codigo, estado, ubicacion, condicion):
    sql = """INSERT INTO EJEMPLAR (isbn, codigo_barras, estado, ubicacion, condicion)
             VALUES (?, ?, ?, ?, ?)"""
    return ejecutar_sql(sql, (isbn, codigo, estado, ubicacion, condicion), fetch=False)

def obtener_inventario():
    sql = """SELECT e.id_ejemplar, e.isbn, l.titulo, e.codigo_barras, e.estado, e.ubicacion, e.condicion
             FROM EJEMPLAR e JOIN LIBRO l ON e.isbn = l.isbn"""
    cols = ['ID', 'ISBN', 'Título', 'Código', 'Estado', 'Ubicación', 'Condición']
    return cargar_dataframe(sql, cols)

def modificar_ejemplar(id_ej, estado, ubicacion, condicion):
    sql = "UPDATE EJEMPLAR SET estado=?, ubicacion=?, condicion=? WHERE id_ejemplar=?"
    return ejecutar_sql(sql, (estado, ubicacion, condicion, id_ej), fetch=False)

def borrar_ejemplar(id_ej):
    sql = "DELETE FROM EJEMPLAR WHERE id_ejemplar=?"
    return ejecutar_sql(sql, (id_ej,), fetch=False)

# --- PRÉSTAMOS ---
def registrar_prestamo(rut, id_ejemplar, vencimiento):
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    sql = """INSERT INTO PRESTAMO (rut_usuario, id_ejemplar, fecha_prestamo, fecha_vencimiento, estado)
             VALUES (?, ?, ?, ?, 'activo')"""
    return ejecutar_sql(sql, (rut, id_ejemplar, fecha_hoy, vencimiento), fetch=False)

def obtener_historial_prestamos():
    sql = """SELECT p.id_prestamo, u.nombre, l.titulo, e.codigo_barras, 
             p.fecha_prestamo, p.fecha_vencimiento, p.fecha_devolucion, p.estado
             FROM PRESTAMO p
             JOIN USUARIO u ON p.rut_usuario = u.rut
             JOIN EJEMPLAR e ON p.id_ejemplar = e.id_ejemplar
             JOIN LIBRO l ON e.isbn = l.isbn
             ORDER BY p.fecha_prestamo DESC"""
    cols = ['ID', 'Usuario', 'Libro', 'Código', 'Inicio', 'Vencimiento', 'Devolución', 'Estado']
    return cargar_dataframe(sql, cols)

def registrar_devolucion(id_prestamo):
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    sql = "UPDATE PRESTAMO SET fecha_devolucion=?, estado='devuelto' WHERE id_prestamo=?"
    return ejecutar_sql(sql, (fecha_hoy, id_prestamo), fetch=False)

def borrar_prestamo(id_prestamo):
    sql = "DELETE FROM PRESTAMO WHERE id_prestamo=?"
    return ejecutar_sql(sql, (id_prestamo,), fetch=False)

# --- ESTADÍSTICAS Y REPORTES ---
def cargar_stats_generales():
    datos = {}
    datos['usuarios'] = ejecutar_sql("SELECT COUNT(*) FROM USUARIO")[0][0]
    datos['libros'] = ejecutar_sql("SELECT COUNT(*) FROM LIBRO")[0][0]
    datos['prestamos'] = ejecutar_sql("SELECT COUNT(*) FROM PRESTAMO WHERE estado IN ('activo', 'vencido')")[0][0]
    
    # Manejo de nulos en la suma
    total_multas = ejecutar_sql("SELECT SUM(monto) FROM MULTA WHERE estado='pendiente'")[0][0]
    datos['deuda'] = total_multas if total_multas else 0
    
    return datos

def cargar_prestamos_activos_vista():
    return cargar_dataframe("SELECT * FROM v_prestamos_activos", 
        ['ID', 'Usuario', 'RUT', 'Correo', 'Tipo', 'Título', 'Autor', 'Código', 
         'Ubicación', 'Inicio', 'Vencimiento', 'Estado', 'Días Atraso'])

def cargar_multas_vista():
    return cargar_dataframe("SELECT * FROM v_multas_pendientes",
        ['ID', 'Usuario', 'RUT', 'Correo', 'Libro', 'Autor', 'Monto', 'Fecha', 'Días'])

def cargar_ranking_libros():
    return cargar_dataframe("SELECT * FROM v_kpi_ranking_libros LIMIT 10",
        ['Ranking', 'ISBN', 'Título', 'Autor', 'Categoría', 'Préstamos', 'Ejemplares', 'Rotación'])

def cargar_disponibilidad():
    return cargar_dataframe("SELECT * FROM v_disponibilidad_ejemplares",
        ['ISBN', 'Título', 'Autor', 'Categoría', 'Total', 'Disponibles', 'Prestados', 'Reparación', 'Bajas'])

# ---------------------------------------------------------
# 3. VISTAS DE LA INTERFAZ (Front-end)
# ---------------------------------------------------------

def vista_dashboard():
    st.markdown("<div class='titulo-principal'>Resumen General</div>", unsafe_allow_html=True)
    
    stats = cargar_stats_generales()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Usuarios", stats['usuarios'])
    c2.metric("Libros en Catálogo", stats['libros'])
    c3.metric("Préstamos Activos", stats['prestamos'])
    c4.metric("Multas por Cobrar", f"${stats['deuda']:,.0f}")
    
    st.divider()
    
    c_izq, c_der = st.columns(2)
    
    with c_izq:
        st.subheader("Lo más solicitado")
        df_top = cargar_ranking_libros().head(5)
        if not df_top.empty:
            grafico = px.bar(df_top, x='Título', y='Préstamos', color='Préstamos')
            st.plotly_chart(grafico, use_container_width=True)
        else:
            st.info("Aún no hay datos suficientes.")
            
    with c_der:
        st.subheader("Categorías")
        sql = "SELECT categoria, COUNT(*) as num FROM LIBRO GROUP BY categoria"
        df_cats = cargar_dataframe(sql, ['Categoría', 'Cantidad'])
        if not df_cats.empty:
            grafico = px.pie(df_cats, values='Cantidad', names='Categoría')
            st.plotly_chart(grafico, use_container_width=True)

    st.divider()
    st.subheader("Estado de Préstamos Actuales")
    df_activos = cargar_prestamos_activos_vista()
    
    if not df_activos.empty:
        # Función para colorear filas con atraso (Sin emojis)
        def color_atraso(row):
            if row['Días Atraso'] > 0:
                return ['background-color: #fee2e2; color: #7f1d1d; font-weight: bold'] * len(row)
            return [''] * len(row)
        
        st.dataframe(df_activos.style.apply(color_atraso, axis=1), hide_index=True, use_container_width=True)
    else:
        st.info("No hay préstamos activos.")

def vista_usuarios():
    st.markdown("<div class='titulo-principal'>Administración de Usuarios</div>", unsafe_allow_html=True)
    
    tab_ver, tab_crear, tab_editar = st.tabs(["Listado", "Nuevo Usuario", "Modificar"])
    
    with tab_ver:
        df = obtener_usuarios()
        busqueda = st.text_input("Buscar usuario (Nombre o RUT):")
        if busqueda:
            df = df[df['Nombre'].str.contains(busqueda, case=False) | df['RUT'].str.contains(busqueda)]
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Registros encontrados: {len(df)}")

    with tab_crear:
        st.write("#### Formulario de Registro")
        with st.form("frm_crear_usr"):
            c1, c2 = st.columns(2)
            rut = c1.text_input("RUT")
            nombre = c1.text_input("Nombre Completo")
            correo = c1.text_input("Email")
            direccion = c2.text_input("Dirección")
            fono = c2.text_input("Teléfono")
            tipo = c2.selectbox("Perfil", ['estudiante', 'docente', 'investigador', 'administrativo'])
            
            if st.form_submit_button("Guardar"):
                if rut and nombre and correo:
                    if insertar_usuario(rut, nombre, correo, direccion, fono, tipo):
                        st.success("Usuario guardado correctamente.")
                    else:
                        st.error("Error: El RUT ya existe o hay un problema de datos.")
                else:
                    st.warning("Faltan campos obligatorios (RUT, Nombre, Correo).")

    with tab_editar:
        st.write("#### Editar o Eliminar")
        df_users = obtener_usuarios()
        if not df_users.empty:
            sel_rut = st.selectbox("Seleccionar Usuario", df_users['RUT'].tolist())
            datos_usr = df_users[df_users['RUT'] == sel_rut].iloc[0]
            
            c1, c2 = st.columns([3, 1])
            with c1:
                with st.form("frm_edit_usr"):
                    n_nombre = st.text_input("Nombre", value=datos_usr['Nombre'])
                    n_correo = st.text_input("Correo", value=datos_usr['Correo'])
                    n_dir = st.text_input("Dirección", value=datos_usr['Dirección'] if pd.notna(datos_usr['Dirección']) else "")
                    n_fono = st.text_input("Teléfono", value=datos_usr['Teléfono'] if pd.notna(datos_usr['Teléfono']) else "")
                    n_tipo = st.selectbox("Perfil", ['estudiante', 'docente', 'investigador', 'administrativo'], 
                                        index=['estudiante', 'docente', 'investigador', 'administrativo'].index(datos_usr['Tipo']))
                    
                    if st.form_submit_button("Actualizar Datos"):
                        if modificar_usuario(sel_rut, n_nombre, n_correo, n_dir, n_fono, n_tipo):
                            st.success("Datos actualizados.")
                            st.rerun()
            
            with c2:
                st.write("Zona de Peligro")
                if st.button("Eliminar Usuario"):
                    if borrar_usuario(sel_rut):
                        st.success("Usuario eliminado.")
                        st.rerun()
                    else:
                        st.error("No se puede eliminar (tiene préstamos asociados).")

def vista_libros():
    st.markdown("<div class='titulo-principal'>Catálogo de Libros</div>", unsafe_allow_html=True)
    
    tab_cat, tab_new, tab_mod = st.tabs(["Catálogo", "Registrar Libro", "Modificar"])
    
    with tab_cat:
        df = obtener_catalogo()
        filtro = st.text_input("Buscar libro:")
        if filtro:
            df = df[df['Título'].str.contains(filtro, case=False) | df['ISBN'].str.contains(filtro)]
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_new:
        with st.form("frm_libro"):
            c1, c2 = st.columns(2)
            isbn = c1.text_input("ISBN")
            titulo = c1.text_input("Título")
            autor = c1.text_input("Autor")
            editorial = c1.text_input("Editorial")
            anio = c2.number_input("Año", 1500, 2100, 2024)
            cat = c2.selectbox("Categoría", ['Ficción', 'No Ficción', 'Referencia', 'Tesis'])
            idioma = c2.text_input("Idioma", "Español")
            pags = c2.number_input("Páginas", 1, 5000)
            
            if st.form_submit_button("Guardar Libro"):
                if insertar_libro(isbn, titulo, editorial, anio, cat, autor, idioma, pags):
                    st.success("Libro agregado al catálogo.")
                else:
                    st.error("Error: Verifique que el ISBN no esté duplicado.")

    with tab_mod:
        df_l = obtener_catalogo()
        if not df_l.empty:
            sel_isbn = st.selectbox("Seleccionar Libro", df_l['ISBN'].tolist())
            datos = df_l[df_l['ISBN'] == sel_isbn].iloc[0]
            
            with st.form("frm_edit_libro"):
                tit = st.text_input("Título", value=datos['Título'])
                aut = st.text_input("Autor", value=datos['Autor'])
                edi = st.text_input("Editorial", value=datos['Editorial'])
                ano = st.number_input("Año", value=int(datos['Año']))
                cate = st.selectbox("Categoría", ['Ficción', 'No Ficción', 'Referencia', 'Tesis'], 
                                  index=['Ficción', 'No Ficción', 'Referencia', 'Tesis'].index(datos['Categoría']))
                idi = st.text_input("Idioma", value=datos['Idioma'])
                pg = st.number_input("Páginas", value=int(datos['Páginas']))
                
                if st.form_submit_button("Actualizar"):
                    if modificar_libro(sel_isbn, tit, edi, ano, cate, aut, idi, pg):
                        st.success("Libro modificado.")
                        st.rerun()
            
            if st.button("Eliminar este Libro"):
                if borrar_libro(sel_isbn):
                    st.success("Libro eliminado.")
                    st.rerun()
                else:
                    st.error("No se puede eliminar (tiene copias físicas registradas).")

def vista_ejemplares():
    st.markdown("<div class='titulo-principal'>Inventario Físico</div>", unsafe_allow_html=True)
    
    tab_inv, tab_add, tab_edit = st.tabs(["Inventario", "Agregar Copia", "Modificar Copia"])
    
    with tab_inv:
        df = obtener_inventario()
        
        # Filtros
        c1, c2 = st.columns(2)
        estado_f = c1.selectbox("Filtrar por Estado", ['Todos', 'disponible', 'prestado', 'en_reparacion', 'perdido'])
        texto_f = c2.text_input("Buscar por código o título")
        
        if estado_f != 'Todos':
            df = df[df['Estado'] == estado_f]
        if texto_f:
            df = df[df['Título'].str.contains(texto_f, case=False) | df['Código'].str.contains(texto_f)]
            
        # Colores simples para el estado
        def color_inventario(row):
            e = row['Estado']
            if e == 'disponible': return ['background-color: #d1fae5; color: #064e3b'] * len(row)
            if e == 'prestado': return ['background-color: #dbeafe; color: #1e3a8a'] * len(row)
            if e == 'perdido': return ['background-color: #fee2e2; color: #7f1d1d'] * len(row)
            return [''] * len(row)
            
        st.dataframe(df.style.apply(color_inventario, axis=1), use_container_width=True, hide_index=True)

    with tab_add:
        libros = obtener_catalogo()
        if not libros.empty:
            with st.form("frm_ejemplar"):
                c1, c2 = st.columns(2)
                isbn_sel = c1.selectbox("Libro", libros['ISBN'].tolist())
                codigo = c1.text_input("Código de Barras (Único)")
                estado = c1.selectbox("Estado Inicial", ['disponible', 'en_reparacion'])
                ubic = c2.text_input("Ubicación (Estantería)")
                cond = c2.selectbox("Condición", ['excelente', 'bueno', 'regular', 'malo'])
                
                if st.form_submit_button("Registrar Copia"):
                    if codigo:
                        if insertar_ejemplar(isbn_sel, codigo, estado, ubic, cond):
                            st.success("Copia registrada.")
                        else:
                            st.error("Error: Código de barras duplicado.")
                    else:
                        st.warning("El código de barras es obligatorio.")
        else:
            st.warning("Primero debes registrar libros en el catálogo.")

    with tab_edit:
        df_e = obtener_inventario()
        if not df_e.empty:
            id_sel = st.selectbox("Seleccionar Copia", df_e['ID'].tolist(), format_func=lambda x: f"ID: {x}")
            datos = df_e[df_e['ID'] == id_sel].iloc[0]
            
            with st.form("frm_edit_ej"):
                st.write(f"Editando: {datos['Título']} ({datos['Código']})")
                n_est = st.selectbox("Estado", ['disponible', 'prestado', 'en_reparacion', 'perdido', 'baja'], 
                                   index=['disponible', 'prestado', 'en_reparacion', 'perdido', 'baja'].index(datos['Estado']))
                n_ubi = st.text_input("Ubicación", value=datos['Ubicación'] if pd.notna(datos['Ubicación']) else "")
                n_con = st.selectbox("Condición", ['excelente', 'bueno', 'regular', 'malo'],
                                   index=['excelente', 'bueno', 'regular', 'malo'].index(datos['Condición']))
                
                if st.form_submit_button("Guardar Cambios"):
                    if modificar_ejemplar(id_sel, n_est, n_ubi, n_con):
                        st.success("Inventario actualizado.")
                        st.rerun()
            
            if st.button("Eliminar Copia"):
                if borrar_ejemplar(id_sel):
                    st.success("Copia eliminada.")
                    st.rerun()
                else:
                    st.error("No se puede eliminar (está prestado o tiene historial).")

def vista_prestamos():
    st.markdown("<div class='titulo-principal'>Control de Préstamos</div>", unsafe_allow_html=True)
    
    tab_hist, tab_prestar, tab_devolver = st.tabs(["Historial", "Realizar Préstamo", "Devoluciones"])
    
    with tab_hist:
        df = obtener_historial_prestamos()
        
        f_estado = st.selectbox("Filtrar Estado", ['Todos', 'activo', 'vencido', 'devuelto'])
        if f_estado != 'Todos':
            df = df[df['Estado'] == f_estado]
            
        # Estilo visual
        def estilo_prestamo(row):
            e = row['Estado']
            if e == 'vencido': return ['background-color: #fee2e2; color: #7f1d1d; font-weight: bold'] * len(row)
            if e == 'activo': return ['background-color: #dbeafe; color: #1e3a8a'] * len(row)
            return [''] * len(row)
            
        st.dataframe(df.style.apply(estilo_prestamo, axis=1), use_container_width=True, hide_index=True)

    with tab_prestar:
        usuarios = obtener_usuarios()
        # Buscar solo copias disponibles
        copias_disp = cargar_dataframe("SELECT e.id_ejemplar, e.codigo_barras, l.titulo FROM EJEMPLAR e JOIN LIBRO l ON e.isbn = l.isbn WHERE e.estado='disponible'", ['ID', 'Código', 'Título'])
        
        if not usuarios.empty and not copias_disp.empty:
            with st.form("frm_prestamo"):
                c1, c2 = st.columns(2)
                usr = c1.selectbox("Usuario", usuarios['RUT'].tolist())
                copia = c2.selectbox("Libro Disponible", copias_disp['ID'].tolist(), 
                                   format_func=lambda x: f"{copias_disp[copias_disp['ID']==x]['Título'].values[0]}")
                
                dias = st.number_input("Días de préstamo", 1, 30, 7)
                
                if st.form_submit_button("Confirmar Préstamo"):
                    fecha_fin = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')
                    if registrar_prestamo(usr, copia, fecha_fin):
                        st.success("Préstamo registrado.")
                        st.rerun()
                    else:
                        st.error("Error al registrar el préstamo.")
        else:
            st.info("No se puede prestar: Faltan usuarios o no hay libros disponibles.")

    with tab_devolver:
        # Buscar préstamos activos
        activos = cargar_dataframe("SELECT p.id_prestamo, u.nombre, l.titulo FROM PRESTAMO p JOIN USUARIO u ON p.rut_usuario=u.rut JOIN EJEMPLAR e ON p.id_ejemplar=e.id_ejemplar JOIN LIBRO l ON e.isbn=l.isbn WHERE p.estado IN ('activo','vencido')", ['ID', 'Usuario', 'Libro'])
        
        if not activos.empty:
            prestamo_sel = st.selectbox("Seleccione el préstamo a devolver", activos['ID'].tolist(),
                                      format_func=lambda x: f"{activos[activos['ID']==x]['Usuario'].values[0]} - {activos[activos['ID']==x]['Libro'].values[0]}")
            
            if st.button("Registrar Devolución"):
                registrar_devolucion(prestamo_sel)
                st.success("Libro devuelto. El inventario ha sido actualizado.")
                st.rerun()
        else:
            st.info("No hay devoluciones pendientes.")

def vista_reportes():
    st.markdown("<div class='titulo-principal'>Reportes</div>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["Ranking Usuarios", "Disponibilidad", "Multas"])
    
    with t1:
        st.subheader("Usuarios con más actividad")
        sql = """SELECT u.nombre, u.tipo_usuario, COUNT(p.id_prestamo) as total
                 FROM USUARIO u JOIN PRESTAMO p ON u.rut = p.rut_usuario
                 GROUP BY u.rut ORDER BY total DESC LIMIT 10"""
        df = cargar_dataframe(sql, ['Nombre', 'Perfil', 'Préstamos'])
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            graf = px.bar(df, x='Nombre', y='Préstamos', color='Perfil')
            st.plotly_chart(graf, use_container_width=True)
            
    with t2:
        st.subheader("Disponibilidad de la Colección")
        df_disp = cargar_disponibilidad()
        st.dataframe(df_disp, use_container_width=True)
        
    with t3:
        st.subheader("Deudas Pendientes")
        df_multas = cargar_multas_vista()
        if not df_multas.empty:
            st.dataframe(df_multas, use_container_width=True)
        else:
            st.info("No hay multas pendientes.")

# ---------------------------------------------------------
# 4. MENÚ PRINCIPAL (Sidebar)
# ---------------------------------------------------------

def app_principal():
    with st.sidebar:
        st.title("📚 Biblioteca")
        opcion = st.radio("Menú", ["Inicio", "Usuarios", "Libros", "Inventario", "Préstamos", "Reportes"])
        
        st.divider()
        # KPI Rápido en el sidebar
        stats = cargar_stats_generales()
        st.caption(f"Usuarios: {stats['usuarios']}")
        st.caption(f"Libros: {stats['libros']}")
        st.caption("v1.0 - Semestre II")

    if opcion == "Inicio":
        vista_dashboard()
    elif opcion == "Usuarios":
        vista_usuarios()
    elif opcion == "Libros":
        vista_libros()
    elif opcion == "Inventario":
        vista_ejemplares()
    elif opcion == "Préstamos":
        vista_prestamos()
    elif opcion == "Reportes":
        vista_reportes()

# Punto de entrada
if __name__ == "__main__":
    conn_check = conectar_bd()
    if conn_check:
        app_principal()
    else:
        st.warning("Por favor ejecuta 'python crear_db.py' primero.")