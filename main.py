from Clases.Connection import Connection
from Clases.ParserData import ParserData
import pandas as pd
import json

#Definir el entorno que desea inicializar desde el archivo de configuracion
#Entorno = "LOCAL"
Entorno = "DEV"

#Obtener las variables de acceso
with open('./config.json','r') as file:
    config = json.load(file)

#realizar la conexion a la base de datos
conexion = Connection(USER=config[Entorno]['USER'],
                      PASS=config[Entorno]['PASS'],
                      HOST=config[Entorno]['HOST'],
                      DATABASE=config[Entorno]['DATABASE'])

#Instanciamos la Clase ParserData con conexion
parserData = ParserData(conexion=conexion)

#Instanciamos la Clase ParserData sin conexion
# parserData = ParserData()

#---------------------------DATA SETs--------------------------------
v_nameFileSubte = "subte_flujo.csv"
v_nameFileVehicular = "flujo_vehicular_dc.csv"
v_nameFileBocaSubte = "bocas-de-subte.csv"

#Guardamos el resultado del dataFrame en una variable
df_subte = parserData.readData(ruta=config[Entorno]['REP_LOCAL'],file=v_nameFileSubte)
#print("Datos Tratados Subte Cantidad "+str(len(df_subte)))
#print(df_subte.head(5))

df_vehicular = parserData.readData(ruta=config[Entorno]['REP_LOCAL'],file=v_nameFileVehicular)
#print("Datos Tratados Vehicular Cantidad "+str(len(df_vehicular)))
#print(df_vehicular.head(5))

df_bocaSubtes = parserData.readData(ruta=config[Entorno]['REP_LOCAL'],file=v_nameFileBocaSubte)
#print("Datos Tratados Bocas Cantidad "+str(len(df_bocaSubtes)))
#print(df_bocaSubtes.head(5))

#---------------------------TABLAS--------------------------
# 1.- Poblamos la tabla de Fechas
df_fechas = parserData.insertTablaFechas(i_anio_d='2020',i_anio_h='2030')
#print(df_fechas.head(5))

# 2.- Poblamos la tabla ubicaciones
df_RUbicacion = parserData.insertTablaUbicacion(i_arrayVehiculos=df_vehicular.copy(),i_arraySubtes=df_bocaSubtes.copy())
#print(df_RUbicacion.head(5))

# 3.- Poblamos la tabla de subte
df_RSubte = parserData.insertTablaSubte(i_arraySubtes=df_bocaSubtes.copy(),i_arrayUbicacion=df_RUbicacion.copy())
#print(df_RSubte.head(5))

# 4.- Guardamos Movimientos de Vehiculos
df_movSubte = parserData.insertTablaMovSubte(i_arraySubtes=df_subte.copy(),i_arrayBocaSubtes=df_RSubte,i_arrayFechas=df_fechas.copy())
#print(df_movSubte.head(5))

# 5.- Guardamos Movimientos de Subte
df_movVehiculo = parserData.insertTablaMovVehiculo(i_arrayVehiculos=df_vehicular.copy(),i_arrayUbicacion=df_RUbicacion.copy(),i_arrayFechas=df_fechas.copy())
#print(df_movVehiculo.head(5))

#Se cierra la conexion a la BD
conexion.connClose()