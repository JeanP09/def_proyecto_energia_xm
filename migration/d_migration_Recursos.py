import requests
import psycopg2
from datetime import datetime

# Parámetros de la solicitud
url = "https://servapibi.xm.com.co/Lists"
payload = {
    "MetricId": "ListadoRecursos"
}
headers = {
    "Content-Type": "application/json"
}

# Solicitud POST
response = requests.post(url, json=payload, headers=headers)

# Verifica la respuesta
if response.status_code == 200:
    data = response.json()

    # Conexión a PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        user="admin",
        password="dbprueba123",
        database="energia_xm"
    )
    cursor = conn.cursor()

    # Lista de recursos que deben ser insertados siempre
    recursos_faltantes = ['JPR1', '2YQO', '3C6Y', '3C71', 'JBV1', '3E98', '3BFJ', '3EEG',
                          '3FDA', '3GPV', 'JAG1', 'RUB1', '3KOD', '3PKN', '3PKH', '3RKN', '3RKP', '4SNT']

    # Procesar los recursos de la API
    for item in data.get("Items", []):
        for entity in item.get("ListEntities", []):
            values = entity.get("Values", {})

            codigo = values.get("Code")
            nombre = values.get("Name")
            tipo = values.get("Type")
            tipo_despacho = values.get("Disp")
            tipo_recurso = values.get("RecType")
            codigo_empresa = values.get("CompanyCode")
            fuente_energia = values.get("EnerSource")
            fecha_operacion_str = values.get("OperStartdate")
            estado = values.get("State")

            try:
                fecha_operacion = datetime.strptime(
                    fecha_operacion_str, "%Y-%m-%d").date()
            except:
                fecha_operacion = None

            cursor.execute(
                "SELECT id_recurso FROM Recurso WHERE codigo = %s", (codigo,))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO Recurso (codigo, nombre, tipo, tipo_despacho, tipo_recurso, 
                                        codigo_empresa, fuente_energia, fecha_operacion, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    codigo, nombre, tipo, tipo_despacho, tipo_recurso,
                    codigo_empresa, fuente_energia, fecha_operacion, estado
                ))
                print(f"Insertado: {codigo}")
            else:
                print(f"Ya existe: {codigo}")

    # Insertar los recursos faltantes
    for codigo in recursos_faltantes:
        cursor.execute("""
            INSERT INTO recurso (codigo, nombre, tipo, tipo_despacho, tipo_recurso, 
                                codigo_empresa, fuente_energia, fecha_operacion, estado) 
            VALUES (%s, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
        """, (codigo,))
        print(f"Recurso insertado con valores NULL: {codigo}")

    conn.commit()
    cursor.close()
    conn.close()

else:
    print(f"Error en la solicitud: {response.status_code}")
