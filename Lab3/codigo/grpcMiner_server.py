import grpc
import time
from concurrent import futures
import grpcMiner_pb2
import grpcMiner_pb2_grpc
import hashlib
import random

class Transaction:
    # constructor for the class
    def __init__(self, transaction_id: int, challenge: int, solution: str, winner: int) -> None:
        self.transaction_id = transaction_id # Identificador da transação, representada por um valor inteiro;
        self.challenge = challenge # Valor do desafio criptográfico associado à transação, representado por um número [1..6], onde 1 é o desafio mais fácil.
        self.solution = solution # String que, se aplicada a função de hashing SHA-1, solucionará o desafio criptográfico proposto;
        self.winner = winner # ClientID do usuário que solucionou o desafio criptográfico para a referida TransactionI

transactions = [Transaction(1, random.randint(1,6), '', 0)]

def menu():
    for transaction in transactions:
        print('------------------- Transaction', transaction.transaction_id, '-------------------')
        print('Challenge:', transaction.challenge)
        print('Solution:', transaction.solution)
        print('Winner:', transaction.winner)
    print("Digite 0 para fechar ou 1 para adicionar nova transacao")
    print()
    n = input("Enter your choice: ")
    if(n=='0'):
        exit()
    if(n=='1'):
        tid = int(input("Enter Transaction ID:"))
        challenge = int(input('Enter Transaction Challenge:'))
        transactions.append(Transaction(tid, challenge, '', 0))

def serve():
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpcMiner_pb2_grpc.add_apiServicer_to_server(MinerulatorServicer(), grpc_server)
    grpc_server.add_insecure_port('[::]:8080')
    grpc_server.start()
    while True:
        menu()


class MinerulatorServicer(grpcMiner_pb2_grpc.apiServicer):
    def getTransactionId(self, request, context):
        return grpcMiner_pb2.intResult(result= transaction.transaction_id)
    def getChallenge(self, request, context):
        if(request.transactionId != transaction.transaction_id):
            return grpcMiner_pb2.intResult(result = -1)
        return grpcMiner_pb2.intResult(result = transaction.challenge)
    def  getTransactionStatus(self, request, context):
         if(request.transactionId != transaction.transaction_id):
             return grpcMiner_pb2.intResult(result = 1)
         if(transaction.solution == '' and transaction.winner == 0):
             return grpcMiner_pb2.intResult(result = 1)
         return grpcMiner_pb2.intResult(result = 0)
    def submitChallenge(self, request, context):
         if(request.transactionId != transaction.transaction_id):
             return grpcMiner_pb2.intResult(result = -1)
         if(transaction.solution != '' and transaction.winner != 0):
             return grpcMiner_pb2.intResult(result = 2)
         if((request.solution)[0:transaction.challenge] == "0" * transaction.challenge):
             transaction.winner = request.clientId
             transaction.solution = request.solution
             return grpcMiner_pb2.intResult(result = 1)
         return grpcMiner_pb2.intResult(result=0)
    def getWinner(self, request, context):
          if(request.transactionId != transaction.transaction_id):
              return grpcMiner_pb2.intResult(result = -1)
          return grpcMiner_pb2.intResult(result = transaction.winner)
    def getSolution(self,request,context):
        if(request.transactionId != transaction.transaction_id):
            return grpcMiner_pb2.structResult(status = -1, solution = -1, challenge = -1)
        if(transaction.solution == '' and transaction.winner == 0):
            return grpcMiner_pb2.structResult(status = 1, solution = -1, challenge = transaction.challenge)
        return grpcMiner_pb2.structResult(status = 0,solution =  transaction.solution, challenge = transaction.challenge)
         
if __name__ == '__main__':
    serve() 
    
