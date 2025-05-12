import os
import requests
import pandas as pd
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'energia_xm',
    'user': 'admin',
    'password': 'dbprueba123'
}

# Cargar archivo Excel con URL de DemaSIN
excel_file = os.path.join(os.path.dirname(__file__), 'metricas.xlsx')
df_metricas = pd.read_excel(excel_file)
url = df_metricas[df_metricas['MetricId'] == 'DemaSIN']['Url'].values[0]

# Fechas: últimos 3 años
fecha_fin = datetime.today().date()
fecha_ini = fecha_fin - relativedelta(years=3)

# Conectar a PostgreSQL
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
except Error as e:
    print(f"❌ Error conectando a la base de datos: {e}")
    exit(1)

# Obtener ID de un sistema o métrica
def get_id(tabla, valor):
    campo = 'metric_id' if tabla.lower() == 'metrica' else 'codigo'
    query = f"SELECT id_{tabla.lower()} FROM {tabla} WHERE {campo} = %s"
    cursor.execute(query, (valor,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

# Insertar en Demanda_Diaria
def insert_demasin(fecha, valor):
    id_sistema = get_id("Sistema", "SIN")
    id_metrica = get_id("Metrica", "DemaSIN")
    if id_sistema and id_metrica:
        cursor.execute("""
            INSERT INTO Demanda_Diaria (id_sistema, id_metrica, fecha, hora, valor)
            VALUES (%s, %s, %s, -1, %s)
        """, (id_sistema, id_metrica, fecha, valor))
    else:
        print("⚠️ ID de sistema o métrica no encontrado")

# Consultar e insertar datos mensuales
def procesar_demasin():
    fecha_actual = fecha_ini
    while fecha_actual <= fecha_fin:
        fecha_mes_fin = (fecha_actual + relativedelta(months=1)) - timedelta(days=1)
        if fecha_mes_fin > fecha_fin:
            fecha_mes_fin = fecha_fin

        payload = {
            "MetricId": "DemaSIN",
            "StartDate": fecha_actual.strftime('%Y-%m-%d'),
            "EndDate": fecha_mes_fin.strftime('%Y-%m-%d'),
            "Entity": "Sistema",
            "Filter": []
        }

        print(f"→ Consultando DemaSIN: {payload['StartDate']} a {payload['EndDate']}")
        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
        else:
            data = response.json()
            for item in data.get("Items", []):
                fecha = item["Date"]
                for registro in item.get("DailyEntities", []):
                    if registro["Id"] == "Sistema":
                        valor = float(registro["Value"])
                        insert_demasin(fecha, valor)
                        print(f"✅ Insertado: {fecha} → {valor}")

            conn.commit()

        fecha_actual = fecha_mes_fin + timedelta(days=1)

# Ejecutar todo
try:
    procesar_demasin()
finally:
    cursor.close()
    conn.close()
    print("✅ Proceso finalizado.")
