# Proyecto Flask clasic
'''
Bootcamp VII
'''
1. Instalar dependencias con
pip install -r requirements.txt

2. CREAR VARIABLE DE ENTORNO
  .Duplicar el fichero .env_templete
  .Renombrar la copia a .env
  .informar FLASK_ENV a elegir entre development y production

3. Crear Fichero de configuración
  .Duplicar el fichero config_templete.py
  .Renombrar la copia a config.py
  .Informar SECRET_KEY. un buen sitio para crear claves:https://randomkeygen.com/
  .Informar el fichero de base de datos. La ruta debe estar dentro del proyecto carpeta data

4. Crear base de datos ejecutando el fichero migrations/inital.sgl
   .puedes hacerlo con un cliente gráfico o con squlite3
   .Ejecutar lo siguiente  
   sqlite3 <ruta al fichero es la carpeta data>
   .red <ruta relativa a migrations/initial.sql>
   .tables
   .q
5. lanzar la a plicación.
. Abrir una consola y ejecutar flask run.
. se lanzará un navegador en 127.0.0.1:5000