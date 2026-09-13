import psycopg2 as pgsql
from dotenv import load_dotenv
import os 


load_dotenv()

def connect_db():
    connection = pgsql.connect(os.environ["DATABASE_URL"])
    cursor = connection.cursor()
    return connection,cursor