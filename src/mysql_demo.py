import os
import pymysql

host = os.environ["MYSQL_HOST"]
port = int(os.environ["MYSQL_PORT"])
database = os.environ["MYSQL_DATABASE"]

print(host, port, database)

user = os.environ["MYSQL_USER"]
password = os.environ["MYSQL_PASSWORD"]

conn = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database,
    charset="utf8mb4",
)

print("MySQL连接成功")

cursor = conn.cursor()

cursor.execute(
    "INSERT INTO practice_tasks (id, title, status) VALUES (%s, %s, %s)",
    (2, "Python连接练习", "todo"),
)
conn.commit()

cursor.execute(
    "SELECT id, title, status FROM practice_tasks WHERE id = %s",
    (2,),
)
row = cursor.fetchone()
print(row)

cursor.close()
conn.close()