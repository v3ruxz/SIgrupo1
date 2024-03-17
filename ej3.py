import sqlite3
import pandas as pd
import statistics

'''
•	Numero de observaciones
•	Numero de valores ausentes (missing)
•	Mediana
•	Media
•	Varianza
•	Valores máximo y mínimo
RockYou 15 - MD5
https://github.com/danielmiessler/SecLists/blob/master/Passwords/Leaked-Databases/rockyou-15.txt
'''

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

    df_users0 = df_base.loc[df_base.permisos == 0]
    df_users1 = df_base.loc[df_base.permisos == 1]
    # df_usersWeak =
    # df_usersNotWeak =
    print(df_base)
    print("\n -Usuarios permisos 0:")
    calcular_datos(df_users0)
    print("\n -Usuarios permisos 1:")
    calcular_datos(df_users1)
