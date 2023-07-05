import socket
import tqdm
import os
import time

# device's IP address
SERVER_HOST = "192.168.18.3"
SERVER_PORT = 5001
# receive 4096 bytes each time
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

# create the server socket
# TCP socket
s = socket.socket()

# bind the socket to our local address
s.bind((SERVER_HOST, SERVER_PORT))

# enabling our server to accept connections
# 5 here is the number of unaccepted connections that
# the system will allow before refusing new connections
s.listen(5)


while True:
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    # accept connection if there is any
    client_socket, address = s.accept() 
    # if below code is executed, that means the sender is connected
    print(f"[+] {address} is connected.")# close the socket
    #s.close()
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    ## remove absolute path if there is
    #filename = os.path.basename(filename)
    pathname = 'imagens_recebidas/'
    # convert to integer
    filesize = int(filesize)

    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving file", unit="B", unit_scale=True, unit_divisor=1024)

    nome_arquivo = str(time.time())
    with open(pathname+nome_arquivo+'.csv', "wb") as f:
        while True:
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
    #adiciona no final do arquivo o tamanho dele
    #quantidade de linhas no arquivo
        #TODO: FEIO, MELHORAR
        q=0
        with open(pathname+nome_arquivo+'.csv', "r") as f2:
            for line in f2:
                q+=1
        print(f"Quantidade de linhas: {q}")
        f.write((','+str(60 if q>40000 else 30)+',1,\n').encode())
        f.close()
    progress.close()
    # close the client socket
    client_socket.close()
    # close the server socket
    #s.close()
