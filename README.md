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
git clone https://url-del-repositorio.git
cd proyecto_energia_xm
