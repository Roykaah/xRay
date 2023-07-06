
import socket
import tqdm
import os
import random

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step
# the ip address or hostname of the server, the receiver
host = "192.168.18.3"
# the port, let's use 5001
port = 5001
# the name of file we want to send, make sure it exists
filenames = ["Dados/G-1.csv","Dados/G-2.csv","Dados/G-3.csv","Dados/G-4.csv","Dados/G-5.csv","Dados/G-6.csv"]
algoritmos = [0,1]
nomeUsuario = ["Bruna","Jonathas","Royka","Paulo"]
filename = filenames[random.randint(0,5)]
algoritmo = algoritmos[random.randint(0,1)]
usuario = nomeUsuario[random.randint(0,3)]

# get the file size
filesize = os.path.getsize(filename)

# create the client socket
s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

# send the filename and filesize
s.send(f"{filename}{SEPARATOR}{filesize}".encode())
# start sending the file
progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
with open(filename, "rb") as f:
    while True:
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        # we use sendall to assure transimission in 
        # busy networks
        s.sendall(bytes_read)
        # update the progress bar
        progress.update(len(bytes_read))
s.sendall((usuario+','+str(algoritmo)).encode())
# close the socket
s.close()
