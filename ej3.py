import sqlite3
import pandas as pd
import statistics
import hashlib


'''  
Valores pedidos del ejercicio 3
•	Numero de observaciones
•	Numero de valores ausentes (missing)
•	Mediana
•	Media
•	Varianza
•	Valores máximo y mínimo
RockYou 15 - MD5
https://github.com/danielmiessler/SecLists/blob/master/Passwords/Leaked-Databases/rockyou-15.txt
'''

# Función para cargar el diccionario SmallRockYou
def cargar_diccionario():
    with open('rockyou-15.txt', 'r', encoding='latin-1') as f:
        return [line.strip() for line in f]

# Función para descifrar una contraseña cifrada con MD5
def descifrar_md5(hash):
    with open('rockyou-15.txt', 'r', encoding='latin-1') as f:
        for line in f:
            password = line.strip()
            if hashlib.md5(password.encode()).hexdigest() == hash:
                return password
    return None

def calcular_datos(df):
    print("Numero de observaciones: " + str(sum(df['email_phishing'])))
    print("Numero de valores ausentes: " + str((df['email_phishing'].isnull().sum())))
    print("Mediana: " + str(df['email_phishing'].median()))
    print("Media: " + str(df['email_phishing'].mean()))
    print("Varianza: " + str(statistics.variance(df['email_phishing'])))
    print("Valor maximo: " + str(df['email_phishing'].max()))
    print("Valor minimo: " + str(df['email_phishing'].min()))


if __name__ == '__main__':

    # Conexión a la base de datos
    conn = sqlite3.connect('misdatabase.db')
    query = '''SELECT * FROM usuarios'''
    df_base = pd.read_sql_query(query, conn)

    # Identificación de contraseñas débiles
    diccionario_rockyou = cargar_diccionario()
    query_contraseñas = "SELECT username, contrasena FROM usuarios"
    df_contraseñas = pd.read_sql_query(query_contraseñas, conn)

    contraseñas_debiles = []
    contraseñas_no_debiles = []
    for index, row in df_contraseñas.iterrows():
        contraseña_cifrada = descifrar_md5(row['contrasena'])
        if contraseña_cifrada in diccionario_rockyou:
            contraseñas_debiles.append(row['username'])
        else:
            contraseñas_no_debiles.append(row['username'])

    # DataFrames
    df_users0 = df_base.loc[df_base.permisos == 0]
    df_users1 = df_base.loc[df_base.permisos == 1]

    query_contraseñas_debiles = f"SELECT * FROM usuarios WHERE username IN ({','.join(['?'] * len(contraseñas_debiles))})"
    df_usersWeak = pd.read_sql_query(query_contraseñas_debiles, conn, params=contraseñas_debiles)

    query_contraseñas_no_debiles = f"SELECT * FROM usuarios WHERE username IN ({','.join(['?'] * len(contraseñas_no_debiles))})"
    df_usersNotWeak = pd.read_sql_query(query_contraseñas_no_debiles, conn, params=contraseñas_no_debiles)

    print(df_base)
    print("\n -Usuarios permisos 0:")
    calcular_datos(df_users0)
    print("\n -Usuarios permisos 1:")
    calcular_datos(df_users1)
    print("\n -Usuarios con contraseñas débiles:")
    calcular_datos(df_usersWeak)
    print("\n -Usuarios con contraseñas no débiles:")
    calcular_datos(df_usersNotWeak)
