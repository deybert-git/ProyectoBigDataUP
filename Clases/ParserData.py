import pandas as pd
import numpy as np
import json

class ParserData():

    #declaracion de variables
    v_conexion = None
    v_file = None

    #declaracion de construcctor con la conexion
    def __init__(self,conexion):
        self.v_conexion = conexion
    
    #declaracion de construcctor vacio
    #def __init__(self):
    #    print("Iniciada la Clase Vacia")

    #funcion para leer y limpiar el archivo csv
    def readData(self,ruta,file):
        #Unifica la ruta mas nombre del archivo
        self.v_file = ruta+file      
        
        #Se lee el arvhivo y se guarda en un dataFrame
        df = pd.read_csv(self.v_file)
        
        #Se eliminan las columnas Hora, CAntidad y Sentido
        df.drop(["HORA","CANTIDAD","SENTIDO"],inplace=True,axis=1)

        #Se eliminan los duplicados
        df = df.drop_duplicates()

        #Se cambian los tipos de datos de las columans latitud y longitud
        df['LATITUD'] = df['LATITUD'].astype('str')
        df['LONGITUD'] = df['LONGITUD'].astype('str')
        
        #Para insertar una nueva columna
        #df.insert(0,"ID",list(range(1,(len(df)+1))))
        
        #logs(Propios)
        print("Datos Tratados")

        #retornamos el dataFrame
        return df

    #funcion para insertar datos en la tabla geo_hash(un solo registro)
    def insertSimpleGeoHash(self):
        sql_insert = """ insert into geo_hash(id,geo_hash,latitud,longitud) values(%s,%s,%s,%s) """
        i_params = (1,"geohash1","123.456","987.456")

        try:
            self.v_conexion.execQuery(sql_insert,i_params)
            self.v_conexion.commit()

            print("Se insertaron estos datos:")
            print(i_params)
        
        except ValueError as err:
            print("Este es el error: "+err)

    #funcion para insertar datos en la tabla geo_hash(Multiples Registros)
    def insertTableGeoHash(self,i_arrayParams):
        sql_insert = """ insert into geo_hash(id,geo_hash,latitud,longitud) values(%s,%s,%s,%s) """
        v_array = []
               
        #opcion 1 544ms
        #for datos in i_arrayParams.itertuples():
        #    i=i+1
        #    v_array.append((i,
        #                   datos.CODIGO_LOCACION,
        #                   datos.LATITUD,
        #                   datos.LONGITUD)) 
        
        #opcion 2 48s
        #for index, row in i_arrayParams.iterrows():
        #    v_array.append((i+1,
        #                   row['CODIGO_LOCACION'],
        #                   row['LATITUD'],
        #                   row['LONGITUD']))

        #opcion 3 51.4 ms
        for i in range(len(i_arrayParams)):
            v_array.append((i+1,
                            i_arrayParams.iloc[i]['CODIGO_LOCACION'],
                            i_arrayParams.iloc[i]['LATITUD'],
                            i_arrayParams.iloc[i]['LONGITUD']))
        
        #print(v_array)            
        try:
            self.v_conexion.execQueryArray(queryParams=sql_insert,paramsArray=v_array)
            self.v_conexion.commit()

            print("Se insertaron los siguientes datos:")
            print(v_array)
        
        except ValueError as err:
            print("Este es el error: "+err)