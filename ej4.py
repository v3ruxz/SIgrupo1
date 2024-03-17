import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

#---------------Media cambio de contraseña-----------------

# Conexión a la base de datos
conn = sqlite3.connect('misdatabase.db')

# Conversión fechas
def parse_dates(date_series):
    return pd.to_datetime(date_series, format='%d/%m/%Y')

# Consulta SQL
query = '''
SELECT u.username, u.permisos, f.fecha
FROM usuarios u
JOIN fechas_ips f ON u.username = f.username
ORDER BY u.username, f.fecha;
'''

# Lectura resultados
df_cambios = pd.read_sql_query(query, conn)
df_cambios['fecha'] = parse_dates(df_cambios['fecha'])

conn.close()

# Cálculo de la diferencia en días entre cambios de contraseñas de cada usuario
df_cambios['diff'] = df_cambios.groupby('username')['fecha'].diff().dt.days

# Selección de los registros
df_diffs = df_cambios[df_cambios['diff'].notna()]

# Calcular la media de tiempo entre cambios de contraseña para usuarios (permisos=0) y administradores (permisos=1)
mean_diff_normal = df_diffs[df_diffs['permisos'] == 0]['diff'].mean()
mean_diff_admin = df_diffs[df_diffs['permisos'] == 1]['diff'].mean()

# Mostrar la media de tiempo entre cambios de contraseña por tipo de usuario mediante un gráfico de barras
plt.figure(figsize=(10, 5))
plt.bar(['Usuarios', 'Administradores'], [mean_diff_normal, mean_diff_admin], color=['#7D89EF', '#EB3449'])
plt.title('Media de Días Cambios de Contraseña')
plt.ylabel('Días Promedio')
plt.xlabel('Tipo Usuario')
plt.show()

#-----------------Usuarios críticos-------------------

conn = sqlite3.connect('misdatabase.db')

# Consulta SQL para obtener los usuarios más criticos según los clics al email con phishing y los clicados
query_criticos = '''
SELECT username, email_phishing, email_cliclados,
       CAST(email_cliclados AS FLOAT) / email_phishing AS ratio
FROM usuarios
WHERE email_phishing > 0 AND contrasena NOT LIKE "%123456%" 
ORDER BY ratio DESC, email_phishing DESC
LIMIT 10;
'''

# Lectura resultados
df_criticos = pd.read_sql_query(query_criticos, conn)

conn.close()

plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(df_criticos['username'], df_criticos['ratio'], color=plt.cm.Paired(range(len(df_criticos))))

ax.set_title('Top 10 Usuarios Críticos ', fontsize=14)
ax.set_xlabel('Tasa de clic en correos con phishing', fontsize=12)
ax.set_ylabel('Usuario', fontsize=12)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.invert_yaxis()

plt.tight_layout()
plt.show()

#-------------Dominios con políticas desactualizadas-------------

conn = sqlite3.connect('misdatabase.db')

# Consulta SQL para obtener el número de políticas desactualizadas de todos los dominios
query = '''
SELECT domain, (3 - (cookies + aviso + proteccion_de_datos)) AS policies_outdated
FROM legal
ORDER BY policies_outdated DESC
'''

df_all_policies_outdated = pd.read_sql_query(query, conn)

conn.close()

# Creamos un gráfico de barras con todos los dominios y el nº de políticas desactualizadas
plt.figure(figsize=(10, 8))
plt.barh(df_all_policies_outdated['domain'], df_all_policies_outdated['policies_outdated'], color=plt.cm.Paired(range(len(df_all_policies_outdated))))
plt.xlabel('Número de Políticas Desactualizadas')
plt.ylabel('Dominio')
plt.title('Políticas Desactualizadas por Dominio')
plt.tight_layout()
plt.gca().invert_yaxis()
plt.show()

#------------Dominios que cumplen con políticas---------------

conn = sqlite3.connect('misdatabase.db')

query = "SELECT * FROM legal"
df_legal = pd.read_sql_query(query, conn)

conn.close()

# Determinamos si cada web cumple con todas las políticas
df_legal['cumple_todas'] = df_legal.apply(lambda x: x['cookies'] == 1 and x['aviso'] == 1 and x['proteccion_de_datos'] == 1, axis=1)

# Agrupamos por año y calculamos el número de webs que cumplen y no cumplen con las políticas
df_cumplimiento = df_legal.groupby('creacion').cumple_todas.value_counts().unstack(fill_value=0)
df_cumplimiento.columns = ['No_Cumplen', 'Cumplen']

plt.style.use('ggplot')

# Gráfico de barras
ax = df_cumplimiento.plot(kind='bar', stacked=True, figsize=(14, 8), color=['#ff0000', '#77dd77'])
plt.title('Cumplimiento de Políticas de Privacidad por Año de Creación', fontsize=16)
plt.xlabel('Año Creación', fontsize=14)
plt.ylabel('Nº de Webs', fontsize=14)
plt.xticks(rotation=45)
plt.legend(title='Cumplimiento de Políticas', fontsize=12)
plt.tight_layout()

plt.show()

