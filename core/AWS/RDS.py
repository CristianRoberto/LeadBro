import os

import mysql.connector as conn

from dotenv import load_dotenv

import _mysql_connector
# dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv()


class connection:
    cursor = None
    count = 0

    def __init__(self) -> None:
        self.connector = None
        self.credentials = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_DATABASE'),
        }

        db_port = os.getenv('DB_PORT')
        if db_port:
            self.credentials['port'] = db_port
            

    def connect(self):
         try:
              self.connector = conn.connect(**self.credentials)
              connection.cursor = self.connector.cursor()
         except conn.Error as e:
          print(f"Error al conectar a la base de datos: {e}")
    
    def is_connected(self):
        return connection.cursor is not None
   
    
    

    def __enter__(self):
        if connection.cursor is None:
            self.connector = conn.connect(**self.credentials)
            connection.cursor = self.connector.cursor()
        connection.count += 1
        return connection.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        connection.count -= 1
        if connection.count == 0:
            if self.connector is not None:
               if exc_tb is None:
                self.connector.commit()
               else:
                print(exc_type, exc_val, exc_tb)
                self.connector.rollback()
                connection.cursor.close()
                self.connector.close()
            connection.cursor = None

db = connection()
db.connect()
print(db.is_connected())  # Debería imprimir True si la conexión fue exitosa