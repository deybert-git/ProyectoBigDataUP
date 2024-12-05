import pandas as pd
from unidecode import unidecode
import os
from pathlib import Path
import chardet
import csv
import unicodedata
from Clases.ParserDataBD import ParserDataBD

class ParserData():

#declaracion de variables
    v_conexion = None
    v_file = None

#declaracion de construcctor vacio
    # def __init__(self):
    #    print("Iniciada la Clase Vacia")

# Funcion para quitar espacios, tabulaciones y saltos de linea a las columnas de texto
    def limpiar_columnas_texto(self,i_dataFrame):
        # Se respalda el DataFrame
        df_limpio = i_dataFrame

        # Identificar columnas de tipo string
        columnas_string = i_dataFrame.select_dtypes(include='object').columns       

        # Opciones de Limpieza
        # Quita espacios
        df_limpio[columnas_string] = df_limpio[columnas_string].apply(lambda col: col.str.strip())

        # Quita caracteres como tabulador o saldo de linea 
        df_limpio[columnas_string] = df_limpio[columnas_string].apply(lambda col: col.str.replace(r'^[\t\n ]+|[\t\n ]+$', '', regex=True))
        #df_limpio[columnas_string] = df_limpio[columnas_string].apply(lambda col: col.str.replace(r'^\s+|\s+$|^[\t\n ]+|[\t\n ]+$', '', regex=True))

        return df_limpio

# Otra Funcion para quitar acentos y caratteres especiales
    def quitar_acentos(self,texto):
        if isinstance(texto, str):  # Solo procesar si es string
            # Normalizar el texto a forma NFKD
            texto_normalizado = unicodedata.normalize('NFKD', texto)
            # Eliminar caracteres no ASCII (acentos y caracteres especiales)
            texto_sin_acento = texto_normalizado.encode('ascii', 'ignore').decode('utf-8')
            return texto_sin_acento
        return texto  # Devolver el valor original si no es string

# Otra Funcion para quitar acentos y caratteres especiales por columnas
    def quitar_columnas_acento(self,i_dataFrame):
        # Se respalda el DataFrame
        df_limpio = i_dataFrame

        # Identificar columnas de tipo string
        columnas_string = i_dataFrame.select_dtypes(include='object').columns

        # Aplica la función Quitar Acentos a las columnas de tipo string
        df_limpio[columnas_string] = df_limpio[columnas_string].apply(lambda col: col.map(self.quitar_acentos))

        return df_limpio
    
# Funcion que permite encontrar el encoding de un archivo
    def detectar_encoding(self,file_path):     
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            encoding_detected = result['encoding']
        return encoding_detected
        
# Funcion que permite identificar el separador de un archivo    
    def detectar_separador(self,file_path, encoding_detected):
        delimiter = ","
        try: 
            with open(file_path, 'r', encoding=encoding_detected) as f:
                sample = f.read(1024)  # Leer una muestra del archivo
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
            return delimiter
        except:
            return delimiter

#funcion para leer un archivo y devolverlo en un dataframe
    def readCSV(self,i_ruta,i_file):
        #Directorio
        file_path = os.path.join(i_ruta, i_file)

        #Lectura del archivo
        df = pd.read_csv(file_path, sep=',', encoding='utf-8')

        #retornamos el dataFrame
        return df

#funcion para leer y limpiar los archivos csv y unificarlos en 1
    def read_data_join(self,i_ruta,i_textFileName): 
        #Declaro variables
        dataframe = []        

        #Se valida que los directorios existan
        directorioOrg = Path(i_ruta+"/Limpios")
        directorioProc = Path(i_ruta+"/Procesados")

        if (not directorioOrg.exists()) and (not directorioOrg.is_dir()):
            raise ValueError("Directorio Originales no Existe")
        
        if (not directorioProc.exists()) and (not directorioProc.is_dir()):
            raise ValueError("Directorio Procesados no Existe")
        
        #Se leen los arvhivos .csv del directorio que contienen el texto pasado por parametro
        texto_archivos = i_textFileName
        
        for file_name in os.listdir(directorioOrg):
            if texto_archivos in file_name and file_name.endswith(".csv"):
                file_path = os.path.join(directorioOrg, file_name)
                
                # Detectar codificación
                encoding_detectado = self.detectar_encoding(file_path)
                
                # Detectar delimitador
                delimitador_detectado = self.detectar_separador(file_path,encoding_detectado)              
                
                df = pd.read_csv(file_path, encoding=encoding_detectado,sep=delimitador_detectado)  
                dataframe.append(df)                 
        
        # Unir todos los DataFrames
        if dataframe:                   
            final_dataframe = pd.concat(dataframe, ignore_index=True)     

        #Se crea una nueva columna con la linea de metro en letra
        if i_textFileName == "PAX15":        
            final_dataframe['LINEA_L'] = final_dataframe['LINEA'].str[-1:]  

        #Limpieza de valores nulos
        if i_textFileName != "bocas-de-subte":
            # elimina los registros con valores nulos
            final_dataframe = final_dataframe.dropna() 
        else:            
            #rellena los valores nulos con los datos mas cercanos -- Solo para las bocas de subte--
            final_dataframe = final_dataframe.ffill().bfill()  
        
        #Se limpian las columnas de texto
        final_dataframe = self.limpiar_columnas_texto(final_dataframe.copy())
        
        # Se quitan los acentos
        final_dataframe = self.quitar_columnas_acento(final_dataframe.copy()) 
        
        # Se guardan los archivos      
        self.saveCSV(final_dataframe,directorioProc,i_textFileName+"_prc.csv")
        
          
#funcion para Leer los archivos limpios de movimientos y guardar
    def read_data_batch(self,i_ruta,i_textFileName): 
        #Se valida que los directorios existan
        directorioOrg = Path(i_ruta+"/Limpios/")
        directorioDest = Path(i_ruta+"/Procesados/")

        if (not directorioOrg.exists()) and (not directorioOrg.is_dir()):
            raise ValueError("Directorio Originales no Existe")
        
        if (not directorioDest.exists()) and (not directorioDest.is_dir()):
            raise ValueError("Directorio Procesados no Existe")
        
        #Se leen los arvhivos .csv del directorio que contienen el texto pasado por parametro
        texto_archivos = i_textFileName
        cont = 0
        
        for file_name in os.listdir(directorioOrg):
            if texto_archivos in file_name and file_name.endswith(".csv"):
                file_path = os.path.join(directorioOrg, file_name)
                cont += 1

                # Detectar codificación
                encoding_detectado = self.detectar_encoding(file_path)

                # Detectar delimitador
                delimitador_detectado = self.detectar_separador(file_path,encoding_detectado)              
                
                #Leemos el csv
                df = pd.read_csv(file_path, encoding=encoding_detectado,sep=delimitador_detectado)                             

                if not df.empty:
                    # elimina los registros con valores nulos            
                    df = df.dropna() 
                    
                    #Se limpian las columnas de texto
                    df = self.limpiar_columnas_texto(df.copy())

                    # Se quitan los acentos
                    df = self.quitar_columnas_acento(df.copy()) 
                    
                    #Condiciones para los arvhivos de mov de subte
                    if i_textFileName == "PAX15":        
                        df['LINEA_L'] = df['LINEA'].str[-1:]                        

                        #Se homologa los nombres de las bocas de subte
                        self.homologaBocasSubte(df)                     

                    #Se guarda el df en el directorio procesados
                    self.saveCSV(df,directorioDest,file_name[:-4]+"_prc_"+str(cont)+".csv")                    
                    
    
#funcion para leer y limpiar los archivos originales y depositarlos en el directorio limpios
    def clean_data_batch(self,ruta): 
        #Se valida que los directorios existan
        directorioOrg = Path(ruta+"/Originales/")
        directorioDest = Path(ruta+"/Limpios/")

        if (not directorioOrg.exists()) and (not directorioOrg.is_dir()):
            raise ValueError("Directorio Originales no Existe")
        
        if (not directorioDest.exists()) and (not directorioDest.is_dir()):
            raise ValueError("Directorio Procesados no Existe")
        
        #Se recorren 1 a 1 los archivos que esten dentro del directorio Org
        for file_name in os.listdir(directorioOrg):
            if file_name.endswith(".csv"):
                file_path = os.path.join(directorioOrg, file_name)

                # Detectar codificación
                encoding_detectado = self.detectar_encoding(file_path)

                # Detectar delimitador
                delimitador_detectado = self.detectar_separador(file_path,encoding_detectado)              
                
                df = pd.read_csv(file_path, encoding=encoding_detectado,sep=delimitador_detectado) 

                #Limpieza de valores nulos
                if file_name != "bocas-de-subte.csv":
                    # elimina los registros con valores nulos
                    df = df.dropna() 
                else:
                    #rellena los valores nulos con los datos mas cercanos -- Solo para las bocas de subte--
                    df = df.ffill().bfill()

                #rellena los valores nulos con un valor nulo de la libreria 
                #df = df.replace("", np.nan)              

                new_path = os.path.join(directorioDest, file_name)
                df.to_csv(new_path, index=False, sep=',', encoding='utf-8')     

                print("Archivo ",file_name," Guardado Correctamente")        

#Funcion para guardar archivos en una ruta partiendo de un dataframe
    def saveCSV(self,i_dataFrame,i_ruta,i_nombre):
        new_path = os.path.join(i_ruta, i_nombre)
        i_dataFrame.to_csv(new_path, index=False, sep=',', encoding='utf-8')
        print("Archivo ",i_nombre," guardado correctamente.")

#Funcion que homologa las Bocas de Subte del Archivo de movimientos subte contra el de subtes
    def homologaBocasSubte(self,i_dataFrame):
        df_homologa = i_dataFrame
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('9 de julio','9 DE JULIO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Acoyte','ACOYTE')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Agoero','AGUERO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Aguero','AGUERO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Alberti','ALBERTI')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Medrano','ALMAGRO - MEDRANO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Angel Gallardo','ANGEL GALLARDO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Avenida de Mayo','AV. DE MAYO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Avenida La Plata','AV. LA PLATA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('General Belgrano','BELGRANO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Boedo','BOEDO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Bolivar','BOLIVAR')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Bulnes','BULNES')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Carlos Pellegrini','C. PELLEGRINI')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Callao','CALLAO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Callao.B','CALLAO - MAESTRO ALFREDO BRAVO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Carabobo','CARABOBO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Carlos Gardel','CARLOS GARDEL')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Caseros','CASEROS')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Castro Barros','CASTRO BARROS')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Catalinas','CATALINAS')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Catedral','CATEDRAL')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Congreso','CONGRESO - PDTE. DR. RAUL ALFONSIN')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Congreso de Tucuman','CONGRESO DE TUCUMAN')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Constitucion','CONSTITUCION')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Cordoba','CORDOBA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Correo Central','CORREO CENTRAL')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Corrientes','CORRIENTES')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Los Incas','DE LOS INCAS - PQUE. CHAS')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Diagonal Norte','DIAGONAL NORTE')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Dorrego','DORREGO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Echeverria','ECHEVERRIA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Emilio Mitre','EMILIO MITRE')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Entre Rios','ENTRE RIOS - RODOLFO WALSH')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Facultad de Derecho','FACULTAD DE DERECHO - JULIETA LANTERI')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Facultad de Medicina','FACULTAD DE MEDICINA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Federico Lacroze','FEDERICO LACROZE')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Florida','FLORIDA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('General San Martin','SAN MARTIN')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Hospitales','HOSPITALES')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Humberto I','HUMBERTO 1')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Inclan','INCLAN - MEZQUITA AL AHMAD')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Independencia','INDEPENDENCIA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Independencia.H','INDEPENDENCIA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Jose Hernandez','JOSE HERNANDEZ')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Jose Maria Moreno','JOSE MARIA MORENO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Rosas','JUAN MANUEL DE ROSAS - VILLA URQUIZA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Jujuy','JUJUY')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Juramento','JURAMENTO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Las Heras','LAS HERAS')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Lavalle','LAVALLE')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Leandro N. Alem','LEANDRO N. ALEM')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Lima','LIMA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Loria','LORIA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Malabia','MALABIA - OSVALDO PUGLIESE')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Medalla Milagrosa','MEDALLA MILAGROSA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Ministro Carranza','MINISTRO CARRANZA - MIGUEL ABUELO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Mariano Moreno','MORENO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Olleros','OLLEROS')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Once','ONCE - 30 DE DICIEMBRE')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Palermo','PALERMO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Patricios','PARQUE PATRICIOS')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Pasco','PASCO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Pasteur','PASTEUR - AMIA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Peru','PERU')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Pichincha','PICHINCHA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Piedras','PIEDRAS')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Plaza de Mayo','PLAZA DE MAYO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Plaza Italia','PLAZA ITALIA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Plaza Miserere','PLAZA MISERERE')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Primera Junta','PRIMERA JUNTA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Puan','PUAN')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Pueyrredon','PUEYRREDON')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Pueyrredon.D','PUEYRREDON')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Pza. de los Virreyes','PLAZA DE LOS VIRREYES - EVA PERON')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Retiro','RETIRO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Retiro E','RETIRO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Rio de Janeiro','RIO DE JANEIRO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Saenz Pea','SAENZ PENA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Saenz Pena','SAENZ PENA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('San Jose','SAN JOSE')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Flores','SAN JOSE DE FLORES')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('San Juan','SAN JUAN')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('San Pedrito','SAN PEDRITO')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Santa Fe','SANTA FE - CARLOS JAUREGUI')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Scalabrini Ortiz','R.SCALABRINI ORTIZ')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Tribunales','TRIBUNALES - TEATRO COLON')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Tronador','TRONADOR - VILLA ORTUZAR')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Urquiza','URQUIZA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Uruguay','URUGUAY')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Varela','VARELA')
        df_homologa['ESTACION'] = df_homologa['ESTACION'].replace('Venezuela','VENEZUELA')
        return df_homologa