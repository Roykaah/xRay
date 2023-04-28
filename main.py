import numpy as np
import psutil
import time
import pandas as pd

#MUITO PESADO PARA RODAR COM O REPLIT, RODAR FORA! xD ;-;

p = np.zeros_like
start_time = time.time()
process = psutil.Process()
cpu_before = process.cpu_percent()
memory_before = process.memory_info().rss


def CGNE(H, g, tol, max_iter):
	# ta com erro aqui ainda n descobri pq
	f = np.zeros((H[0].shape))
	r = np.array(g - (H * f))
	r = np.resize(r, (1, H[0].shape))
	print(r)
	p = np.transpose(H) * r

	for i in range(1, 10):
		alpha = 1


'''
   r_norm_old = np.linalg.norm(r0)
    for i in range(max_iter):
        Ap = A @ p0
        alpha = r_norm_old**2 / (p0.T @ Ap)
        x = x + alpha * p0
        r = r0 - alpha * Ap
        r_norm = np.linalg.norm(r)
        if r_norm < tol:
            break
        if i > 0 and i % 50 == 0:
            # reorthogonalize p every 50 iterations
            for j in range(i):
                beta = (p0.T @ A @ p[j]) / (p[j].T @ A @ p[j])
                p0 = p0 - beta * p[j]
        beta = r_norm**2 / r_norm_old**2
        p0 = r + beta * p0
        r_norm_old = r_norm
        p[i] = p0
    return x
    '''

M = pd.read_csv('Dados/M.csv', sep=';', dtype=np.float64, header=None)
a = pd.read_csv('Dados/a.csv', sep=';', dtype=np.float64, header=None)
N = pd.read_csv('Dados/N.csv', sep=';', dtype=np.float64, header=None)
print(type(a))
'''
try: 
    print(N @ M)
    print(a @ M)
    print(M @ a)
except: 
	print("Algo deu de errado")
'''
#H = pd.read_csv('H-1/H-2.csv', sep=',',dtype=np.float32, header=None)
M = M / 100

CGNE(M, a, 1, 1)
end_time = time.time()

total_time = end_time - start_time
print("Tempo total de execução: {:.2f} segundos".format(total_time))

memory_after = process.memory_info().rss
memory_consumed = memory_after - memory_before
print(f"Consumo de memória: {memory_consumed/1024/1024:.2f} MB")

cpu_after = process.cpu_percent()
cpu_consumed = cpu_after - cpu_before
print(f"Uso da CPU: {cpu_consumed:.2f}%")
