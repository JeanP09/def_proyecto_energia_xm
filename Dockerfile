FROM postgres:latest

COPY ./init.sql /docker-entrypoint-initdb.d/
COPY ./pg_hba.conf /etc/postgresql/postgresql.conf.d/
COPY ./postgresql.conf /etc/postgresql/postgresql.conf.d/

