-- ============================================
-- Sistema de Gestión de Biblioteca Universitaria
-- Universidad Finis Terrae
-- Versión Corregida - UTF-8
-- ============================================

-- Configuración inicial
PRAGMA foreign_keys = OFF;
PRAGMA encoding = "UTF-8";

-- Limpieza de base de datos (eliminar tablas si existen)
DROP TABLE IF EXISTS MULTA;
DROP TABLE IF EXISTS RESERVA;
DROP TABLE IF EXISTS PRESTAMO;
DROP TABLE IF EXISTS EJEMPLAR;
DROP TABLE IF EXISTS LIBRO;
DROP TABLE IF EXISTS USUARIO;
DROP TABLE IF EXISTS PERSONAL;
DROP TABLE IF EXISTS DEPARTAMENTO;

DROP VIEW IF EXISTS v_prestamos_activos;
DROP VIEW IF EXISTS v_multas_pendientes;
DROP VIEW IF EXISTS v_kpi_ranking_libros;
DROP VIEW IF EXISTS v_kpi_ranking_usuarios;

DROP INDEX IF EXISTS idx_libro_titulo;
DROP INDEX IF EXISTS idx_libro_autor;
DROP INDEX IF EXISTS idx_ejemplar_isbn;
DROP INDEX IF EXISTS idx_prestamo_usuario;
DROP INDEX IF EXISTS idx_prestamo_ejemplar;
DROP INDEX IF EXISTS idx_reserva_usuario;
DROP INDEX IF EXISTS idx_reserva_isbn;
DROP INDEX IF EXISTS idx_prestamo_ejemplar_activo_o_vencido;
DROP INDEX IF EXISTS idx_reserva_pendiente_unica;

DROP TRIGGER IF EXISTS trg_prestamo_devolucion;
DROP TRIGGER IF EXISTS trg_prestamo_nuevo;
DROP TRIGGER IF EXISTS trg_marcar_prestamos_vencidos;

-- Activar foreign keys
PRAGMA foreign_keys = ON;

-- ============================================
-- 1. DDL (Creación de Tablas)
-- ============================================

CREATE TABLE DEPARTAMENTO (
    id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    ubicacion TEXT
);

CREATE TABLE PERSONAL (
    id_personal INTEGER PRIMARY KEY AUTOINCREMENT,
    id_departamento INTEGER NOT NULL,
    cargo TEXT,
    fecha_contratacion TEXT NOT NULL,
    FOREIGN KEY (id_departamento) REFERENCES DEPARTAMENTO(id_departamento)
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

CREATE TABLE USUARIO (
    rut TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    direccion TEXT,
    telefono TEXT,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('estudiante', 'docente', 'investigador', 'administrativo')),
    CHECK (correo LIKE '%@%')
);

CREATE TABLE LIBRO (
    isbn TEXT PRIMARY KEY,
    titulo TEXT NOT NULL,
    editorial TEXT,
    anio INTEGER CHECK (anio >= 1500 AND anio <= 2100),
    categoria TEXT CHECK (categoria IN ('Ficción', 'No Ficción', 'Referencia', 'Periódico', 'Revista', 'Tesis')),
    autor TEXT,
    idioma TEXT DEFAULT 'español',
    num_paginas INTEGER CHECK (num_paginas > 0),
    CHECK (LENGTH(REPLACE(isbn, '-', '')) IN (10, 13))
);

CREATE TABLE EJEMPLAR (
    id_ejemplar INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT NOT NULL,
    codigo_barras TEXT NOT NULL UNIQUE,
    estado TEXT NOT NULL CHECK (estado IN ('disponible', 'prestado', 'en_reparacion', 'perdido', 'baja')),
    ubicacion TEXT,
    condicion TEXT NOT NULL DEFAULT 'bueno' CHECK (condicion IN ('excelente', 'bueno', 'regular', 'malo')),
    FOREIGN KEY (isbn) REFERENCES LIBRO(isbn) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

CREATE TABLE PRESTAMO (
    id_prestamo INTEGER PRIMARY KEY AUTOINCREMENT,
    rut_usuario TEXT NOT NULL,
    id_ejemplar INTEGER NOT NULL,
    fecha_prestamo TEXT NOT NULL DEFAULT (DATE('now')),
    fecha_vencimiento TEXT NOT NULL,
    fecha_devolucion TEXT,
    estado TEXT NOT NULL CHECK (estado IN ('activo', 'devuelto', 'vencido')) DEFAULT 'activo',
    FOREIGN KEY (rut_usuario) REFERENCES USUARIO(rut) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    FOREIGN KEY (id_ejemplar) REFERENCES EJEMPLAR(id_ejemplar) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

CREATE TABLE RESERVA (
    id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
    rut_usuario TEXT NOT NULL,
    isbn TEXT NOT NULL,
    fecha_reserva TEXT NOT NULL DEFAULT (DATE('now')),
    fecha_expiracion TEXT,
    estado TEXT NOT NULL CHECK (estado IN ('pendiente', 'notificado', 'cumplido', 'expirado', 'cancelado')) DEFAULT 'pendiente',
    FOREIGN KEY (rut_usuario) REFERENCES USUARIO(rut) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (isbn) REFERENCES LIBRO(isbn) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

CREATE TABLE MULTA (
    id_multa INTEGER PRIMARY KEY AUTOINCREMENT,
    id_prestamo INTEGER NOT NULL UNIQUE,
    monto REAL NOT NULL CHECK (monto >= 0),
    fecha_generacion TEXT NOT NULL DEFAULT (DATE('now')),
    fecha_pago TEXT,
    estado TEXT NOT NULL CHECK (estado IN ('pendiente', 'pagado', 'condonado')) DEFAULT 'pendiente',
    FOREIGN KEY (id_prestamo) REFERENCES PRESTAMO(id_prestamo) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- ============================================
-- 2. TRIGGERS (Reglas de Negocio Automáticas)
-- ============================================

-- Trigger para actualizar estado a 'disponible' al devolver
CREATE TRIGGER trg_prestamo_devolucion
AFTER UPDATE ON PRESTAMO
FOR EACH ROW
WHEN (NEW.estado = 'devuelto' AND OLD.estado != 'devuelto')
BEGIN
    UPDATE EJEMPLAR
    SET estado = 'disponible'
    WHERE id_ejemplar = NEW.id_ejemplar;
END;

-- Trigger para actualizar estado a 'prestado' al crear préstamo
CREATE TRIGGER trg_prestamo_nuevo
AFTER INSERT ON PRESTAMO
FOR EACH ROW
WHEN NEW.estado IN ('activo', 'vencido')
BEGIN
    UPDATE EJEMPLAR
    SET estado = 'prestado'
    WHERE id_ejemplar = NEW.id_ejemplar;
END;

-- Trigger para marcar préstamos como vencidos automáticamente
CREATE TRIGGER trg_marcar_prestamos_vencidos
AFTER UPDATE ON PRESTAMO
FOR EACH ROW
WHEN (NEW.estado = 'activo' AND DATE('now') > DATE(NEW.fecha_vencimiento))
BEGIN
    UPDATE PRESTAMO 
    SET estado = 'vencido' 
    WHERE id_prestamo = NEW.id_prestamo;
END;

-- ============================================
-- 3. ÍNDICES (Optimizaciones)
-- ============================================

CREATE INDEX idx_libro_titulo ON LIBRO (titulo);
CREATE INDEX idx_libro_autor ON LIBRO (autor);
CREATE INDEX idx_libro_categoria ON LIBRO (categoria);
CREATE INDEX idx_ejemplar_isbn ON EJEMPLAR (isbn);
CREATE INDEX idx_ejemplar_estado ON EJEMPLAR (estado);
CREATE INDEX idx_prestamo_usuario ON PRESTAMO (rut_usuario);
CREATE INDEX idx_prestamo_ejemplar ON PRESTAMO (id_ejemplar);
CREATE INDEX idx_prestamo_estado ON PRESTAMO (estado);
CREATE INDEX idx_reserva_usuario ON RESERVA (rut_usuario);
CREATE INDEX idx_reserva_isbn ON RESERVA (isbn);

-- Índice único condicional: solo un préstamo activo/vencido por ejemplar
CREATE UNIQUE INDEX idx_prestamo_ejemplar_activo_o_vencido
ON PRESTAMO(id_ejemplar)
WHERE estado IN ('activo', 'vencido');

-- Índice único condicional: evitar reservas pendientes duplicadas
CREATE UNIQUE INDEX idx_reserva_pendiente_unica
ON RESERVA (rut_usuario, isbn)
WHERE estado = 'pendiente';

-- ============================================
-- 4. VISTAS (Reportes y KPIs)
-- ============================================

CREATE VIEW v_prestamos_activos AS
SELECT
    p.id_prestamo,
    u.nombre AS nombre_usuario,
    u.rut,
    u.correo,
    u.tipo_usuario,
    l.titulo AS titulo_libro,
    l.autor,
    e.codigo_barras,
    e.ubicacion,
    p.fecha_prestamo,
    p.fecha_vencimiento,
    p.estado,
    CASE
        WHEN p.estado = 'vencido' OR DATE('now') > DATE(p.fecha_vencimiento) 
        THEN CAST(JULIANDAY('now') - JULIANDAY(p.fecha_vencimiento) AS INTEGER)
        ELSE 0
    END AS dias_de_atraso
FROM PRESTAMO p
JOIN USUARIO u ON p.rut_usuario = u.rut
JOIN EJEMPLAR e ON p.id_ejemplar = e.id_ejemplar
JOIN LIBRO l ON e.isbn = l.isbn
WHERE p.estado IN ('activo', 'vencido');

CREATE VIEW v_multas_pendientes AS
SELECT
    m.id_multa,
    u.nombre AS nombre_usuario,
    u.rut,
    u.correo,
    l.titulo AS titulo_libro_asociado,
    l.autor,
    m.monto,
    m.fecha_generacion,
    CAST(JULIANDAY('now') - JULIANDAY(m.fecha_generacion) AS INTEGER) AS dias_pendientes
FROM MULTA m
JOIN PRESTAMO p ON m.id_prestamo = p.id_prestamo
JOIN USUARIO u ON p.rut_usuario = u.rut
JOIN EJEMPLAR e ON p.id_ejemplar = e.id_ejemplar
JOIN LIBRO l ON e.isbn = l.isbn
WHERE m.estado = 'pendiente';

CREATE VIEW v_kpi_ranking_libros AS
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(p.id_prestamo) DESC) AS ranking,
    l.isbn,
    l.titulo,
    l.autor,
    l.categoria,
    COUNT(p.id_prestamo) AS total_prestamos,
    COUNT(DISTINCT e.id_ejemplar) AS num_ejemplares,
    ROUND(CAST(COUNT(p.id_prestamo) AS REAL) / COUNT(DISTINCT e.id_ejemplar), 2) AS rotacion_por_ejemplar
FROM LIBRO l
LEFT JOIN EJEMPLAR e ON l.isbn = e.isbn
LEFT JOIN PRESTAMO p ON e.id_ejemplar = p.id_ejemplar
GROUP BY l.isbn, l.titulo, l.autor, l.categoria
ORDER BY total_prestamos DESC;

CREATE VIEW v_kpi_ranking_usuarios AS
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(p.id_prestamo) DESC) AS ranking,
    u.rut,
    u.nombre,
    u.tipo_usuario,
    COUNT(p.id_prestamo) AS total_prestamos,
    COUNT(CASE WHEN p.estado = 'devuelto' THEN 1 END) AS prestamos_devueltos,
    COUNT(CASE WHEN p.estado = 'activo' THEN 1 END) AS prestamos_activos,
    COUNT(CASE WHEN p.estado = 'vencido' THEN 1 END) AS prestamos_vencidos,
    COALESCE(SUM(m.monto), 0) AS total_multas_pendientes
FROM USUARIO u
LEFT JOIN PRESTAMO p ON u.rut = p.rut_usuario
LEFT JOIN MULTA m ON p.id_prestamo = m.id_prestamo AND m.estado = 'pendiente'
GROUP BY u.rut, u.nombre, u.tipo_usuario
ORDER BY total_prestamos DESC;

CREATE VIEW v_disponibilidad_ejemplares AS
SELECT
    l.isbn,
    l.titulo,
    l.autor,
    l.categoria,
    COUNT(e.id_ejemplar) AS total_ejemplares,
    COUNT(CASE WHEN e.estado = 'disponible' THEN 1 END) AS ejemplares_disponibles,
    COUNT(CASE WHEN e.estado = 'prestado' THEN 1 END) AS ejemplares_prestados,
    COUNT(CASE WHEN e.estado = 'en_reparacion' THEN 1 END) AS ejemplares_reparacion,
    COUNT(CASE WHEN e.estado IN ('perdido', 'baja') THEN 1 END) AS ejemplares_fuera_servicio
FROM LIBRO l
LEFT JOIN EJEMPLAR e ON l.isbn = e.isbn
GROUP BY l.isbn, l.titulo, l.autor, l.categoria;

-- ============================================
-- 5. DML (Carga de Datos de Prueba)
-- ============================================

INSERT INTO DEPARTAMENTO (nombre, ubicacion) VALUES
('Circulación', 'Piso 1, Mesón Principal'),
('Referencia', 'Piso 2, Hemeroteca'),
('Administración', 'Piso 3, Oficina 301');

INSERT INTO PERSONAL (id_departamento, cargo, fecha_contratacion) VALUES
(3, 'Jefe de Biblioteca', '2020-03-01'),
(1, 'Bibliotecario Circulación', '2022-05-15'),
(2, 'Bibliotecario Referencia', '2021-11-01');

INSERT INTO USUARIO (rut, nombre, correo, direccion, telefono, tipo_usuario) VALUES
('11111111-1', 'Geovanny Moreno Viera', 'g.moreno@mail.com', 'Calle Ficticia 123', '911111111', 'estudiante'),
('22222222-2', 'Sahiam Perez Hernandez', 's.perez@mail.com', 'Avenida Siempre Viva 456', '922222222', 'estudiante'),
('33333333-3', 'Nicolas Pinones Aranguiz', 'n.pinones@mail.com', 'Pasaje Los Robles 789', '933333333', 'estudiante'),
('44444444-4', 'Fernando San Martin', 'f.sanmartin@profesor.uft.cl', 'Oficina 301', '944444444', 'docente'),
('55555555-5', 'Ana Gonzalez', 'a.gonzalez@mail.com', 'El Peral 20', '955555555', 'investigador');

INSERT INTO LIBRO (isbn, titulo, editorial, anio, categoria, autor, idioma, num_paginas) VALUES
('9780321765723', 'Fundamentals of Database Systems', 'Pearson', 2015, 'Referencia', 'Elmasri & Navathe', 'ingles', 1200),
('9780132354784', 'Clean Code', 'Prentice Hall', 2008, 'Referencia', 'Robert C. Martin', 'ingles', 464),
('9788437604947', 'Cien años de soledad', 'Sudamericana', 1967, 'Ficción', 'Gabriel Garcia Marquez', 'español', 417),
('9788497592208', 'La casa de los espíritus', 'Plaza & Janes', 1982, 'Ficción', 'Isabel Allende', 'español', 456),
('0321125215', 'Domain-Driven Design', 'Addison-Wesley', 2003, 'Referencia', 'Eric Evans', 'ingles', 560),
('9789563250427', 'Historia de Chile 1808-2010', 'Debate', 2012, 'No Ficción', 'Gabriel Salazar', 'español', 840),
('9788420674258', 'Don Quijote de la Mancha', 'Cátedra', 2005, 'Ficción', 'Miguel de Cervantes', 'español', 1248),
('9780596007126', 'SQL Cookbook', 'O''Reilly Media', 2005, 'Referencia', 'Anthony Molinaro', 'ingles', 628),
('9788498387088', 'Sapiens: De animales a dioses', 'Debate', 2015, 'No Ficción', 'Yuval Noah Harari', 'español', 496),
('9788478884452', 'Harry Potter y la piedra filosofal', 'Salamandra', 1999, 'Ficción', 'J.K. Rowling', 'español', 256);

INSERT INTO EJEMPLAR (isbn, codigo_barras, estado, ubicacion, condicion) VALUES
('9780321765723', 'UFT000001', 'disponible', 'Estantería 2A', 'excelente'),
('9780321765723', 'UFT000002', 'disponible', 'Estantería 2A', 'bueno'),
('9780321765723', 'UFT000003', 'disponible', 'Estantería 2A', 'bueno'),
('9780132354784', 'UFT000004', 'disponible', 'Estantería 2A', 'bueno'),
('9780132354784', 'UFT000005', 'disponible', 'Estantería 2A', 'regular'),
('9788437604947', 'UFT000006', 'disponible', 'Estantería 10B', 'excelente'),
('9788437604947', 'UFT000007', 'en_reparacion', 'Taller', 'malo'),
('9788497592208', 'UFT000008', 'disponible', 'Estantería 10B', 'bueno'),
('0321125215', 'UFT000009', 'disponible', 'Estantería 2A', 'regular'),
('0321125215', 'UFT000010', 'disponible', 'Estantería 2A', 'bueno'),
('9789563250427', 'UFT000011', 'disponible', 'Estantería 5C', 'bueno'),
('9789563250427', 'UFT000012', 'disponible', 'Estantería 5C', 'excelente'),
('9788420674258', 'UFT000013', 'disponible', 'Estantería 10A', 'regular'),
('9788420674258', 'UFT000014', 'disponible', 'Estantería 10A', 'bueno'),
('9780596007126', 'UFT000015', 'disponible', 'Estantería 2A', 'bueno'),
('9780596007126', 'UFT000016', 'disponible', 'Estantería 2A', 'excelente'),
('9788498387088', 'UFT000017', 'disponible', 'Estantería 5C', 'bueno'),
('9788498387088', 'UFT000018', 'disponible', 'Estantería 5C', 'bueno'),
('9788478884452', 'UFT000019', 'disponible', 'Estantería 11F', 'regular'),
('9788478884452', 'UFT000020', 'disponible', 'Estantería 11F', 'bueno');

-- Préstamos activos (los triggers actualizarán automáticamente el estado de los ejemplares)
INSERT INTO PRESTAMO (rut_usuario, id_ejemplar, fecha_prestamo, fecha_vencimiento, estado) VALUES
('11111111-1', 2, '2025-10-15', '2025-10-22', 'activo'),
('44444444-4', 8, '2025-10-10', '2025-10-24', 'activo'),
('55555555-5', 11, '2025-09-25', '2025-10-25', 'activo');

-- Préstamo vencido
INSERT INTO PRESTAMO (rut_usuario, id_ejemplar, fecha_prestamo, fecha_vencimiento, estado) VALUES
('22222222-2', 5, '2025-10-01', '2025-10-08', 'vencido');

-- Préstamos ya devueltos
INSERT INTO PRESTAMO (rut_usuario, id_ejemplar, fecha_prestamo, fecha_vencimiento, fecha_devolucion, estado) VALUES
('33333333-3', 15, '2025-09-10', '2025-09-17', '2025-09-20', 'devuelto'),
('11111111-1', 6, '2025-09-01', '2025-09-08', '2025-09-07', 'devuelto');

-- Multas
INSERT INTO MULTA (id_prestamo, monto, fecha_generacion, estado) VALUES
(4, 6500, '2025-10-09', 'pendiente');

INSERT INTO MULTA (id_prestamo, monto, fecha_generacion, fecha_pago, estado) VALUES
(5, 1500, '2025-09-20', '2025-09-21', 'pagado');

-- Reservas
INSERT INTO RESERVA (rut_usuario, isbn, fecha_reserva, fecha_expiracion, estado) VALUES
('33333333-3', '9788498387088', '2025-10-20', '2025-10-23', 'pendiente'),
('11111111-1', '9780132354784', '2025-10-21', '2025-10-24', 'pendiente'),
('22222222-2', '9788420674258', '2025-10-15', '2025-10-18', 'cancelado'),
('44444444-4', '9788497592208', '2025-10-08', '2025-10-11', 'cumplido');

-- ============================================
-- 6. CONSULTAS DE VERIFICACIÓN
-- ============================================

-- Verificar usuarios
SELECT 'USUARIOS' AS tabla, COUNT(*) AS total FROM USUARIO;

-- Verificar libros
SELECT 'LIBROS' AS tabla, COUNT(*) AS total FROM LIBRO;

-- Verificar ejemplares
SELECT 'EJEMPLARES' AS tabla, COUNT(*) AS total FROM EJEMPLAR;

-- Verificar préstamos
SELECT 'PRESTAMOS' AS tabla, COUNT(*) AS total FROM PRESTAMO;

-- Ver préstamos activos con días de atraso
SELECT * FROM v_prestamos_activos;

-- Ver multas pendientes
SELECT * FROM v_multas_pendientes;

-- Ver ranking de libros más prestados
SELECT * FROM v_kpi_ranking_libros LIMIT 5;

-- Ver ranking de usuarios más activos
SELECT * FROM v_kpi_ranking_usuarios LIMIT 5;

-- Ver disponibilidad de ejemplares
SELECT * FROM v_disponibilidad_ejemplares;