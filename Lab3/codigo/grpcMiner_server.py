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

transaction = Transaction(1, random.randint(1,6), '', 0)
        
def serve():
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpcMiner_pb2_grpc.add_apiServicer_to_server(MinerulatorServicer(), grpc_server)
    grpc_server.add_insecure_port('[::]:8080')
    grpc_server.start()
    grpc_server.wait_for_termination()


class MinerulatorServicer(grpcMiner_pb2_grpc.apiServicer):
    def add(self, request, context):
        return grpcMiner_pb2.result((request.numOne + request.numTwo))
    def getTransactionId(self, request, context):
        return grpcMiner_pb2.intResult(result= transaction.transaction_id)
    def getChallenge(self, request, context):
        if(request.transactionId != transaction.transaction_id):
            return grpcMiner_pb2.intResult(result = -1)
        return grpcMiner_pb2.intResult(result = transaction.challenge)
    def  getTransationStatus(self, request, context):
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
         if(bin(int(hashlib.sha1(request.solution), 16))[::transaction.challenge] == [0] * transaction.challenge):
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
    
