import os
import pandas as pd
import requests
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Configuración de conexión a PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'energia_xm',
    'user': 'admin',
    'password': 'dbprueba123'
}

# Cargar archivo Excel con métricas
excel_file = os.path.join(os.path.dirname(__file__), 'metricas.xlsx')
df_metricas = pd.read_excel(excel_file)

# Últimos 3 años
fecha_fin = datetime.today().date()
fecha_ini = fecha_fin - relativedelta(years=3)

# Conexión a PostgreSQL
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
except Error as e:
    print(f"❌ Error de conexión a la base de datos: {e}")
    exit(1)

# Obtener IDs
def get_id(tabla, valor):
    campo = 'codigo'
    if tabla.lower() == 'metrica':
        campo = 'metric_id'
    query = f"SELECT id_{tabla.lower()} FROM {tabla} WHERE {campo} = %s"
    cursor.execute(query, (valor,))
    res = cursor.fetchone()
    return res[0] if res else None

# Inserciones
def insert_hourly(fecha, hora, valor, sistema, metric_id):
    id_sistema = get_id("Sistema", sistema)
    id_metrica = get_id("Metrica", metric_id)
    if id_sistema and id_metrica:
        cursor.execute("""
            INSERT INTO Generacion_Horaria (id_sistema, id_metrica, fecha, hora, valor)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (id_sistema, id_metrica, fecha, hora, valor))

def insert_daily(fecha, valor, entidad, metric_id, tabla):
    id_entidad = get_id(tabla, entidad)
    id_metrica = get_id("Metrica", metric_id)
    if id_entidad and id_metrica:
        if metric_id == 'CapEfecNeta':
            cursor.execute("""
                INSERT INTO Capacidad_Diaria (id_recurso, id_metrica, fecha, valor)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (id_entidad, id_metrica, fecha, valor))
        else:
            cursor.execute("""
                INSERT INTO Demanda_Diaria (id_sistema, id_metrica, fecha, valor)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (id_entidad, id_metrica, fecha, valor))
    elif not id_entidad:
        print(f"⚠️ Recurso no encontrado en BD: {entidad}")

# Generación de payload dinámico
def crear_payload(metric_id, start_date, end_date):
    entity = 'Sistema'
    if metric_id == 'CapEfecNeta':
        entity = 'Recurso'
    return {
        "MetricId": metric_id,
        "StartDate": start_date.strftime('%Y-%m-%d'),
        "EndDate": end_date.strftime('%Y-%m-%d'),
        "Entity": entity,
        "Filter": []
    }

# Procesamiento por métrica y mes
def procesar_metrica(row):
    metric_id = row['MetricId']
    if metric_id != 'CapEfecNeta':
        return  # Ignorar otras métricas
    url = row['Url']

    fecha_actual = fecha_ini
    while fecha_actual <= fecha_fin:
        fecha_mes_fin = (fecha_actual + relativedelta(months=1)) - timedelta(days=1)
        if fecha_mes_fin > fecha_fin:
            fecha_mes_fin = fecha_fin

        payload = crear_payload(metric_id, fecha_actual, fecha_mes_fin)
        print(f"→ Consultando {metric_id} desde {payload['StartDate']} a {payload['EndDate']}")

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print(f"❌ Error {response.status_code} para {metric_id}: {response.text}")
        else:
            data = response.json()
            for i, item in enumerate(data.get("Items", [])):
                try:
                    fecha = item["Date"]

                    if metric_id == 'Gene' and 'HourlyEntities' in item:
                        for registro in item['HourlyEntities']:
                            sistema = registro["Id"]
                            values = registro["Values"]
                            for h in range(1, 25):
                                hora_key = f"Hour{h:02}"
                                valor = values.get(hora_key)
                                if valor:
                                    insert_hourly(fecha, h, float(valor), sistema, metric_id)

                    elif metric_id == 'CapEfecNeta' and 'DailyEntities' in item:
                        count = 0
                        for registro in item['DailyEntities']:
                            recurso = registro["Code"]
                            valor = float(registro["Value"])
                            insert_daily(fecha, valor, recurso, metric_id, "Recurso")
                            count += 1
                        print(f"🗓️ {fecha}: {count} recursos insertados")

                    elif metric_id in ['DemaReal', 'DemaCome', 'DemaSIN'] and 'DailyEntities' in item:
                        for registro in item['DailyEntities']:
                            sistema = registro.get("Code", registro.get("Id"))
                            valor = float(registro["Value"])
                            insert_daily(fecha, valor, sistema, metric_id, "Sistema")
                except Exception as e:
                    print(f"⚠️ Error procesando item {i}: {e}")

            conn.commit()

        fecha_actual = fecha_mes_fin + timedelta(days=1)

# Recorrer todas las métricas
try:
    for _, row in df_metricas.iterrows():
        procesar_metrica(row)
finally:
    cursor.close()
    conn.close()
    print("✅ Migración finalizada.")
