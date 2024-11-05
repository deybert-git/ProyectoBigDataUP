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

    #funcion para leer y limpiar el archivo csv, limpia solo filas con datos nulos
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

    #Funcion que permite poblar la tabla de Ubicaciones con coordenadas y geohash
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
    
    #Funcion que permite poblar la tabla con los subtes, molitenes y ubicaciones
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
        
    #Funcion que permite poblar la tabla fechas de calendario
    def insertTablaFechas(self,i_anio_d,i_anio_h):
        #Variables
        sql_insert = """ insert into fechas(fecha,dia,mes,anio) values(%s,%s,%s,%s) """
        v_array = []

        if i_anio_d < i_anio_h:
            #Tratamos los datos de los movimientos de vehiculos y subtes para guardar las ubicaciones      
            fechas = pd.date_range(start=i_anio_d+'-01-01', end=i_anio_h+'-12-31', freq='D')
            df_fechas = pd.DataFrame(fechas, columns=['FECHA'])
            df_fechas = df_fechas[['FECHA']].assign(DIA = df_fechas['FECHA'].dt.day,MES=df_fechas['FECHA'].dt.month,ANIO=df_fechas['FECHA'].dt.year)
            #df_fechas['Dia'] = df_fechas['Fecha'].dt.day
            #df_fechas['Mes'] = df_fechas['Fecha'].dt.month
            #df_fechas['Anio'] = df_fechas['Fecha'].dt.year
            #df_fechas.insert(0,"ID_FECHA",list(range(1,(len(df_fechas)+1))))  
        else:
            raise ValueError("Datos inconsistentes")

        #Se recorre el df y se pasa a un arreglo para insertarlo en la tabla
        for i in range(len(df_fechas)):
            v_array.append((df_fechas.iloc[i]['FECHA'].strftime('%Y-%m-%d'),                            
                            int(df_fechas.iloc[i]['DIA']),
                            int(df_fechas.iloc[i]['MES']),
                            int(df_fechas.iloc[i]['ANIO'])
                        ))      

        try:
            self.v_conexion.execQueryArray(queryParams=sql_insert,paramsArray=v_array)
            self.v_conexion.commit()

            #Log
            print("Se insertaron los Datos de subtes Correctamente")
            
            #Retormamos el df
            return df_fechas
        
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
            