
import socket
import tqdm
import os
import random
from PIL import Image 

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step
# the ip address or hostname of the server, the receiver
host = "192.168.18.3"
# the port, let's use 5002
port = 5011
# the name of file we want to send, make sure it exists
filenames = ["Dados/G-1.csv","Dados/G-2.csv","Dados/G-4.csv","Dados/G-5.csv"]
algoritmos = [0,1]
nomeUsuario = ["Bruna","Jonathas","Royka","Paulo"]
filename = filenames[random.randint(0,5)]
algoritmo = algoritmos[random.randint(0,1)]
usuario = nomeUsuario[random.randint(0,3)]

#pergunta o nome do usuario
usuario = input("Digite o nome do usuário: ")
receber_ou_enviar = input("Digite 1 para receber um arquivo, digite 2 para enviar o arquivo: ")


# get the file size
filesize = os.path.getsize(filename)

# create the client socket
s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

# send the filename and filesize
if receber_ou_enviar == '2':
# start sending the file

    s.send(f"{filename}{SEPARATOR}{filesize}".encode())
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
if receber_ou_enviar == '1':
    s.sendall((usuario).encode())
    print("Recebendo Dados...\n")
    path_imagem_recebida = 'imagens_enviadas_ao_cliente/'+usuario+'_'+str(algoritmo)+'.png'
    with open(path_imagem_recebida, 'wb') as f: #vai salvar a imagem no local indicado
        print('file opened')
        print('Recebendo dados...')
        data = s.recv(62000) #recebe o arquivo do servidor. Tamanho máximo de 62000
        f.write(data) #escreve o arquivo
        f.close()
    with open(path_imagem_recebida, 'rb') as f:
        im = Image.open(f) #abre a imagem
        im.show() #mostra a imagem
# close the socket
s.close()
