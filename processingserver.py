import socket
import tqdm
import os
import os.path






def getPath(file_format):
    save_path = {".pdf":"/Users/nhan/Desktop/COMP7212Project/Storage pdf/",
                ".docx":"/Users/nhan/Desktop/COMP7212Project/Storage docx/",
                ".txt":"/Users/nhan/Desktop/COMP7212Project/Storage txt/"}
    
    path = save_path[file_format]
    return path


SERVER_HOST ="0.0.0.0"
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

s=socket.socket()
s.bind((SERVER_HOST,SERVER_PORT))
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

while True:

    client_socket, address = s.accept()
    print(f"[+] {address} is connected.")
    received = client_socket.recv(BUFFER_SIZE).decode()
    
    if not received:
        break

    else:

        folder, command, filename, filesize = received.split(SEPARATOR)
        print(filename)
        # remove absolute path if there is
        if command =="upload":
            filename = os.path.basename(filename)

            temp_filename, file_Extension = os.path.splitext(filename)
            path = getPath(file_Extension)
            
            

            print(file_Extension)
            final_filename=""
            
            if not os.path.exists(path+folder):
                os.mkdir(path+folder)
        
            final_filename = os.path.join(path+"/"+folder,temp_filename+file_Extension)

            

            # convert to integer
            filesize = int(filesize)
            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            
            with open(final_filename, "wb") as f:
                for _ in progress:
                    # read 1024 bytes from the socket (receive)
                    bytes_read = client_socket.recv(BUFFER_SIZE)
                    if not bytes_read:    
                        # nothing is received
                        # file transmitting is done
                        break
                    # write to the file the bytes we just received

                    f.write(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))


            print("Here is your file name"+ filename)
            # close the client socket
            
            # close the server socket
        elif command =="delete":
            print(command+" "+filename)
            temp_filename, file_Extension = os.path.splitext(filename)
            print(file_Extension)
            print(temp_filename)
            path = getPath(file_Extension)

            print(path)
            final_filename=os.path.join(path,"")
            
            if os.path.exists(final_filename+folder):
                os.remove(final_filename+folder+"/"+filename)
            else:
                print("does not exist")
            
        elif command == "download":
            print(command+" "+filename+"link: "+folder)
            file_directory = folder
            
            
            with open(file_directory,"rb") as f:
                
                l=f.read(4096)
                while(l):

                    client_socket.send(l)
                    l=f.read(4096)
                f.close()
            client_socket.shutdown(1)
                    #progress.update(len(bytes_read))
        elif command == "downloadFromLink":
            
            with open(folder,"rb") as f:
                
                l=f.read(4096)
                while(l):
                    client_socket.send(l)
                    l=f.read(4096)
                f.close()
            client_socket.shutdown(1)
