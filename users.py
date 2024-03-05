import sqlite3
import json

f=open('users_data_online.json', 'r')
users_data = json.load(f)

conn = sqlite3.connect('user.db')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY,
        telefono INTEGER,
        contrasena TEXT,
        provincia TEXT,
        permisos INTEGER
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        username TEXT,
        total INTEGER,
        phishing INTEGER,
        cliclados INTEGER,
        FOREIGN KEY (username) REFERENCES usuarios(username)
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS fechas (
        username TEXT,
        fecha TEXT,
        FOREIGN KEY (username) REFERENCES usuarios(username)
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS ips (
        username TEXT,
        ip TEXT,
        FOREIGN KEY (username) REFERENCES usuarios(username)
    )
''')

for user_data in users_data['usuarios']:
    for username, user_info in user_data.items():
        cur.execute('''
            INSERT INTO usuarios (username, telefono, contrasena, provincia, permisos)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, user_info['telefono'], user_info['contrasena'], user_info['provincia'], int(user_info['permisos'])))

        cur.execute('''
            INSERT INTO emails (username, total, phishing, cliclados)
            VALUES (?, ?, ?, ?)
        ''', (username, user_info['emails']['total'], user_info['emails']['phishing'], user_info['emails']['cliclados']))

        for fecha in user_info['fechas']:
            cur.execute('INSERT INTO fechas (username, fecha) VALUES (?, ?)', (username, fecha))

        if 'ips' in user_info:
            for ip in user_info['ips']:
                cur.execute('INSERT INTO ips (username, ip) VALUES (?, ?)', (username, ip))

conn.commit()
conn.close()
