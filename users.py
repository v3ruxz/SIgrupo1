import sqlite3
import json

f = open('users_data_online.json', 'r')
users_data = json.load(f)

conn = sqlite3.connect('misdatabase.db')
cur = conn.cursor()

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

cur.execute('''
    CREATE TABLE IF NOT EXISTS fechas_ips (
        username TEXT,
        fecha TEXT,
        ip TEXT,
        FOREIGN KEY (username) REFERENCES usuarios(username)
    )
''')

for user_data in users_data['usuarios']:
    for username, user_info in user_data.items():
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

        for fecha, ip in zip(user_info['fechas'], user_info.get('ips', [])):
            cur.execute('INSERT INTO fechas_ips (username, fecha, ip) VALUES (?, ?, ?)', (username, fecha, ip))

conn.commit()
conn.close()
