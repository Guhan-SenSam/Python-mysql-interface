import mysql.connector
mydb = mysql.connector.connect(
     host = "localhost",
     user = "root",
     passwd = "Guhan",
     
     )
print(mydb) 

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

for db in mycursor:
    print(db)
 
 