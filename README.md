# Proyecto de Base de Datos Energética

Este proyecto tiene como objetivo diseñar e implementar una base de datos relacional para gestionar métricas energéticas de un sistema de monitoreo. La base de datos se implementa utilizando PostgreSQL dentro del contenedor Docker.

## Estructura del Proyecto

El proyecto está hecho por los siguientes archivos:

- **docker-compose.yml**: Orquesta la creación y configuración del contenedor PostgreSQL.
- **Dockerfile**: (Opcional) Usado solo si necesitas personalizar la imagen de PostgreSQL.
- **init.sql**: Script SQL para crear las tablas, índices y restricciones necesarias en la base de datos.
- **pg_hba.conf**: Configuración de acceso a PostgreSQL (puede ser la configuración por defecto).
- **postgresql.conf**: Configuración personalizada de PostgreSQL (opcional).
- **README.md**: Este archivo, que contiene instrucciones de uso.
- **bd_energia_diagramER.png**: Imagen que representa el modelo relacional (MER o DER) de la base de datos.

## Requisitos

- Docker y Docker Compose instalados en tu sistema.
- Acceso a la terminal o consola de comandos.
- Uso del sistema de gestión de bases de datos relacional orientado a objetos y de código abierto PostgreSQL 

## Instrucciones de Uso

### Paso 1: Iniciar Docker

Asegúrate de que Docker esté corriendo en tu sistema. Si usas **Docker Desktop**, abre la aplicación y verifica que esté activa.

### Paso 2: Descargar proyecto

Descarga y/o copia el proyecto en tu máquina.

```bash
git clone https://github.com/JeanP09/proyecto_energia.git
cd proyecto_energia_xm
```


### Paso 3: Levantar el contenedor

Dentro de la carpeta del proyecto, abre la terminal y ejecuta el siguiente comando para construir y levantar el contenedor PostgreSQL:

```bash
docker-compose up --build -d
```
Este comando descargará la imagen de PostgreSQL, la construirá si es necesario y levantará el contenedor en segundo plano.

### Paso 4: Acceder a la Base de Datos
Una vez que el contenedor esté corriendo, accede a la base de datos ejecutando:

```bash
docker exec -it energia_postgres psql -U postgres -d bd_energia
```
Esto abrirá una sesión de PostgreSQL dentro del contenedor donde podrás ejecutar comandos SQL.

### Paso 5: Inicializar la Base de Datos
El script ```init.sql``` se ejecuta automáticamente al levantar el contenedor y crea las tablas necesarias, índices y restricciones. No es necesario ejecutar ninguna acción adicional para poblar la base de datos.

### Paso 6: Verificar el estado
Puedes verificar que todo esté funcionando correctamente revisando los logs del contenedor con el siguiente comando:
```bash
docker logs energia_postgres
```

### Consideraciones Adicionales
1. **Configuración de PostgreSQL**: No se requiere ninguna configuración especial para PostgreSQL, solo la ejecución del script init.sql para crear la base de datos y las tablas.

2. **Métricas y API Externas**: No se requiere configuración adicional para métricas ni API externas en esta fase del proyecto.

3. **Sistema Operativo**: Los comandos de Docker y los scripts son compatibles con sistemas operativos como Windows, macOS y Linux. Las rutas son relativas, por lo que el proyecto debería funcionar independientemente del sistema operativo.

### Justificación del Modelo Relacional
El modelo relacional está diseñado para manejar las métricas energéticas de manera eficiente, permitiendo consultas rápidas y fáciles sobre la demanda, generación y capacidad del sistema energético. La estructura sigue las mejores prácticas de diseño de bases de datos, garantizando la integridad de los datos y la optimización para consultas.

La imagen ```bd_energia_diagramER.png``` proporciona una representación visual del modelo de datos utilizado en este proyecto.

### Futuras Mejoras
En una segunda entrega, se incluirá la migración de datos de las APIs externas, así como consultas de ejemplo que contengan 5 consultas que traten de solucionar la pregunta planteada (*4. ¿Cómo se interrelacionan Demanda_Energética, Capacidad_Instalada, Índice_Servicio y Tiempo_Respuesta_Demanda para implementar mejoras que garanticen un servicio eficiente y disminuyan en un 20% los tiempos de respuesta en 9 meses?*) para interactuar con la base de datos.