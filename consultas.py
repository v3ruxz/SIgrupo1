import sqlite3
import pandas as pd

# Conexión a la base de datos
conn = sqlite3.connect('misdatabase.db')

# Consulta para obtener los datos de fechas y contraseñas
query = '''
    SELECT u.username, COUNT(fi.fecha) AS total_fechas, COUNT(DISTINCT fi.ip) AS total_ips,
           SUM(u.email_phishing) AS total_phishing,
           MIN(u.email_total) AS min_total_emails, MAX(u.email_total) AS max_total_emails,
           MIN(u.email_phishing) AS min_phishing_emails, MAX(u.email_phishing) AS max_phishing_emails
    FROM usuarios u
    LEFT JOIN fechas_ips fi ON u.username = fi.username
    GROUP BY u.username
'''

# Leer los resultados de la consulta en un DataFrame
df = pd.read_sql_query(query, conn)

# Calcular los valores requeridos
num_muestras = len(df)
media_desviacion_fechas = df['total_fechas'].agg(['mean', 'std'])
media_desviacion_ips = df['total_ips'].agg(['mean', 'std'])
media_desviacion_phishing = df['total_phishing'].agg(['mean', 'std'])
min_max_total_emails = df[['min_total_emails', 'max_total_emails']].agg(['min', 'max'])
min_max_phishing_emails = df[['min_phishing_emails', 'max_phishing_emails']].agg(['min', 'max'])

# Imprimir los resultados
print("Número de muestras:", num_muestras)
print("Media y desviación estándar de fechas cambiadas:", media_desviacion_fechas)
print("Media y desviación estándar de IPs detectadas:", media_desviacion_ips)
print("Media y desviación estándar de emails de phishing:", media_desviacion_phishing)
print("Valor mínimo y máximo de total de emails recibidos:", min_max_total_emails)
print("Valor mínimo y máximo de emails de phishing para administradores:", min_max_phishing_emails)

# Cerrar la conexión a la base de datos
conn.close()