import socket
import os
import mysql.connector
import pickle

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nintendopro1",
    database="FileData"
)


storages = {"pdf":"/Users/nhan/Desktop/COMP7212Project/Storage pdf/", 
            "docx":"/Users/nhan/Desktop/COMP7212Project/Storage docx/",
            "txt":"/Users/nhan/Desktop/COMP7212Project/Storage txt/"}

server_host ="0.0.0.0"
port = 1234

meta_server= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
meta_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
meta_server.bind((server_host,port))
meta_server.listen(5)
print("Welcome to the server")


def insertDatabase(info_list):
    mycursor = mydb.cursor()
    sql = "INSERT INTO file (file_name, file_format, file_location, user_gmail) VALUES (%s,%s,%s,%s)"
    val = (info_list[0],info_list[1],info_list[2], info_list[3])
    mycursor.execute(sql,val)
    mydb.commit()
    print("Inserted data into database sucessfully")
    return info_list[2]

def removeFile(info_list):
    mycursor=mydb.cursor()
    print(info_list[3]+" "+info_list[1]+" "+info_list[2]+"Hello")
    sql = "DELETE FROM file WHERE user_gmail= %s AND file_name =%s AND file_format= %s"
    mycursor.execute(sql,(info_list[3],info_list[0],info_list[1],))
    mydb.commit()

    


# Function to get the information of file to insert into database.
def getfileInfo(filedirectory):
    file_name_format = os.path.basename(filedirectory[1])
    file_format = file_name_format.split(".")[1]
    file_name = file_name_format.split(".")[0]
    
    user_gmail= filedirectory[2]
    file_location = storages.get(file_format)+user_gmail+"/"+file_name+"."+file_format
    info_list = [file_name,file_format,file_location,user_gmail]
    return info_list

def getFilesRequest(user_gmail):
    mycursor = mydb.cursor()
    sql= """SELECT * FROM file WHERE user_gmail= %s"""
    mycursor.execute(sql, (user_gmail,))
    record = mycursor.fetchall()
    file = []
    for row in record:
        file.append(row[1]+"."+row[2])
    return file

def getLinkofFile(info_list):
    mycursor=mydb.cursor()
    sql = "SELECT file_location FROM file WHERE user_gmail=%s AND file_name=%s AND file_format=%s"
    mycursor.execute(sql,(info_list[3],info_list[0],info_list[1],))
    record = mycursor.fetchone()
    link = record[0]
    return link
def getFileNameFormat(file_location):
    mycursor=mydb.cursor()
    sql = "SELECT file_name, file_format FROM file WHERE file_location=%s"
    mycursor.execute(sql,(file_location,))
    record=mycursor.fetchone()
    fileName = record[0]
    fileFormat=record[1]
    fileInfo=[fileName,fileFormat]
    return fileInfo






while True:
    connection, address = meta_server.accept()
    receiving_packet = connection.recv(1024)

    if not receiving_packet:
        break
    else:
        packet_received = pickle.loads(receiving_packet)

        # command  is assigned = packet_received[]
        if packet_received[0]=="upload":
            info_list = getfileInfo(packet_received)
            link_file = insertDatabase(info_list)
            message = "Link to your file: "+link_file 
            connection.send(message.encode('utf-8'))
        
        elif packet_received[0]=="requestFiles":
            file = getFilesRequest(packet_received[1])
            packet = pickle.dumps(file)
            connection.send(packet)
        
        elif packet_received[0]=="delete":
            print("delete")
            info_list = getfileInfo(packet_received)
            print(info_list[0]+" "+info_list[1])
            removeFile(info_list)
        elif packet_received[0]=="getlink":
            print("getlink")
            info_list = getfileInfo(packet_received)
            link = getLinkofFile(info_list)
            connection.send(link.encode())
        elif packet_received[0]=="getFileName":
            print("Get file name")
            fileInfo=pickle.dumps(getFileNameFormat(packet_received[1]))
            connection.send(fileInfo)

    
        




