import mysql.connector

connection = mysql.connector.connect(
    host="db4free.net",
    user="jerrin23",
    password="9890614803",
    port="3306",
    database="college_database",
    ssl_disabled=True  # Disable SSL for the connection
)
print("Connected successfully without SSL!")