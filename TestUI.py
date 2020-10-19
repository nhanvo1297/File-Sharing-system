import tkinter as tk
import socket
import select
import errno
import sys
import pickle
from threading import Thread
from tkinter import filedialog
import os
import tqdm



def login():
    global username 
    username= entry.get()
    label_file_explorer.configure(text="Logged In with username: "+username)
def browseFiles():

    global filename
    filename = filedialog.askopenfilename(initialdir = "/", 
                                          title = "Select a File", 
                                          filetypes = (("Text files", 
                                                        "*.pdf"),("Text files",
                                                        "*.txt"),
                                                        ("Text files",
                                                        "*.docx"),
                                                       ("all files", 
                                                        "*.*")))  
       
    label_file_explorer.configure(text="File opened: "+filename)
    

def uploadFiles():
    IP = ''
    PROCESSING_SERVER_PORT = 5001
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, PROCESSING_SERVER_PORT))

    # this is the original file directory of the file
    file_directory = filename
    filesize = os.path.getsize(filename);
    command = "upload"
    #Sending file to processing server
    client_socket.send(f"{username}{SEPARATOR}{command}{SEPARATOR}{filename}{SEPARATOR}{filesize}".encode())

    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        for _ in progress:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
           # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            client_socket.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    # close the socket
    #client_socket.close()

    META_SERVER_PORT = 1234
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, META_SERVER_PORT))

    packet = ["upload",file_directory, username]
    sending_packet = pickle.dumps(packet)

    client_socket.send(sending_packet)

    message = client_socket.recv(1024)
    print(message.decode('utf-8'))   

    label_file_explorer.configure(text="File uploaded sucessfully: "+filename)
    



def requestFiles():
    IP = ''
    META_SERVER_PORT = 1234
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, META_SERVER_PORT))

    packet = ["requestFiles", username,""]
    sending_packet = pickle.dumps(packet)

    client_socket.send(sending_packet)

    message = client_socket.recv(1024)
    files = pickle.loads(message)
    text.delete(0,'end')
    for file in files:
        text.insert(0,file)

    label_file_explorer.configure(text="Your files are updated")
    

def deleteFiles():
    # Notify meta server to delete file
    SEPARATOR = "<SEPARATOR>"
    
    IP = ""
    PROCESSING_SERVER_PORT = 5001
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, PROCESSING_SERVER_PORT))
    command = "delete"
    
    file_selected = text.get(text.curselection())
    label_file_explorer.configure(text="Selected: "+file_selected)
    filesize=""
    client_socket.send(f"{username}{SEPARATOR}{command}{SEPARATOR}{file_selected}{SEPARATOR}{filesize}".encode())

    # notify meta server to remove file
    META_SERVER_PORT = 1234
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, META_SERVER_PORT))

    packet = ["delete",file_selected, username]
    sending_packet = pickle.dumps(packet)
    client_socket.send(sending_packet)

    label_file_explorer.configure(text="Your file has been deleted")


   
def downloadFile():
    SEPARATOR = "<SEPARATOR>"
    IP = ""
    BUFFER_SIZE = 4096
    META_SERVER_PORT = 1234
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, META_SERVER_PORT))

    file_selected = text.get(text.curselection())
    label_file_explorer.configure(text="Selected: "+file_selected)

    packet = ["getlink",file_selected, username]
    sending_packet = pickle.dumps(packet)
    client_socket.send(sending_packet)
    file_location = client_socket.recv(1024).decode()

    # send file location to processing to dơưnload file


    PROCESSING_SERVER_PORT = 5001
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, PROCESSING_SERVER_PORT))
    command = "download"
    filesize = os.path.getsize(file_location)
    client_socket.send(f"{file_location}{SEPARATOR}{command}{SEPARATOR}{file_selected}{SEPARATOR}{filesize}".encode())
    path="/Users/nhan/Desktop/COMP7212Project/Storage of Client/"
    final_filename = os.path.join(path,file_selected)

    
    with open(final_filename, "wb") as f:
        while True:
            data=client_socket.recv(4096)
            if not data:
                break
            f.write(data)

    f.close()
    client_socket.shutdown(1)
    label_file_explorer.configure(text="Downloaded: "+file_selected+"check your download folder.")
                    



def getFileLink():
    SEPARATOR = "<SEPARATOR>"
    IP = ""
    META_SERVER_PORT = 1234
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, META_SERVER_PORT))

    file_selected = text.get(text.curselection())
    label_file_explorer.configure(text="Selected: "+file_selected)

    packet = ["getlink",file_selected, username]
    sending_packet = pickle.dumps(packet)
    client_socket.send(sending_packet)
    link = client_socket.recv(1024).decode()

    entry1.delete(0,'end')
    entry1.insert(0,link)

def downloadFileFromLink():
    SEPARATOR = "<SEPARATOR>"
    IP = ""

    file_location = entry1.get()

    META_SERVER_PORT = 1234
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, META_SERVER_PORT))
    packet = ["getFileName",file_location, "none"]
    sending_packet = pickle.dumps(packet)
    client_socket.send(sending_packet)

    fileInfo = client_socket.recv(1024)
    final_fileInfo = pickle.loads(fileInfo)
    file_name=final_fileInfo[0]
    file_format=final_fileInfo[1]
    label_file_explorer.configure(text="Downloading file: "+file_name)
    
    PROCESSING_SERVER_PORT = 5001
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((IP, PROCESSING_SERVER_PORT))
    file_selected=""
    filesize=""
    command="downloadFromLink"
    client_socket.send(f"{file_location}{SEPARATOR}{command}{SEPARATOR}{file_selected}{SEPARATOR}{filesize}".encode())
    path="/Users/nhan/Desktop/COMP7212Project/Storage of Client/"
    final_filename = os.path.join(path,file_name+"."+file_format)

    with open(final_filename, "wb") as f:
        while True:
            data=client_socket.recv(4096)
            if not data:
                break
            f.write(data)

    f.close()
    client_socket.shutdown(1)

top = tk.Tk()
top.title("File Distributed System")
top.geometry("600x700")
top.resizable(width=False, height = False)
top.configure(bg='alice blue')

label_file_explorer = tk.Label(top, text ="Welcome to File Distributed System",width = 54, height =4, fg ="blue",bg= 'alice blue')
label_file_explorer.grid(row=0,columnspan=2,padx=(0,0),pady=(5,40))
label = tk.Label(top,width=10,text="Username:",fg="Gray25",font="Verdana 13 bold",bg='light sky blue')
label.grid(row=0,column=0,padx=(0,250),ipadx=2,pady=(50,5))
entry = tk.Entry(top, width = 22)
entry.grid(row=0,column=0, ipadx=20, padx=(100,0), pady=(50,5))
button =tk.Button(top, width=10, text="Log In", fg="#3578e5", font = 'Verdana 13 bold', command =login)
button.grid(row=0,column=1, pady=(50,5),padx=(10,10))

text = tk.Listbox(top, width=40,height=25, bg='white',highlightcolor='blue')
text.grid(row=1, column=0,pady=(50,10),padx=(30,10))
button1 =tk.Button(top, width=13,height=2,text="Browse", fg="RoyalBlue1",font = 'Times 15 bold',bg='SteelBlue1', command = browseFiles)
button2 =tk.Button(top, width=13,height=2,text="Upload", fg="RoyalBlue2",font = 'Times 15 bold', command = uploadFiles)
button3 =tk.Button(top, width=13,height=2,text="Delete", fg="RoyalBlue3",font = 'Times 15 bold',command = deleteFiles)
button4 =tk.Button(top, width=13,height=2,text="Request Files", fg="DeepSkyBlue2",font = 'Times 15 bold', command = requestFiles)
button5 =tk.Button(top, width=13,height=2,text="Download File", fg="DeepSkyBlue3",font = 'Times 15 bold', command = downloadFile)
button6 =tk.Button(top, width=13,height=2,text="Get Link", fg="DeepSkyBlue3",font = 'Times 15 bold', command = getFileLink)
button1.grid(row=1,column=1, pady=(0,350), padx=(18,5))
button2.grid(row=1,column=1, pady=(5,270), padx=(18,5))
button3.grid(row=1,column=1, pady=(10,190),padx=(18,5))
button4.grid(row=1,column=1, pady=(15,110),padx=(18,5))
button5.grid(row=1,column=1, pady=(75,80),padx=(18,5))
button6.grid(row=1,column=1, pady=(165,83),padx=(18,5))

download_link_label =tk.Label(top, width=20, text="Download file from link", fg='blue',bg='light sky blue')
download_link_label.grid(row=2, column=0)

entry1 =tk.Entry(top,width = 40)
entry1.grid(row=3,column=0)
button_download = tk.Button(top, width=10, text="Download", fg="#3578e5", font = 'Verdana 13 bold',command=downloadFileFromLink)
button_download.grid(row=3,column=1)


top.mainloop()