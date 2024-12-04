import pandas as pd
#import numpy as np
#import json
#import chardet
#import pygeohash as pygeo
from unidecode import unidecode
import re
import os
import shutil
from pathlib import Path
import chardet
import csv

class ParserData():

#declaracion de variables
    v_conexion = None
    v_file = None

#declaracion de construcctor vacio
    # def __init__(self):
    #    print("Iniciada la Clase Vacia")

# Funcion para quitar acentos y caracteres especiales
    def limpiar_texto(texto):
        if isinstance(texto, str):  # Verifica si es una cadena
            texto = unidecode(texto)  # Eliminar acentos
            texto = re.sub(r'[^A-Za-z0-9\s]', '', texto)  # Eliminar caracteres especiales            
        return texto
    
# Funcion que permite encontrar el encoding de un archivo
    def detectar_encoding(self,file_path):
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            encoding_detected = result['encoding']
        return encoding_detected

# Funcion que permite identificar el separador de un archivo    
    def detectar_separador(self,file_path, encoding_detected):
        with open(file_path, 'r', encoding=encoding_detected) as f:
            sample = f.read(1024)  # Leer una muestra del archivo
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
        return delimiter

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

            #rellena los valores nulos con los datos mas cercanos
            #df = df.fillna(method='ffill').fillna(method='bfill')  
            
            #rellena los valores nulos con la media
            #df = df.fillna(df.mean())

            #rellena los valores nulos con ceros
            #df = df.fillna(0)

            #rellena los valores nulos con un valor nulo de la libreria
            #df = df.replace("", np.nan)
         
        #elimina caracteres espciales y acentos
        df = df.apply(ParserData.limpiar_texto) 

        #retornamos el dataFrame
        return df

#funcion para leer y limpiar el archivo csv, limpia solo filas con datos nulos
    def readDataFlujoSubte(self,ruta): 
        #Declaro variables
        dataframe = []        

        #Se valida que los directorios existan
        directorioOrg = Path(ruta+"/Limpios")
        directorioProc = Path(ruta+"/Procesados")

        if (not directorioOrg.exists()) and (not directorioOrg.is_dir()):
            raise ValueError("Directorio Originales no Existe")
        
        if (not directorioProc.exists()) and (not directorioProc.is_dir()):
            raise ValueError("Directorio Procesados no Existe")
        
        #Se leen los arvhivos .csv del directorio que contienen el texto PAX15
        texto_archivos = "PAX15"
        #texto_archivos = "archivo_limp"

        for file_name in os.listdir(directorioOrg):
            if texto_archivos in file_name and file_name.endswith(".csv"):
                file_path = os.path.join(directorioOrg, file_name)

                # Detectar codificación
                encoding_detectado = self.detectar_encoding(file_path)

                # Detectar delimitador
                delimitador_detectado = self.detectar_separador(file_path,encoding_detectado)              
                
                df = pd.read_csv(file_path, encoding=encoding_detectado,sep=delimitador_detectado)  
                dataframe.append(df)

                # Mover el archivo al directorio de procesados
                #new_path = os.path.join(directorioProc, file_name)
                #shutil.move(file_path, new_path)
        
        # Unir todos los DataFrames
        if dataframe:                   
            final_dataframe = pd.concat(dataframe, ignore_index=True)                  

        #elimina filas con datos en nulo
        #final_dataframe = final_dataframe.dropna(axis=0)

        #elomina columnas con datos en nulo
        #final_dataframe = final_dataframe.dropna(axis=1) 

        #elimina caracteres espciales y acentos
        final_dataframe = final_dataframe.apply(ParserData.limpiar_texto)      

        #retornamos el dataFrame
        return final_dataframe
    
#funcion para leer y limpiar el archivo csv
    def LimpiarCSV(self,ruta): 
        #Se valida que los directorios existan
        directorioOrg = Path(ruta+"/Originales")
        directorioProc = Path(ruta+"/Limpios/")

        if (not directorioOrg.exists()) and (not directorioOrg.is_dir()):
            raise ValueError("Directorio Originales no Existe")
        
        if (not directorioProc.exists()) and (not directorioProc.is_dir()):
            raise ValueError("Directorio Procesados no Existe")
        
        #Se leen los arvhivos .csv del directorio que contienen el texto PAX15
        texto_archivos = "PAX15"        

        for file_name in os.listdir(directorioOrg):
            if texto_archivos in file_name and file_name.endswith(".csv"):
                file_path = os.path.join(directorioOrg, file_name)

                # Detectar codificación
                encoding_detectado = self.detectar_encoding(file_path)

                # Detectar delimitador
                delimitador_detectado = self.detectar_separador(file_path,encoding_detectado)              
                
                df = pd.read_csv(file_path, encoding=encoding_detectado,sep=delimitador_detectado)  
                df = df.dropna()
                df = df.apply(ParserData.limpiar_texto)

                new_path = os.path.join(directorioProc, file_name)
                df.to_csv(new_path, index=False, sep=',', encoding='utf-8')     

                print("Archivo ",file_name," Guardado Correctamente")        

        #retornamos el dataFrame
        #return "Archivos Limpios guardados correctamente"