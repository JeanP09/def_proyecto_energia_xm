-- Crear tabla de sistemas energéticos
CREATE TABLE Sistema (
    id_sistema SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL
);

-- Crear tabla de recursos energéticos
CREATE TABLE Recurso (
    id_recurso SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL
);

-- Crear tabla de métricas
CREATE TABLE Metrica (
    id_metrica SERIAL PRIMARY KEY,
    metric_id VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- Crear tabla de demanda diaria con partición por fecha
CREATE TABLE Demanda_Diaria (
    id SERIAL,
    id_sistema INT NOT NULL,
    id_metrica INT NOT NULL,
    fecha DATE NOT NULL,
    valor DECIMAL(20,5) NOT NULL,
    PRIMARY KEY (id, fecha),
    FOREIGN KEY (id_sistema) REFERENCES Sistema(id_sistema),
    FOREIGN KEY (id_metrica) REFERENCES Metrica(id_metrica)
) PARTITION BY RANGE (fecha);

-- Crear tabla de capacidad diaria con partición por fecha
CREATE TABLE Capacidad_Diaria (
    id SERIAL,
    id_recurso INT NOT NULL,
    id_metrica INT NOT NULL,
    fecha DATE NOT NULL,
    valor DECIMAL(20,5) NOT NULL,
    PRIMARY KEY (id, fecha),
    FOREIGN KEY (id_recurso) REFERENCES Recurso(id_recurso),
    FOREIGN KEY (id_metrica) REFERENCES Metrica(id_metrica)
) PARTITION BY RANGE (fecha);

-- Crear tabla de generación horaria con partición por fecha
CREATE TABLE Generacion_Horaria (
    id SERIAL,
    id_sistema INT NOT NULL,
    id_metrica INT NOT NULL,
    fecha DATE NOT NULL,
    hora SMALLINT NOT NULL,
    valor DECIMAL(20,5) NOT NULL,
    PRIMARY KEY (id, fecha, hora),
    FOREIGN KEY (id_sistema) REFERENCES Sistema(id_sistema),
    FOREIGN KEY (id_metrica) REFERENCES Metrica(id_metrica)
) PARTITION BY RANGE (fecha);

-- Crear particiones por año para cada tabla
DO $$
DECLARE
    y INT := 2022;
BEGIN
    WHILE y <= 2025 LOOP
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS Demanda_Diaria_%s
            PARTITION OF Demanda_Diaria
            FOR VALUES FROM (''%s-01-01'') TO (''%s-01-01'');
        ', y, y, y + 1);

        EXECUTE format('
            CREATE TABLE IF NOT EXISTS Capacidad_Diaria_%s
            PARTITION OF Capacidad_Diaria
            FOR VALUES FROM (''%s-01-01'') TO (''%s-01-01'');
        ', y, y, y + 1);

        EXECUTE format('
            CREATE TABLE IF NOT EXISTS Generacion_Horaria_%s
            PARTITION OF Generacion_Horaria
            FOR VALUES FROM (''%s-01-01'') TO (''%s-01-01'');
        ', y, y, y + 1);

        y := y + 1;
    END LOOP;
END $$;

-- Insertar métricas usadas
INSERT INTO Metrica (metric_id, nombre, descripcion) VALUES
('DemaReal', 'Demanda Real por Sistema', 'Demanda energética registrada por el SIN.'),
('DemaCome', 'Demanda Comercial por Sistema', 'Demanda comercial registrada por el SIN.'),
('DemaSIN', 'Demanda SIN', 'Demanda del Sistema Interconectado Nacional.'),
('CapEfecNeta', 'Capacidad Efectiva Neta', 'Capacidad neta instalada por recurso.'),
('Gene', 'Generación por Sistema', 'Generación horaria de energía eléctrica.');

-- Insertar ejemplo de sistemas
INSERT INTO Sistema (codigo, nombre) VALUES
('SIN', 'Sistema Interconectado Nacional'),
('SYSX', 'Sistema Experimental X');

-- Insertar ejemplo de recursos
INSERT INTO Recurso (codigo, nombre) VALUES
('2QBW', 'Planta Térmica 2QBW'),
('9VXY', 'Planta Hidráulica 9VXY');
