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
medias_analiticas = []

process = psutil.Process()
#Não apagar essa linha /opt/anaconda3/bin/python3.9 /home/todos/alunos/ct/a2236664/xRay/main.py
#https://www-users.cse.umn.edu/~saad/IterMethBook_2ndEd.pdf
memoria_antes_carregamento_modelos = process.memory_info().rss

print('Carregando matrizes modelos')
H1 = pd.read_csv('Dados/H-1.csv', sep=',', dtype=np.float64, header=None)
H2 = pd.read_csv('Dados/H-2.csv', sep=',', dtype=np.float64, header=None)
print('Terminou de carregar as matrizes modelos')






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
        print(error)
        if iter >= 50:
            break
    if(g.shape[0])==50816:
        imgf = np.resize(f, [60, 60])
    elif(g.shape[0])==27904:
        imgf = np.resize(f, [30, 30])
    
    imgf = np.transpose(imgf)
    return imgf,iter

        

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
        print(error)
        if iter >= 50:
            break

    if(g.shape[0])==50816:
        imgf = np.resize(f, [60, 60])
    elif(g.shape[0])==27904:
        imgf = np.resize(f, [30, 30])
    
    imgf = np.transpose(imgf)
    return imgf,iter
    # cv2.imwrite('imagefinal.png', imgf * 255)



def regulariza_imagem(H,imagem):
    #normaliza a imagem   
    coeficiente = np.max(abs(np.transpose(H)@imagem))[0] * 0.1
    print(f'coeficiente: {coeficiente}')
    imagem =  coeficiente/imagem
    return imagem

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

    imagem = regulariza_imagem(H,imagem)

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

    #print("Tempo total de execução: {:.2f} segundos".format(total_time))
    if usuario != 'TESTE':
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
    
    for imagem in ['Dados/G-1.csv', 'Dados/G-4.csv']:
        for algoritmo in [0,1]:
            total_cpu = 0
            total_memoria = 0
            for i in range(5):
                time.sleep(0.2)
                cpu_before = psutil.cpu_percent()
                memory_before = psutil.virtual_memory().percent
                processa_imagem(algoritmo, imagem, 'TESTE',60 if imagem == 'Dados/G-1.csv' else 30)

                memory_after = psutil.virtual_memory().percent
                total_memoria = total_memoria + abs(memory_after - memory_before)
                cpu_after = psutil.cpu_percent()
                total_cpu = (cpu_after - cpu_before) + total_cpu
            media_cpu = total_cpu/5
            media_memoria = total_memoria/5
            print(f"Consumo de memória médio: {media_memoria:.2f}% MB")
            print(f"Uso da CPU médio: {media_cpu:.2f}%")
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

def aumenta_pontuacao(nome_arquivo):
    try:
        with open(nome_arquivo, 'r') as fin:
            data = fin.read().splitlines(True)
        splitado = data[-1].split(',')
        nova_pontuacao = int(splitado[3]) + 1
        with open(nome_arquivo, 'w') as fout:
            data[-1] = splitado[0] + ',' + splitado[1] + ',' + splitado[2] + ',' + str(nova_pontuacao) + ',\n'
            fout.writelines(data)
        fin.close()
        fout.close()
    except:
        nova_pontuacao = 0
    return nova_pontuacao

def escolhe_proximo_arquivo():
    #percorre a fila de não processados
    proximo_arquivo = None
    primeiro_que_coube = None
    pontuacao_primeiro_que_coube = 0
    maior_pontuacao_arquivos_que_nao_cabem = 0
    #para ter mais certeza de quanto cpu estará gastando, fica esperando por 0.2 segundos
    time.sleep(0.2)
    cpu_agora = psutil.cpu_percent()
    for arquivo in os.listdir('imagens_recebidas'):
        if arquivo.endswith(".csv"):
            #O primeiro que couber, coloca lá!!!
            nome_arquivo = 'imagens_recebidas/' + arquivo
            custo = quanto_custa(nome_arquivo)
            if custo[0] is not None and custo[0]/10 < 100 - cpu_agora and custo[1] < psutil.virtual_memory().percent:
                #print(f'o custo é de {custo/10:.2f}% e o uso da cpu é de {cpu_agora:.2f}%')
                primeiro_que_coube = nome_arquivo
                pontuacao_primeiro_que_coube = aumenta_pontuacao(nome_arquivo)
                break
            else:
                nova_pontucao = aumenta_pontuacao(nome_arquivo)
                if nova_pontucao > maior_pontuacao_arquivos_que_nao_cabem:
                    maior_pontuacao_arquivos_que_nao_cabem = nova_pontucao
                    proximo_arquivo = nome_arquivo
    #SE existe algum que cabe            
    if primeiro_que_coube is not None:
        #Se esse proximo que cabe merece o próximo lugar na fila
        if pontuacao_primeiro_que_coube + 2 > maior_pontuacao_arquivos_que_nao_cabem:
            print("Pontuacao do primeiro que coube é maior!!!")
            return shutil.move(primeiro_que_coube, 'em_processamento/'+primeiro_que_coube.split('/')[-1])
        else:
            print("Pontuacao do primeiro da fila é maior, esperando espaço...")
            return espera_ter_espaco(proximo_arquivo)
        
    else: #Se não existe nenhum que cabe
        return None
    
def espera_ter_espaco(nome_arquivo):
    while( quanto_custa(nome_arquivo)[0]/10 > 100 - psutil.cpu_percent() or quanto_custa(nome_arquivo)[1] > psutil.virtual_memory().percent):
        time.sleep(0.2)
    return shutil.move(nome_arquivo, 'em_processamento/'+nome_arquivo.split('/')[-1])

def main():
    print('Começou')
    processa_imagem(0,'Dados/G-6.csv','TESTE',30)
    print('Acabou')
    '''testa_processamento()
    #medias_analiticas = [[436.76000000000005, 668467.2], [309.04, 0.0], [481.98, 117145.6], [289.53999999999996, 0.0]]
    while(True):
        proximo_arquivo = escolhe_proximo_arquivo()
        if proximo_arquivo != None:
            usuario,tipo_de_processamento,modelo = divide_arquivo(proximo_arquivo)
            thread = threading.Thread(target=processa_imagem, args=(tipo_de_processamento,proximo_arquivo, usuario, modelo))
            thread.start()'''
            
            

if __name__ == "__main__":
    main()

