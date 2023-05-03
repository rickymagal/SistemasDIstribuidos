from enum import Enum
import grpc
import grpcMiner_pb2
import grpcMiner_pb2_grpc
import pybreaker
from multiprocessing.pool import ThreadPool
import multiprocessing as mp
import hashlib
import random
import queue

breaker = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=2)
@breaker

def solve(queue, challenge):
    guess = [random.randint(0,1)] * 160
    if bin(int(hashlib.sha1(guess), 16))[::challenge] == [0]*challenge:
        queue.put(guess)
    return
    

def run(client, n):
    if n == '1':
        print('1. Buscar transactionID atual;')
        print('getTransactionID:')
        # raise pybreaker.CircuitBreakerError
        res = client.getTransactionId(grpcMiner_pb2.void())
        print(res.result)
    if n == '2':
        print('2. Buscar a challenge (desafio) associada à transactionID atual;')
        print('getChallenge:')
        # raise pybreaker.CircuitBreakerError
        tid = int(input('Entre com o transactionId: '))
        res = client.getChallenge(grpcMiner_pb2.transactionId(transactionId=tid))
        print(res.result)
    if n == '3':
        print('3. Buscar, localmente, uma solução para o desafio proposto')
        print('getTransactionStatus:')
        # raise pybreaker.CircuitBreakerError
        tid = int(input('Entre com o transactionId: '))
        res = client.getTransactionStatus(grpcMiner_pb2.transactionId(transactionId=tid))
        print(res.result)
    if n == '4':
        print('4. Imprimir localmente a solução encontrada;')
        print('getWinner:')
        # raise pybreaker.CircuitBreakerError
        tid = int(input('Entre com o transactionId: '))
        res = client.getWinner(grpcMiner_pb2.transactionId(transactionId=tid))
        print(res.result)
    if n == '5':
        print('5. Mine;')
        print('Mine:')
        # raise pybreaker.CircuitBreakerError
        tid = int(input('Entre com o transactionId:'))
        cid = int(input('Entre com o clienteId: '))
        challenge = client.getChallenge(grpcMiner_pb2.transactionId(transactionId=tid))
        numThreads = int(input('Digite o numero de threads a serem usadas: '))
        fila = queue.Queue()
        pool = mp.pool.ThreadPool(processes = numThreads)
        pool.apply_async(solve, fila, challenge)
        sol = fila.get()
        res = client.submitChallenge(grpcMiner_pb2.challengeArgs(transactionId=tid,clientId=cid, solution=sol))
        print(res.result)
    if n == '6':
        print('6. Imprimir/Decodificar resposta do servidor.')
        print('getSolution:')
        # raise pybreaker.CircuitBreakerError
        tid = int(input('Entre com o transactionId: '))
        res = client.getSolution(grpcMiner_pb2.transactionId(transactionId=tid))
        print(res.status, res.solution, res.challenge)
    elif n == '0':
        print('Fim.')
        exit()
    else:
        print('Entrada Inválida,')

@breaker
def connect():
    channel = grpc.insecure_channel('localhost:8080')
    client = grpcMiner_pb2_grpc.apiStub(channel)
    while True:
        print('Escolha:')
        print('1 para getTransactionID,')
        print('2 para getChallenge,')
        print('3 para getTransactionStatus')
        print('4 para getWinner,')
        print('5 para Mine')
        print('6 para getSolution')
        print('0 para Finalizar')
        print()
        
        n = input('Enter your choice: ')
        
        try:
            running = run(client, n)
            # print(running)
        except pybreaker.CircuitBreakerError:
            print(pybreaker.CircuitBreakerError)


if __name__ == '__main__':
    connect()

