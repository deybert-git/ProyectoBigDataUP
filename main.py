from Clases.Connection import Connection
from Clases.ParserData import ParserData
import json

#Definir el entorno que desea inicializar desde el archivo de configuracion
Entorno = "LOCAL"
#Entorno = "DEV"
v_df = None
v_nameFile = None

#Obtener las variables de acceso
with open('./config.json','r') as file:
    config = json.load(file)

#realizar la conexion a la base de datos
conexion = Connection(USER=config[Entorno]['USER'],
                      PASS=config[Entorno]['PASS'],
                      HOST=config[Entorno]['HOST'],
                      DATABASE=config[Entorno]['DATABASE'])

#Instanciamos la Clase ParserData
parserData = ParserData(conexion=conexion)
#Definimos el archivo que se va a leer
#v_nameFile = "output_file-1.csv"
v_nameFile = "dataset_flujo_vehicular_formateado_cleaned.csv"

#Guardamos el resultado del dataFrame en una variable
v_df = parserData.readData(ruta=config[Entorno]['REP_LOCAL'],file=v_nameFile)

#Guardamos los datos en una tabla
parserData.insertTableGeoHash(i_arrayParams=v_df)
