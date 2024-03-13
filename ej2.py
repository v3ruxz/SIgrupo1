import sqlite3
import json

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
