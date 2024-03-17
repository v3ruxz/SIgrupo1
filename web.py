import sqlite3
import pandas as pd
import hashlib
from flask import Flask, render_template

app = Flask(__name__)


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
def cargarResultadosEj3():
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

    return df_permisos, stats_por_permisos, stats_contraseñas_debiles, contraseñas_debiles

def cargarResultadosEj2():
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

    return num_muestras, media_fechas, std_fechas, media_ips, std_ips, media_phishing, std_phishing, min_email_total, max_email_total, min_email_admin, max_email_admin


@app.route('/')
def inicio():
    return 'Pagina inicio'


@app.route('/ej3')
def ej3():
    df_permisos, stats_por_permisos, stats_contraseñas_debiles, contraseñas_debiles = cargarResultadosEj3()
    return render_template('ej3.html', df_permisos=df_permisos, stats_por_permisos=stats_por_permisos,
                           stats_contraseñas_debiles=stats_contraseñas_debiles, contraseñas_debiles=contraseñas_debiles)


@app.route('/ej2')
def ej2():
    num_muestras, media_fechas, std_fechas, media_ips, std_ips, media_phishing, std_phishing, min_email_total, max_email_total, min_email_admin, max_email_admin = cargarResultadosEj2()
    return render_template('ej2.html', num_muestras=num_muestras, media_fechas=media_fechas, std_fechas=std_fechas, media_ips=media_ips, std_ips=std_ips, media_phishing=media_phishing, std_phishing=std_phishing, min_email_total=min_email_total, max_email_total=max_email_total, min_email_admin=min_email_admin, max_email_admin=max_email_admin)



if __name__ == '__main__':
    app.run(debug=True)
