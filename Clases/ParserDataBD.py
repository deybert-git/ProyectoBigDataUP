import pandas as pd
import numpy as np
import json
import chardet
import pygeohash as pygeo
from unidecode import unidecode
import re

class ParserDataBD():

#declaracion de variables
    v_conexion = None
    v_file = None

#declaracion de construcctor con la conexion
    def __init__(self,conexion):
        self.v_conexion = conexion
    
#declaracion de construcctor vacio
    # def __init__(self):
    #    print("Iniciada la Clase Vacia")   

#Funcion que permite poblar la tabla de Ubicaciones con coordenadas y geohash
    def insertTablaUbicacion(self,i_arrayVehiculos,i_arraySubtes):
        #Variables
        sql_insert = """ insert into ubicacion(id_ubicacion,latitud,longitud,geohash) values(%s,%s,%s,%s) """
        v_array = []

        #consulta a la base de datos y retorna los datos de la base
        sql_select = """ select LATITUD,LONGITUD from ubicacion """
        df_ubicacionBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)

        #Tratamos los datos de los movimientos de vehiculos y subtes para guardar las ubicaciones
        df_ubicacion1 = i_arrayVehiculos[["LATITUD","LONGITUD","GEOHASH"]]
        df_ubicacion2 = i_arraySubtes[["lat","long"]].assign(GEOHASH=None)
        df_ubicacion2.columns = ["LATITUD","LONGITUD","GEOHASH"]
        df_ubicacion = pd.concat([df_ubicacion1,df_ubicacion2])
        df_ubicacion = df_ubicacion.drop_duplicates()
        df_ubicacion.insert(0,"ID",list(range(1,(len(df_ubicacion)+1)))) 

        #Solo inserta la diferencia de Ubicaciones que estan en la bd
        if len(df_ubicacionBD) > 0:
            df_ubicacionBD["LATITUD"] = pd.to_numeric(df_ubicacionBD["LATITUD"], errors='coerce')
            df_ubicacionBD["LONGITUD"] = pd.to_numeric(df_ubicacionBD["LONGITUD"], errors='coerce')            
            df_ubicacion = pd.merge(df_ubicacion, df_ubicacionBD, how='left', indicator=True)
            df_ubicacion = df_ubicacion[df_ubicacion['_merge'] == 'left_only'].drop(columns=['_merge'])              
        
        #Se recorre el df y se pasa a un arreglo para insertarlo en la tabla
        # for i in range(len(df_ubicacion)):
        #     v_array.append((int(df_ubicacion.iloc[i]['ID']),                            
        #                     str(df_ubicacion.iloc[i]['LATITUD']),
        #                     str(df_ubicacion.iloc[i]['LONGITUD']),
        #                     df_ubicacion.iloc[i]['GEOHASH']
        #                 ))
            
        for i in range(len(df_ubicacion)):
            v_array.append((int(df_ubicacion.iloc[i]['ID']),                            
                            str(df_ubicacion.iloc[i]['LATITUD']),
                            str(df_ubicacion.iloc[i]['LONGITUD']),
                            pygeo.encode(df_ubicacion.iloc[i]['LATITUD'], df_ubicacion.iloc[i]['LONGITUD'], precision=6)
                        ))

        try:
            self.v_conexion.execQueryArray(queryParams=sql_insert,paramsArray=v_array)
            self.v_conexion.commit()

            #Log
            print("Se insertaron los Datos de UBICACION Correctamente")
            
            #consulta a la base de datos y retorna los datos de la base
            sql_select = """ select id_ubicacion as ID, LATITUD, LONGITUD, GEOHASH from ubicacion """
            df_ubicacionBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)
            
            #Retormamos el df
            return df_ubicacionBD

        except ValueError as err:
            print("Este es el error: "+err)
    
#Funcion que permite poblar la tabla con los subtes, molitenes y ubicaciones
    def insertTablaSubte(self,i_arraySubtes,i_arrayUbicacion):
        #Variables
        sql_insert = """ insert into subte(id_subte,id_ubicacion,linea,estacion,molinete) values(%s,%s,%s,%s,%s) """
        v_array = []

        #consulta a la base de datos y retorna los datos de la base
        sql_select = """ select LINEA, ESTACION from subte """
        df_subteBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)

        #Tratamos los datos de los movimientos de vehiculos y subtes para guardar las ubicaciones
        #df_tlbSubte = i_arraySubtes[["lat","long","linea","estacion"]].assign(molinte = i_arraySubtes["dom_orig"].fillna(i_arraySubtes["calle"]))
        df_tlbSubte = i_arraySubtes[["lat","long","linea","estacion"]].assign(molinte = None)
        df_tlbSubte = df_tlbSubte.drop_duplicates(subset=['linea', 'estacion'])
        df_tlbSubte = df_tlbSubte.sort_values(by=["linea","estacion"])
        df_tlbSubte.columns = ['LATITUD','LONGITUD','LINEA','ESTACION','MOLINETE']        
        i_arrayUbicacion["LATITUD"] = pd.to_numeric(i_arrayUbicacion["LATITUD"], errors='coerce')
        i_arrayUbicacion["LONGITUD"] = pd.to_numeric(i_arrayUbicacion["LONGITUD"], errors='coerce')        
        df_tlbSubte = pd.merge(df_tlbSubte,i_arrayUbicacion,on=['LATITUD', 'LONGITUD'], how='inner')
        df_tlbSubte.insert(0,"ID_SUB",list(range(1,(len(df_tlbSubte)+1))))
        df_tlbSubte = df_tlbSubte[["ID_SUB","ID","LINEA","ESTACION","MOLINETE"]]  
       

        if len(df_subteBD) > 0:                         
            df_tlbSubte = pd.merge(df_tlbSubte, df_subteBD, how='left', indicator=True)
            df_tlbSubte = df_tlbSubte[df_tlbSubte['_merge'] == 'left_only'].drop(columns=['_merge'])       
        
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
            print("Se insertaron los Datos de SUBTES Correctamente")

            #consulta a la base de datos y retorna los datos de la base
            sql_select = """ select * from subte """
            df_subteBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)
            
            #Retormamos el df
            return df_subteBD
        
        except ValueError as err:
            print("Este es el error: "+err)   
        
    #Funcion que permite poblar la tabla fechas de calendario
    def insertTablaFechas(self,i_anio_d,i_anio_h):
        #Variables
        sql_insert = """ insert into fechas(fecha,dia,mes,anio) values(%s,%s,%s,%s) """
        v_array = []

        #consulta a la base de datos y retorna los datos de la base
        sql_select = """ select date_format(FECHA,'%Y-%m-%d') FECHA, DIA, MES, ANIO from fechas """
        df_fechasBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)        

        #Evalua si los datos vienen o no
        if len(i_anio_d) == 0 or len(i_anio_h) == 0:
            raise ValueError("Faltan Datos")
        
        #Evalua si el año desde es menor que el año hasta
        if (i_anio_d < i_anio_h):
            #Tratamos los datos de los movimientos de vehiculos y subtes para guardar las ubicaciones      
            fechas = pd.date_range(start=i_anio_d+'-01-01', end=i_anio_h+'-12-31', freq='D')
            df_fechas = pd.DataFrame(fechas, columns=['FECHA'])
            df_fechas = df_fechas[['FECHA']].assign(DIA = df_fechas['FECHA'].dt.day,MES=df_fechas['FECHA'].dt.month,ANIO=df_fechas['FECHA'].dt.year)              
            
            #Solo inserta la diferencia de fechas que estan en la bd
            if len(df_fechasBD) > 0:
                df_fechas['FECHA'] = pd.to_datetime(df_fechas['FECHA'])
                df_fechasBD['FECHA'] = pd.to_datetime(df_fechasBD['FECHA'])                
                df_fechas = pd.merge(df_fechas, df_fechasBD, how='left', indicator=True)
                df_fechas = df_fechas[df_fechas['_merge'] == 'left_only'].drop(columns=['_merge'])             
                
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
            print("Se insertaron los Datos de FECHAS Correctamente")

            sql_select = """ select * from fechas """
            df_fechasBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)
            
            #Retormamos el df
            return df_fechasBD
        
        except ValueError as err:
            print("Este es el error: "+err)
    
#Funcion que permite cargar los datos en la tabla de movimientos de Subte
    def insertTablaMovSubte(self,i_arraySubtes,i_arrayBocaSubtes,i_arrayFechas):
        #Variables
        sql_insert = """ insert into mov_subte(id_subte,id_fecha,hora,turno,cantidad) values(%s,%s,%s,%s,%s) """
        v_array = []

        #consulta a la base de datos y retorna los datos de la base
        sql_select = """ select id_subte as ID_SUBTE, id_fecha as ID_FECHA, hora as HORA, turno as TURNO, cantidad as CANT from mov_subte """
        df_movSubteBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)

        #Tratamos los datos de los movimientos de vehiculos y subtes para guardar las ubicaciones
        df_tlbMovSubte = i_arraySubtes[["FECHA","DESDE","TURNO","LINEA","ESTACION","pax_TOTAL"]]
        df_tlbMovSubte = df_tlbMovSubte.sort_values(by=["LINEA","ESTACION"])
        df_tlbMovSubte.columns = ["FECHA","DESDE","TURNO","LINEA","ESTACION","CANT"]        
        
        #Merchamos la Fecha
        df_tlbFecha = i_arrayFechas[["id_fecha","fecha"]].copy()
        df_tlbFecha.columns = ["ID_FECHA","FECHA"]  
        df_tlbFecha['FECHA'] = pd.to_datetime(df_tlbFecha['FECHA']) 
        df_tlbMovSubte['FECHA'] = pd.to_datetime(df_tlbMovSubte['FECHA'])        
        df_tlbMovSubte = pd.merge(df_tlbMovSubte,df_tlbFecha,on=['FECHA'], how='inner')
        
        #Merchamos la linea y estacion
        df_tblBocaSubtes = i_arrayBocaSubtes[["id_subte","linea","estacion"]]
        df_tblBocaSubtes.columns = ["ID_SUBTE","LINEA","ESTACION"]  
        df_tlbMovSubte['ESTACION'] = df_tlbMovSubte['ESTACION'].str.upper()
        df_tlbMovSubte = pd.merge(df_tlbMovSubte,df_tblBocaSubtes,on=["LINEA","ESTACION"], how='inner')

        #Solo inserta la diferencia de fechas que estan en la bd
        if len(df_movSubteBD) > 0:             
            df_tlbMovSubte = df_tlbMovSubte[["ID_SUBTE","ID_FECHA","DESDE","TURNO","CANT"]]             
            df_tlbMovSubte = pd.merge(df_tlbMovSubte, df_movSubteBD, how='left', indicator=True)
            df_tlbMovSubte = df_tlbMovSubte[df_tlbMovSubte['_merge'] == 'left_only'].drop(columns=['_merge'])
        
                       
        # Se recorre el df y se pasa a un arreglo para insertarlo en la tabla
        for i in range(len(df_tlbMovSubte)):
            v_array.append((int(df_tlbMovSubte.iloc[i]['ID_SUBTE']),                            
                            int(df_tlbMovSubte.iloc[i]['ID_FECHA']),
                            df_tlbMovSubte.iloc[i]['DESDE'],
                            df_tlbMovSubte.iloc[i]['TURNO'],
                            int(df_tlbMovSubte.iloc[i]['CANT'])
                        ))

        try:
            self.v_conexion.execQueryArray(queryParams=sql_insert,paramsArray=v_array)
            self.v_conexion.commit()

            #Log
            print("Se insertaron los Datos de MOV SUBTES Correctamente")

            #consulta a la base de datos y retorna los datos de la base
            sql_select = """ select id_subte as ID_SUBTE, id_fecha as ID_FECHA, hora as HORA, turno as TURNO, cantidad as CANT from mov_subte """
            df_movSubteBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)
            
            #Retormamos el df
            return df_movSubteBD
        
        except ValueError as err:
            print("Este es el error: "+err) 

#Funcion que permite cargar los datos en la tabla de movimientos de vehiculos
    def insertTablaMovVehiculo(self,i_arrayVehiculos,i_arrayUbicacion,i_arrayFechas):
        #Variables
        sql_insert = """ insert into mov_vehiculo(id_ubicacion,id_fecha,hora,cantidad) values(%s,%s,%s,%s) """
        v_array = []

        #consulta a la base de datos y retorna los datos de la base
        sql_select = """ select id_ubicacion as ID_UBICACION, id_fecha ID_FECHA, hora HORA, cantidad CANTIDAD from mov_vehiculo """
        df_tlbMovVehiBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)

        #Tratamos los datos de los movimientos de vehiculos y subtes para guardar las ubicaciones
        df_tlbMovVehi = i_arrayVehiculos[["FECHA","HORA","CANTIDAD","LATITUD","LONGITUD"]].copy()        

        #Merchamos la Fecha
        df_tlbFecha = i_arrayFechas[["id_fecha","fecha"]].copy()
        df_tlbFecha.columns = ["ID_FECHA","FECHA"]  
        df_tlbFecha['FECHA'] = pd.to_datetime(df_tlbFecha['FECHA']) 
        df_tlbMovVehi['FECHA'] = pd.to_datetime(df_tlbMovVehi['FECHA'])        
        df_tlbMovVehi = pd.merge(df_tlbMovVehi,df_tlbFecha,on=['FECHA'], how='inner')   

        #Merchamos las coordenadas
        i_arrayUbicacion["LATITUD"] = pd.to_numeric(i_arrayUbicacion["LATITUD"], errors='coerce')
        i_arrayUbicacion["LONGITUD"] = pd.to_numeric(i_arrayUbicacion["LONGITUD"], errors='coerce')        
        df_tlbMovVehi = pd.merge(df_tlbMovVehi,i_arrayUbicacion,on=['LATITUD', 'LONGITUD'], how='inner') 

        #Solo inserta la diferencia de fechas que estan en la bd
        if len(df_tlbMovVehiBD) > 0:             
            df_tlbMovVehi = df_tlbMovVehi[["ID","ID_FECHA","HORA","CANTIDAD"]]             
            df_tlbMovVehi = pd.merge(df_tlbMovVehi, df_tlbMovVehiBD, how='left', indicator=True)
            df_tlbMovVehi = df_tlbMovVehi[df_tlbMovVehi['_merge'] == 'left_only'].drop(columns=['_merge'])   
        
        #Se recorre el df y se pasa a un arreglo para insertarlo en la tabla
        for i in range(len(df_tlbMovVehi)):
            v_array.append((int(df_tlbMovVehi.iloc[i]['ID']),                            
                            int(df_tlbMovVehi.iloc[i]['ID_FECHA']),
                            df_tlbMovVehi.iloc[i]['HORA'],
                            int(df_tlbMovVehi.iloc[i]['CANTIDAD'])
                        ))

        try:
            self.v_conexion.execQueryArray(queryParams=sql_insert,paramsArray=v_array)
            self.v_conexion.commit()

            #Log
            print("Se insertaron los Datos de MOV VEHICULOS Correctamente")

            #consulta a la base de datos y retorna los datos de la base
            sql_select = """ select id_ubicacion as ID_UBICACION, id_fecha ID_FECHA, hora HORA, cantidad CANTIDAD from mov_vehiculo """
            df_tlbMovVehiBD = pd.read_sql_query(sql_select,self.v_conexion.connAlchemy)
            
            #Retormamos el df
            return df_tlbMovVehiBD
        
        except ValueError as err:
            print("Este es el error: "+err)
       
            