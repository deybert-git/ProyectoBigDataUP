import mysql.connector
from mysql.connector import errorcode

class Connection():
    USER = None
    PASS = None
    HOST = None
    DATABASE = None

    conn = None

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

            print("Conectado a BD")
            self.conn = cnx

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Algo anda mal con su base de datos")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("La base de datos no existe")
            else:
                print(err)

    def execQuery(self,queryParams,params):
        cursor = self.conn.cursor()
        cursor.execute(queryParams,params)

    def execQueryArray(self,queryParams,paramsArray):
        cursor = self.conn.cursor()
        cursor.executemany(queryParams,paramsArray)
    
    def execQuerySimple(self,query):
        cursor = self.conn.cursor()
        cursor.execute(query) 
        self.conn.commit()

    def commit(self):
        self.conn.commit()