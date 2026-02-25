import os

from dotenv import load_dotenv
import psycopg2

load_dotenv()

import psycopg2

# Установка соединения с PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

cursor = conn.cursor()
named_cursor = conn.cursor(name="my_cursor")
dict_cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)   

print(f"PostgreSQL params: {conn.get_dsn_parameters()}")

conn.close()

