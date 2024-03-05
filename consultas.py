import sqlite3
import pandas as pd

# Conecta con la base de datos
conn = sqlite3.connect('user.db')

# Realiza la consulta para obtener los datos necesarios
query = '''
    SELECT u.username, u.telefono, u.contrasena, u.provincia, e.total, e.phishing, f.fecha, i.ip, u.permisos
    FROM usuarios u
    LEFT JOIN emails e ON u.username = e.username
    LEFT JOIN fechas f ON u.username = f.username
    LEFT JOIN ips i ON u.username = i.username
'''

# Carga los datos en un DataFrame
df_users = pd.read_sql_query(query, conn)

# Cierra la conexión
conn.close()

# Visualiza el conjunto de datos
print(df_users.head(20))