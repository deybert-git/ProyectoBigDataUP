import pandas as pd
import numpy as np
import json
import geohash as geo
import chardet

class ParserData():

    #declaracion de variables
    v_conexion = None
    v_file = None

    #declaracion de construcctor con la conexion
    def __init__(self,conexion):
        self.v_conexion = conexion
    
    #declaracion de construcctor vacio
    # def __init__(self):
    #    print("Iniciada la Clase Vacia")

    #funcion para leer y limpiar el archivo csv
    def readData(self,ruta,file):
         #Unifica la ruta mas nombre del archivo
        self.v_file = ruta+file  

        #Diferencia los archivos ya q tienen diferentes codificaciones
        if file == "bocas-de-subte.csv":
            df = pd.read_csv(self.v_file, encoding="ISO-8859-1")       
        else:
            df = pd.read_csv(self.v_file)
        
            #elimina filas con datos en nulo
            df = df.dropna(axis=0)

            #elomina columnas con datos en nulo
            df = df.dropna(axis=1)        

        #retornamos el dataFrame
        return df

    def insertTablaUbicacion(self,i_arrayVehiculos,i_arraySubtes):
        #Variables
        sql_insert = """ insert into ubicacion(id_ubicacion,latitud,longitud,geohash) values(%s,%s,%s,%s) """
        v_array = []

        #Tratamos los datos de los movimientos de vehiculos y subtes para guardar las ubicaciones
        df_ubicacion1 = i_arrayVehiculos[["LATITUD","LONGITUD","GEOHASH"]]
        df_ubicacion2 = i_arraySubtes[["lat","long"]].assign(GEOHASH=None)
        df_ubicacion2.columns = ["LATITUD","LONGITUD","GEOHASH"]
        df_ubicacion = pd.concat([df_ubicacion1,df_ubicacion2])
        df_ubicacion = df_ubicacion.drop_duplicates()
        df_ubicacion.insert(0,"ID",list(range(1,(len(df_ubicacion)+1))))          
        
        #Se recorre el df y se pasa a un arreglo para insertarlo en la tabla
        for i in range(len(df_ubicacion)):
            v_array.append((int(df_ubicacion.iloc[i]['ID']),                            
                            str(df_ubicacion.iloc[i]['LATITUD']),
                            str(df_ubicacion.iloc[i]['LONGITUD']),
                            df_ubicacion.iloc[i]['GEOHASH']
                        ))

        try:
            self.v_conexion.execQueryArray(queryParams=sql_insert,paramsArray=v_array)
            self.v_conexion.commit()

            #Log
            print("Se insertaron los Datos de Ubicacion Correctamente")
            
            #Retormamos el df
            return df_ubicacion

        except ValueError as err:
            print("Este es el error: "+err)
    
    def insertTablaSubte(self,i_arraySubtes,i_arrayUbicacion):
        #Variables
        sql_insert = """ insert into subte(id_subte,id_ubicacion,linea,estacion,molinete) values(%s,%s,%s,%s,%s) """
        v_array = []

        #Tratamos los datos de los movimientos de vehiculos y subtes para guardar las ubicaciones
        df_tlbSubte = i_arraySubtes[["lat","long","linea","estacion"]].assign(molinte = i_arraySubtes["dom_orig"].fillna(i_arraySubtes["calle"]))
        df_tlbSubte = df_tlbSubte.drop_duplicates()
        df_tlbSubte = df_tlbSubte.sort_values(by=["linea","estacion"])
        df_tlbSubte.columns = ['LATITUD','LONGITUD','LINEA','ESTACION','MOLINETE']
        df_tlbSubte = pd.merge(df_tlbSubte,i_arrayUbicacion,on=['LATITUD', 'LONGITUD'], how='inner')
        df_tlbSubte.insert(0,"ID_SUB",list(range(1,(len(df_tlbSubte)+1))))
        df_tlbSubte = df_tlbSubte[["ID_SUB","ID","LINEA","ESTACION","MOLINETE"]]        
        
        #Se recorre el df y se pasa a un arreglo para insertarlo en la tabla
        for i in range(len(df_tlbSubte)):
            v_array.append((int(df_tlbSubte.iloc[i]['ID_SUB']),                            
                            int(df_tlbSubte.iloc[i]['ID']),
                            df_tlbSubte.iloc[i]['LINEA'],
                            df_tlbSubte.iloc[i]['ESTACION'],
                            df_tlbSubte.iloc[i]['MOLINETE']
                        ))

        try:
            self.v_conexion.execQueryArray(queryParams=sql_insert,paramsArray=v_array)
            self.v_conexion.commit()

            #Log
            print("Se insertaron los Datos de subtes Correctamente")
            
            #Retormamos el df
            return df_tlbSubte
        
        except ValueError as err:
            print("Este es el error: "+err)   
        
    

    #-------------------------PRUEBAS-----------------------------------#
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

        # #Se eliminan las columnas Hora, CAntidad y Sentido
        i_arrayParams.drop(["HORA","CANTIDAD","SENTIDO"],inplace=True,axis=1)

        # #Se eliminan los duplicados
        i_arrayParams = i_arrayParams.drop_duplicates()

        #Se cambian los tipos de datos de las columans latitud y longitud
        #i_arrayParams['LATITUD'] = i_arrayParams['LATITUD'].astype('str')
        #i_arrayParams['LONGITUD'] = i_arrayParams['LONGITUD'].astype('str')
        
        #Otra forma de cambiar el tipo de dato pero igual da una advertencia
        #i_arrayParams.loc[:,'LATITUD'] = i_arrayParams.loc[:,'LATITUD'].astype(str)
        #i_arrayParams.loc[:,'LONGITUD'] = i_arrayParams.loc[:,'LONGITUD'].astype('str')

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
                            str(i_arrayParams.iloc[i]['LATITUD']),
                            str(i_arrayParams.iloc[i]['LONGITUD'])))
        
        #print(v_array)            
        try:
            self.v_conexion.execQueryArray(queryParams=sql_insert,paramsArray=v_array)
            self.v_conexion.commit()

            print("Se insertaron los siguientes datos:")
            print(v_array)
        
        except ValueError as err:
            print("Este es el error: "+err)
    
            