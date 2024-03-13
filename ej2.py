# EJERCICIO 2

import sqlite3
import json
import pandas as pd

# Cargar los .json
u = open('users_data_online.json', 'r')
l = open('legal_data_online.json', 'r')
users_data = json.load(u)
legal_data=json.load(l)

# Crear la base de datos
conn = sqlite3.connect('misdatabase.db')
cur = conn.cursor()

# Crear las tablas

# La primera tabla "legal" es para el legal_data_online.json
cur.execute('''
    CREATE TABLE IF NOT EXISTS legal (
        domain TEXT PRIMARY KEY,
        cookies INTEGER,
        aviso INTEGER,
        proteccion_de_datos INTEGER,
        creacion INTEGER
    )
''')

# La segunda tabla "usuarios" es para el users_data_online.json
cur.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY,
        telefono INTEGER,
        contrasena TEXT,
        provincia TEXT,
        permisos INTEGER,
        email_total INTEGER,
        email_phishing INTEGER,
        email_cliclados INTEGER
    )
''')

# La tercera tabla "fechas_ips" es para el users_data_online.json y se enlaza una fecha a una ip dentro de cada usuario
cur.execute('''
    CREATE TABLE IF NOT EXISTS fechas_ips (
        username TEXT,
        fecha TEXT,
        ip TEXT,
        FOREIGN KEY (username) REFERENCES usuarios(username)
    )
''')

# Inserción de datos en la tabla legal
for item in legal_data['legal']:
    for domain, attributes in item.items():
        cur.execute('''
            INSERT OR REPLACE INTO legal (domain, cookies, aviso, proteccion_de_datos, creacion)
            VALUES (?, ?, ?, ?, ?)
        ''', (domain, attributes['cookies'], attributes['aviso'], attributes['proteccion_de_datos'], attributes['creacion']))

# Inserción de datos en la tabla usuarios    
for item in users_data['usuarios']:
    for username, user_info in item.items():
        cur.execute('''
            INSERT INTO usuarios (username, telefono, contrasena, provincia, permisos, email_total, email_phishing, email_cliclados)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            user_info['telefono'],
            user_info['contrasena'],
            user_info['provincia'],
            int(user_info['permisos']),
            user_info['emails']['total'],
            user_info['emails']['phishing'],
            user_info['emails']['cliclados']
        ))

        # Inserción de datos en la tabla fecha_ips    
        for fecha, ip in zip(user_info['fechas'], user_info.get('ips', [])):
            cur.execute('INSERT INTO fechas_ips (username, fecha, ip) VALUES (?, ?, ?)', (username, fecha, ip))

# Se realiza el commit y se cierra la conexión con la base de datos
conn.commit()
conn.close()

# Se vuelve a conectar a la base de datos para hacer las consultas
conn = sqlite3.connect('misdatabase.db')

# Consulta para obtener todos los datos de la tabla usuarios
query_usuarios = "SELECT * FROM usuarios"

# Consulta para obtener todas las fechas e IPs de la tabla fechas_ips
query_fechas_ips = "SELECT username, fecha, ip FROM fechas_ips"

# Leer los datos en un DataFrame de pandas
df_usuarios = pd.read_sql_query(query_usuarios, conn)
df_fechas_ips = pd.read_sql_query(query_fechas_ips, conn)

# Cerrar la conexión
conn.close()

# Calculando el número de muestras (valores distintos de missing)
num_muestras = df_usuarios.shape[0]

# Calculando la media y desviación estándar del total de fechas en las que se ha cambiado la contraseña
media_fechas = df_fechas_ips.groupby('username').size().mean()
std_fechas = df_fechas_ips.groupby('username').size().std()

# Calculando la media y desviación estándar del total de IPs que se han detectado
media_ips = df_fechas_ips.groupby('username')['ip'].nunique().mean()
std_ips = df_fechas_ips.groupby('username')['ip'].nunique().std()

# Calculando la media y desviación estándar del número de email recibidos de phishing en los que ha interactuado cualquier usuario
media_phishing = df_usuarios['email_phishing'].mean()
std_phishing = df_usuarios['email_phishing'].std()

# Valor mínimo y valor máximo del total de emails recibidos
min_email_total = df_usuarios['email_total'].min()
max_email_total = df_usuarios['email_total'].max()

# Valor mínimo y valor máximo del número de emails de phishing en los que ha interactuado un administrador
min_email_admin = df_usuarios[df_usuarios['permisos'] == 1]['email_phishing'].min()
max_email_admin = df_usuarios[df_usuarios['permisos'] == 1]['email_phishing'].max()

# Imprimir los resultados
print("Número de muestras:", num_muestras)
print("Media de fechas de cambio de contraseña:", media_fechas)
print("Desviación estándar de fechas de cambio de contraseña:", std_fechas)
print("Media de IPs detectadas:", media_ips)
print("Desviación estándar de IPs detectadas:", std_ips)
print("Media de emails de phishing:", media_phishing)
print("Desviación estándar de emails de phishing:", std_phishing)
print("Mínimo de emails totales recibidos:", min_email_total)
print("Máximo de emails totales recibidos:", max_email_total)
print("Mínimo de emails de phishing de administrador:", min_email_admin)
print("Máximo de emails de phishing de administrador:", max_email_admin)