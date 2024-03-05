import sqlite3
import json

f=open('legal_data_online.json', 'r')
legal_data=json.load(f)

conn = sqlite3.connect('legal.db')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS legal (
        domain TEXT PRIMARY KEY,
        cookies INTEGER,
        aviso INTEGER,
        proteccion_de_datos INTEGER,
        creacion INTEGER
    )
''')

for item in legal_data['legal']:
    for domain, attributes in item.items():
        cur.execute('''
            INSERT OR REPLACE INTO legal (domain, cookies, aviso, proteccion_de_datos, creacion)
            VALUES (?, ?, ?, ?, ?)
        ''', (domain, attributes['cookies'], attributes['aviso'], attributes['proteccion_de_datos'], attributes['creacion']))

conn.commit()
conn.close()

