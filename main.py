import numpy as np
import psutil
import time
import pandas as pd
import cv2
import json 
import csv
import os
import threading
import shutil

ALGORITMO_CGNE=0
ALGORITMO_CGNR=1
medias_analiticas = [[436.76000000000005, 668467.2], [309.04, 0.0], [481.98, 117145.6], [289.53999999999996, 0.0]]

process = psutil.Process()
#Não apagar essa linha /opt/anaconda3/bin/python3.9 /home/todos/alunos/ct/a2236664/xRay/main.py
#https://www-users.cse.umn.edu/~saad/IterMethBook_2ndEd.pdf
memoria_antes_carregamento_modelos = process.memory_info().rss
print('Carregando matrizes modelos')
H1 = pd.read_csv('Dados/H-1.csv', sep=',', dtype=np.float64, header=None)
H2 = pd.read_csv('Dados/H-2.csv', sep=',', dtype=np.float64, header=None)





def CGNE(H, g, tol):
    f = np.zeros([(np.transpose(H)).shape[0], 1])
    
    r = g 
    p = np.transpose(H) @ r
    iter = 0

    error = abs(np.linalg.norm(r))

    while (error)  >= tol:
        error = abs(np.linalg.norm(r))
        iter += 1

        alpha = (np.transpose(r) @ r)[0][0] / (np.transpose(p) @ p)[0][0]
        f = f + alpha * p
        r1 = r - alpha * H @ p
        betha = (np.transpose(r1) @ r1)[0][0] / (np.transpose(r) @ r)[0][0]
        p1 = np.transpose(H) @ r1 + betha * p
        r = r1
        p = p1

        error = abs(abs(np.linalg.norm(r)) - error )
    
    if(g.shape[0])==50816:
        imgf = np.resize(f, [60, 60])
    elif(g.shape[0])==27904:
        imgf = np.resize(f, [30, 30])
    
    imgf = np.transpose(imgf)
    return imgf,iter
    cv2.imwrite('imagefinal.png', imgf * 255)

        

def CGNR(H, g, tol):
    f = np.zeros([(np.transpose(H)).shape[0], 1])
    r = g 
    z = np.transpose(H) @ r
    p = z
    error = abs(np.linalg.norm(r))
    iter = 0

    while error >= tol:
        error = abs(np.linalg.norm(r))
        iter += 1
        
        w = H @ p
        alpha = np.power(np.linalg.norm(z),2) / np.power(np.linalg.norm(w),2)
        f = f + alpha * p
        r = r - alpha * w
        z1 = np.transpose(H) @ r
        betha = np.power(np.linalg.norm(z1),2) / np.power(np.linalg.norm(z),2)
        p = z + betha * p
        z=z1

        error = abs(abs(np.linalg.norm(r)) - error )

    if(g.shape[0])==50816:
        imgf = np.resize(f, [60, 60])
    elif(g.shape[0])==27904:
        imgf = np.resize(f, [30, 30])
    
    imgf = np.transpose(imgf)
    return imgf,iter
    # cv2.imwrite('imagefinal.png', imgf * 255)

def processa_imagem(tipo_de_processamento, nome_arquivo, usuario,modelo):

    imagem = pd.read_csv(nome_arquivo, sep=',', dtype=np.float64, header=None)
    p = np.zeros_like
    start_time = time.time()

    if(modelo)==60:
        H = H1
        pixel = "60x60"
    elif(modelo)==30:
        H = H2
        pixel = "30x30"

    if(tipo_de_processamento==ALGORITMO_CGNE):
        imagem_final, iteracoes= CGNE(H, imagem, 1e-4)
        algoritmo = "CGNE"
    elif(tipo_de_processamento==ALGORITMO_CGNR):
        imagem_final, iteracoes= CGNR(H, imagem, 1e-4)
        algoritmo = "CGNR"

    end_time = time.time()

    total_time = end_time - start_time
    
    #salva imagem com os dados obrigatorios
    dictionary = {
        'usuario': usuario,
        'algoritmo': algoritmo,
        'data_inicio': start_time,
        'data_fim': end_time,
        'tm_pixel': pixel,
        'iteracoes': int(iteracoes),
        'id_imagem': usuario + str(start_time) # id unico da imagem
    }
    json_object = json.dumps(dictionary, indent = 4) 
    cv2.imwrite('imagens_finais/' + usuario + str(start_time) + '.png', imagem_final * 255)
    with open('relatorios_finais/' + usuario + str(start_time) + '.json', 'w') as outfile:
        json.dump(json_object, outfile)
    # print(json_object)

    print("Tempo total de execução: {:.2f} segundos".format(total_time))
    os.remove(nome_arquivo)



def divide_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(nome_arquivo, 'w') as fout:
        linha_dados_usuario = data[-1]
        fout.writelines(data[:-1])
    splitado  = linha_dados_usuario.split(',')
    return splitado[0],int(splitado[1]),int(splitado[2])


def testa_processamento():
    print('Começou a fazer os testes de processamento')
    #testa para o algoritmo 1:
    
    for imagem in ['Dados/G-1.csv', 'Dados/G-2.csv']:
        for algoritmo in [0,1]:
            total_cpu = 0
            total_memoria = 0
            for i in range(5):
                time.sleep(2)
                cpu_before = process.cpu_percent()
                memory_before = process.memory_info().rss
                processa_imagem(algoritmo, imagem, 'TESTE',60 if imagem == 'Dados/G-1.csv' else 30)

                memory_after = process.memory_info().rss 
                total_memoria = total_memoria + abs(memory_after - memory_before)
                cpu_after = process.cpu_percent()
                total_cpu = (cpu_after - cpu_before) + total_cpu
            media_cpu = total_cpu/5
            media_memoria = total_memoria/5
            print(f"Consumo de memória médio: {media_memoria/1024/1024:.2f} MB")
            print(f"Uso da CPU médio: {media_cpu/10:.2f}%")
            medias_analiticas.append([media_cpu,media_memoria])
        print(medias_analiticas)

def quanto_custa(nome_arquivo):
    with open(nome_arquivo, 'r') as fin:
        data = fin.read().splitlines(True)

    try:
        linha_dados_usuario = data[-1]
        fin.close()
        splitado  = linha_dados_usuario.split(',')
        algoritmo = int(splitado[1])
        modelo =  1 if int(splitado[2]) == 30 else 0
        return medias_analiticas[algoritmo+(modelo*2)]
    except:
        return None, None

def escolhe_proximo_arquivo():
    #percorre a fila de não processados
    proximo_arquivo = None
    for arquivo in os.listdir('imagens_recebidas'):
        if arquivo.endswith(".csv"):
            #O primeiro que couber, coloca lá!!!
            custo = quanto_custa('imagens_recebidas/' + arquivo)[0]
            load1, load5, load15 = psutil.getloadavg()
 
            cpu_agora = (load15/os.cpu_count()) * 100
            if custo is not None and custo < 100 - cpu_agora:
                print(f'o custo é de {custo/10:.2f}% e o uso da cpu é de {cpu_agora/10:.2f}%')
                proximo_arquivo = 'imagens_recebidas/' + arquivo
            '''else
                with open(nome_arquivo, 'r') as fin:
                    data = fin.read().splitlines(True)
                with open(nome_arquivo, 'w') as fout:
                    data[-1] = data[-1] + ',CUSTO'
                    fout.writelines(data)'''
    if proximo_arquivo is not None:
        #passa o arquivo para a pasta de processados
        proximo_arquivo = shutil.move(proximo_arquivo, 'em_processamento/'+proximo_arquivo.split('/')[-1])
    return proximo_arquivo



def main():
    #testa_processamento()
    #medias_analiticas = [[436.76000000000005, 668467.2], [309.04, 0.0], [481.98, 117145.6], [289.53999999999996, 0.0]]
    while(True):
        proximo_arquivo = escolhe_proximo_arquivo()
        if proximo_arquivo != None:
            usuario,tipo_de_processamento,modelo = divide_arquivo(proximo_arquivo)
            thread = threading.Thread(target=processa_imagem, args=(tipo_de_processamento,proximo_arquivo, usuario, modelo))
            thread.start()
            
            

if __name__ == "__main__":
    main()

