# alymoly

## Descarga de programas y archivos
* [Descargar](http://archivos.crecelibre.cl/alymoly.zip) la base de datos
* [Descargar](https://github.com/CreceLibre/alymoly/archive/master.zip) el app de github
* [Instalar](https://www.python.org/downloads/) python2.7.x  
* [instalar](https://pip.pypa.io/en/latest/installing/) pip  (Para esta instalacion; `C:\Python27` debe estar en el `path` de windows )
* [Instalar](https://www.postgresql.org/download/windows/) PostgreSQL 9.5.4

## Setup

Agregar variables al PATH de windows para usar los programas que se descargaron. Para esto hay que ir a "Propiedades del Sistema", luego hacer click en "Variables de entorno", luego buscar por "path" en la lista de "Variables del sistema", y hacer click en "Editar"
* C:\Python27
* C:\Python27\Scripts
* C:\Program Files\PostgreSQL\9.5\bin

Luego crear un directorio llamado "app" en la carpeta raiz del ususario (por ejemplo `C:\Users\USUARIO\app`), en ese directorio descomprimir el app de github que se bajo anteriormente.

Luego abrir el command prompt (o buscar por cmd en el buscador del menu de inicio de windows 10) y tipar lo siguiente:
```bash
cd app\alymoly-master
```
Si todo estuvo bien configurado, deberias poder ver la raiz de la aplicacion si tipeas `dir`

El proximo paso es instalar las librerias ncesarias de la aplicacion, en la misma ventana de `cmd` que se uso anteriormente tipear lo siguiente:
```bash
pip install -r requirements.txt
```
### Restauracion de la base de datos
#### PgAdminIII
Antes de restaurar la base de datos, debemos crear una localmente para esto iniciamos el programa `pgadmin` (fue instalado con postgresql).
En pgadmin debemos crear el rol `alymoly` y su password debe ser `alymoly`, luego creamos una base de datos llamada `alymoly` y su propietario debe ser el rol que acabamos de crear `alymoly`.
#### SQL Shell
Ahora debemos cargar el archivo de base de datos que fue descargado anteriormente, para eso lo descomprimimos en un directorio que conocemos, luego iniciamos el programa `SQL Shell`  (fue instalado con postgresql), el programa preguntara por informacion de autenticacion y la base de datos , a continuacion listo los valores que hay que ingresar
```bash
Server {localhost}: localhost
Database [postgres]: alymoly
Port [5432]: 5432
Username [postgres]: alymoly
Password for user alymoly: alymoly
```
Una vez loggeado, procedemos a restaurar la base de datos, para esto copiar la ruta donde fue descomprimido el archivo y cargar la base de datos usando el comando `\i` por ejemplo
```bash
\i 'C:/Users/USERNAME/Downloads/alymoly/alymoly.backup'
```

## Prueba del sistema

Ahora procedemos a probar que el sistema funciona correctamente, para esto lanzar `cmd` nuevamente y escribir lo siguientes comandos
```bash
cd app\alymoly-master
python manage.py runserver
```

Ahora que el servidor de prueba esta en ejecucion, abrimos la siguiente direccion en nuestro browser: http://127.0.0.1:8000/admin

Si todo anda bien, se podra ver la pantalla de login.
