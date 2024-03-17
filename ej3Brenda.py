import sqlite3
import pandas as pd
import hashlib



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


# Función para cargar los resultados de la base de datos

conn = sqlite3.connect('misdatabase.db')

# Agrupación por tipo de permisos de usuario
query_permisos = "SELECT permisos, COUNT(*) as count FROM usuarios GROUP BY permisos"
df_permisos = pd.read_sql_query(query_permisos, conn)

# Identificación de contraseñas débiles
diccionario_rockyou = cargar_diccionario()
query_contraseñas = "SELECT username, contrasena FROM usuarios"
df_contraseñas = pd.read_sql_query(query_contraseñas, conn)

contraseñas_debiles = []
for index, row in df_contraseñas.iterrows():
    contraseña_cifrada = descifrar_md5(row['contrasena'])
    if contraseña_cifrada in diccionario_rockyou:
        contraseñas_debiles.append(row['username'])

# Cálculo de estadísticas para la variable dentro del email de phishing
stats_por_permisos = {}
for permiso in [0, 1]:
    query_phishing = f"SELECT email_phishing FROM usuarios WHERE permisos = {permiso}"
    df_phishing = pd.read_sql_query(query_phishing, conn)

    num_observaciones = len(df_phishing)
    valores_ausentes = df_phishing['email_phishing'].isnull().sum()
    mediana = df_phishing['email_phishing'].median()
    media = df_phishing['email_phishing'].mean()
    varianza = df_phishing['email_phishing'].var()
    valor_min = df_phishing['email_phishing'].min()
    valor_max = df_phishing['email_phishing'].max()

    stats_por_permisos[permiso] = {
        'num_observaciones': num_observaciones,
        'valores_ausentes': valores_ausentes,
        'mediana': mediana,
        'media': media,
        'varianza': varianza,
        'valor_min': valor_min,
        'valor_max': valor_max
    }

# Cálculo de estadísticas para contraseñas débiles
query_contraseñas_debiles = f"SELECT email_phishing FROM usuarios WHERE username IN ({','.join(['?'] * len(contraseñas_debiles))})"
df_phishing_contraseñas_debiles = pd.read_sql_query(query_contraseñas_debiles, conn, params=contraseñas_debiles)
stats_contraseñas_debiles = {
    'num_observaciones': len(df_phishing_contraseñas_debiles),
    'valores_ausentes': df_phishing_contraseñas_debiles['email_phishing'].isnull().sum(),
    'mediana': df_phishing_contraseñas_debiles['email_phishing'].median(),
    'media': df_phishing_contraseñas_debiles['email_phishing'].mean(),
    'varianza': df_phishing_contraseñas_debiles['email_phishing'].var(),
    'valor_min': df_phishing_contraseñas_debiles['email_phishing'].min(),
    'valor_max': df_phishing_contraseñas_debiles['email_phishing'].max()
}

# Cerrar la conexión
conn.close()

# Imprimir los datos por consola
print("Agrupación por tipo de permisos de usuario:")
print(df_permisos)
print("\nEstadísticas por tipo de permisos de usuario:")
print(stats_por_permisos)
print("\nEstadísticas para contraseñas débiles:")
print(stats_contraseñas_debiles)
print("\nUsuarios con contraseñas débiles:")
print(contraseñas_debiles)

