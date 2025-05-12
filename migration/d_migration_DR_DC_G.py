import os
import pandas as pd
import requests
import psycopg2
from psycopg2 import sql, OperationalError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'energia_xm',
    'user': 'admin',
    'password': 'dbprueba123'
}

# Carga de datos desde el archivo Excel
excel_file = os.path.join(os.path.dirname(__file__), 'metricas.xlsx')
df_metricas = pd.read_excel(excel_file)

# Fechas: últimos 3 años
fecha_fin = datetime.today().date()
fecha_ini = fecha_fin - relativedelta(years=3)

# Conexión
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
except OperationalError as e:
    print(f"❌ Error de conexión a la base de datos: {e}")
    exit(1)

# Obtener el ID de las tablas
def get_id(tabla, valor):
    campo = 'codigo'
    if tabla.lower() == 'metrica':
        campo = 'metric_id'
    tabla = tabla.lower()  # Asegura que use minúsculas
    query = f"SELECT id_{tabla} FROM {tabla} WHERE {campo} = %s"
    cursor.execute(query, (valor,))
    res = cursor.fetchone()
    return res[0] if res else None

# Inserciones
def insert_demanda_diaria_demareal_demacome(fecha, hora, valor, metric_id):
    id_sistema = get_id("Sistema", "SIN")
    id_metrica = get_id("Metrica", metric_id)
    if id_sistema and id_metrica:
        cursor.execute("""
            INSERT INTO Demanda_Diaria (id_sistema, id_metrica, fecha, hora, valor)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (id_sistema, id_metrica, fecha, hora, valor))

def insert_generacion_horaria(fecha, hora, valor, metric_id):
    id_sistema = get_id("Sistema", "SIN")
    id_metrica = get_id("Metrica", metric_id)
    if id_sistema and id_metrica:
        cursor.execute("""
            INSERT INTO Generacion_Horaria (id_sistema, id_metrica, fecha, hora, valor)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (id_sistema, id_metrica, fecha, hora, valor))

# Crear el payload para la API
def crear_payload(metric_id, start_date, end_date):
    return {
        "MetricId": metric_id,
        "StartDate": start_date.strftime('%Y-%m-%d'),
        "EndDate": end_date.strftime('%Y-%m-%d'),
        "Entity": "Sistema",
        "Filter": []
    }

# Proceso de cada métrica
def procesar_metrica(row):
    metric_id = row['MetricId']
    if metric_id not in ['DemaReal', 'DemaCome', 'Gene']:
        return  # Ignorar otras métricas

    url = row['Url']
    fecha_actual = fecha_ini

    while fecha_actual <= fecha_fin:
        fecha_mes_fin = (fecha_actual + relativedelta(months=1)) - timedelta(days=1)
        if fecha_mes_fin > fecha_fin:
            fecha_mes_fin = fecha_fin

        payload = crear_payload(metric_id, fecha_actual, fecha_mes_fin)
        print(f"→ Consultando {metric_id} desde {payload['StartDate']} a {payload['EndDate']}")

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            for item in data.get("Items", []):
                fecha = item["Date"]
                if metric_id in ['DemaReal', 'DemaCome', 'Gene'] and 'HourlyEntities' in item:
                    for registro in item['HourlyEntities']:
                        values = registro.get("Values", {})
                        for h in range(1, 25):  # 24 horas
                            clave_hora = f"Hour{h:02d}"
                            if clave_hora in values:
                                try:
                                    valor = float(values[clave_hora])
                                    hora = h - 1
                                    if metric_id in ['DemaReal', 'DemaCome']:
                                        insert_demanda_diaria_demareal_demacome(fecha, hora, valor, metric_id)
                                    else:
                                        insert_generacion_horaria(fecha, hora, valor, metric_id)
                                except ValueError:
                                    print(f"⚠️ Valor inválido en {clave_hora}: {values[clave_hora]}")

            conn.commit()

        except Exception as e:
            print(f"❌ Error al procesar {metric_id}: {e}")

        fecha_actual = fecha_mes_fin + timedelta(days=1)

# Procesar todas las métricas
try:
    for _, row in df_metricas.iterrows():
        procesar_metrica(row)
finally:
    cursor.close()
    conn.close()
    print("✅ Migración terminada")
