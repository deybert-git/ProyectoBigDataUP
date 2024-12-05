from Clases.Connection import Connection
from Clases.ParserData import ParserData
from Clases.ParserDataBD import ParserDataBD
import json

#Definir el entorno que desea inicializar desde el archivo de configuracion
Entorno = "DEV1.1"
#Entorno = "DEV"

#Obtener las variables de acceso
with open('./config.json','r') as file:
    config = json.load(file)

#realizar la conexion a la base de datos
conexion = Connection(USER=config[Entorno]['USER'],
                      PASS=config[Entorno]['PASS'],
                      HOST=config[Entorno]['HOST'],
                      DATABASE=config[Entorno]['DATABASE'])

#Instanciamos la Clase ParserData
parserData = ParserData()

#Instanciamos la Clase ParserData sin conexion
parserDataBD = ParserDataBD(conexion=conexion)

#---------------------------DATA SETs--------------------------------
v_nameFileFlujoSubte = "PAX15"
v_nameFileVehicular = "flujo_vehicular_dc"
v_nameFileBocaSubte = "bocas-de-subte"

# #LIMPIAR ARCHIVOS: Este proceso consiste en cambiar los formatos de los archivos para que se puedan procesar
# parserData.clean_data_batch(ruta=config[Entorno]['REP_LOCAL'])

# #PROCESAR ARCHIVOS: Este proceso consisten en eliminar los acentos y caracteres especiales de las columnas tipo string, limpiar campos nulos y homologar los nombres de las bocas del subte
# #Todos los archivos limpios encontrados de mov de subte los ejecuta uno a uno
# parserData.read_data_batch(config[Entorno]['REP_LOCAL'],v_nameFileFlujoSubte)

# # Todos los archivos de Flujo vehicular los unifica en uno solo
# parserData.read_data_join(i_ruta=config[Entorno]['REP_LOCAL'],i_textFileName=v_nameFileVehicular)

# # Todos los archivos de boca subte los unifica en uno solo
# parserData.read_data_join(i_ruta=config[Entorno]['REP_LOCAL'],i_textFileName=v_nameFileBocaSubte)

# Hasta aqui el proceso puede ser independiente ya que si se cuentan con los archivos procesados se puede continuar asi.

#---------------------------TABLAS--------------------------
#Se rescatan los archivos procesados y se guardan en dataframe
df_vehicular = parserData.readCSV(config[Entorno]['REP_LOCAL']+"Procesados/","flujo_vehicular_dc_prc.csv")
df_bocaSubtes = parserData.readCSV(config[Entorno]['REP_LOCAL']+"Procesados/","bocas-de-subte_prc.csv")
#df_subte = parserData.readCSV(config[Entorno]['REP_LOCAL']+"Procesados/","202401_PAX15min-ABC_prc_1.csv")

# 1.- Poblamos la tabla de Fechas
df_fechas = parserDataBD.insertTablaFechas(i_anio_d='2020',i_anio_h='2030')
# print(df_fechas.head(5))

# 2.- Poblamos la tabla ubicaciones
df_RUbicacion = parserDataBD.insertTablaUbicacion(i_arrayVehiculos=df_vehicular.copy(),i_arraySubtes=df_bocaSubtes.copy())
#print(df_RUbicacion.head(5))

# 3.- Poblamos la tabla de subte
df_RSubte = parserDataBD.insertTablaSubte(i_arraySubtes=df_bocaSubtes.copy(),i_arrayUbicacion=df_RUbicacion.copy())
#print(df_RSubte.head(5))

# 4.- Guardamos Movimientos de Vehiculos
#df_movVehiculo = parserDataBD.insertTablaMovVehiculo(i_arrayVehiculos=df_vehicular.copy(),i_arrayUbicacion=df_RUbicacion.copy(),i_arrayFechas=df_fechas.copy())

# 5.- Guardamos Movimientos de Subte
parserDataBD.insertLotesMovSubte(config[Entorno]['REP_LOCAL'],df_RSubte.copy(),df_fechas.copy())

#Se cierra la conexion a la BD
conexion.connClose()