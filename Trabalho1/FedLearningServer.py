import os
import grpc
from concurrent import futures
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D,Flatten,Dense
from tensorflow.keras.optimizers import SGD
import numpy as np
import FedLearningProto_pb2 as pb2
import FedLearningProto_pb2_grpc as pb2_grpc
import matplotlib.pyplot as plt
import threading
import asyncio

# Inputs
min_clients = int(input("Numero minimo de clientes:"))
max_rounds = int(input("Numero maximo de rounds:"))
target_tolerance = float(input("Tolerancia alvo:"))
server_port = '8080'
#Canal de Comunicacao com cliente
channel = grpc.insecure_channel('localhost:8080')
stub = pb2_grpc.TrainingClientStub(channel)

# Servidor de Treinamento
class TrainingServer(pb2_grpc.TrainingServerServicer):
    def __init__(self):
        input_shape = (28, 28, 1)
        num_classes = 10
        self.model = define_model(input_shape,num_classes)
        self.clients = {}
        self.round_accuracies = [[]]
        self.current_round = 1
        self.finished_training = False
        self.aggregated_weights_file_path = "aggregated_file.tf"
    #Chamada de Registro
    def RegisterClient(self, request, context):
        client_id = request.client_id
        client_ip = request.ip
        client_port = request.port
        self.clients[client_id] = {
            'ip': client_ip,
            'port': client_port,
            'weights': str(request.client_id) +"weights.tf"
        }
        if len(self.clients) >= min_clients:
            thread = threading.Thread(target=self.TrainFederated)
            thread.start()
        return pb2.RegistrationResponse(confirmation_code=200)
    # Treina federado
    def TrainFederated(self):
        while self.current_round < max_rounds:
            client_weights = []
            for client_id, client_info in self.clients.items():
                training_response = stub.StartTraining(pb2.TrainingStartRequest(current_round=self.current_round, weights_file_path=client_info['weights']), wait_for_ready=True)
                self.model = tf.keras.models.load_model(client_info['weights'])
                client_weights.append(self.model.get_weights())
            for client in clients:
                self.model.set_weights = average_weights(client_weights)
                self.model.save(self.aggregated_weights_file_path)
                evaluation_request = pb2.EvaluationRequest(aggregated_weights_file_path=self.aggregated_weights_file_path)
                evaluation_response = stub.EvaluateModel(evaluation_request,wait_for_ready=True)
                self.round_accuracies.append(evaluation_response.accuracy)
            self.current_round += 1
            self.plot_round_accuracies()
    # Plota precisao
    def plot_round_accuracies(self):
        rounds = range(1, self.current_round)
        mean_accuracies = np.mean(self.round_accuracies, axis=0)

        plt.plot(rounds, mean_accuracies, marker='o')
        plt.xlabel('Round')
        plt.ylabel('Mean Accuracy')
        plt.title('Federated Learning Training Progress')
        plt.grid(True)
        plt.show()




# Define modelo
def define_model(input_shape,num_classes):
  model = Sequential()
  model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=input_shape))
  model.add(MaxPool2D((2, 2)))
  model.add(Flatten())
  model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
  model.add(Dense(num_classes, activation='softmax'))
  # compile model
  opt = SGD(learning_rate=0.01, momentum=0.9)
  model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
  return model

# Agrega os pesos
def average_weights(weights_list):
    avg_weights = []
    num_weights = len(weights_list)

    for weights in zip(*weights_list):
        avg_weights.append(np.mean(weights, axis=0))

    return avg_weights

# Inicia servidor
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_TrainingServerServicer_to_server(TrainingServer(), server)
    server.add_insecure_port(f'[::]:{server_port}')
    server.start()
    print(f'Servidor gRPC iniciado na porta {server_port}')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
