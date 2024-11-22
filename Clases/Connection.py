import mysql.connector
from mysql.connector import errorcode
from sqlalchemy import create_engine

class Connection():
    USER = None
    PASS = None
    HOST = None
    DATABASE = None

    conn = None
    connAlchemy = None

    def __init__(self,USER,PASS,HOST,DATABASE):
        self.USER = USER
        self.PASS = PASS
        self.HOST = HOST
        self.DATABASE = DATABASE

        try:
            cnx = cnx = mysql.connector.connect(user=self.USER,
                                                password=self.PASS,
                                                host=self.HOST,
                                                database=self.DATABASE)
            cnx.autocommit = False

            #engine = create_engine('mysql+mysqlconnector://root:@localhost/mi_base_datos')
            #engine = create_engine('mysql+mysqlconnector://usuario:contraseña@host:puerto/base_datos')

            engine = create_engine(f'mysql+mysqlconnector://{self.USER}:{self.PASS}@{self.HOST}:3306/{self.DATABASE}')

            print("Conectado a BD")
            self.conn = cnx
            self.connAlchemy = engine

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Algo anda mal con su base de datos")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("La base de datos no existe")
            else:
                print(err)

    def execQuery(self,queryParams,params):
        try:
            cursor = self.conn.cursor()
            cursor.execute(queryParams,params)

        except ValueError as err:
            print("Este es el error: "+err)
        finally:
            self.cursor.close()
            print("Cursor (EQ) cerrado")               

    def execQueryArray(self,queryParams,paramsArray):
        try:
            cursor = self.conn.cursor()
            cursor.executemany(queryParams,paramsArray)

        except ValueError as err:
            print("Este es el error: "+err)
        finally:
            cursor.close()            
            print("Cursor (EQA) cerrado")            
    
    def execQuerySimple(self,query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query) 
            self.conn.commit()

        except ValueError as err:
            print("Este es el error: "+err)
        finally:
            cursor.close()      
            print("Cursor (EQS) cerrado")

    def commit(self):
        self.conn.commit()
    
    def connClose(self):
        self.conn.close()
        print("Conexion Cerrada")