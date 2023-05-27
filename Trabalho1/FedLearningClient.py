import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D,Flatten,Dense
from tensorflow.keras.optimizers import SGD
import random
from concurrent import futures
import grpc
import numpy as np
import FedLearningProto_pb2 as pb2
import FedLearningProto_pb2_grpc as pb2_grpc
import asyncio

#Cliente de Treinamento
class TrainingClient(pb2_grpc.TrainingClientServicer):
    def __init__(self):
        self.model = None
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None
        self.weights_file_path=None
    
    def get_parameters(self, config):
        return self.model.get_weights()
    #Treina
    def fit(self):
        self.model.fit(self.x_train, self.y_train, epochs=1, verbose=2)
        self.model.save(self.weights_file_path)
    # Avalia modelo e seta os pesos passados pelo servidor
    def evaluate(self, filepath):
        aggregatedModel = tf.keras.models.load_model(filepath)
        self.model.set_weights(aggregatedModel.get_weights())
        loss, acc = self.model.evaluate(self.x_test, self.y_test, verbose=2)
        return loss, acc
    # Chamada de treinamento
    def StartTraining(self, request, context):
        print("Round:", request.current_round)
        self.weights_file_path = request.weights_file_path
        input_shape = (28,28,1)
        num_classes=10
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
        sample_size_train = int((1/10)*len(x_train))
        sample_size_test = int((1/10)*len(x_test))
        idx_train = np.random.choice(np.arange(len(x_train)), sample_size_train, replace=False)
        self.x_train = x_train[idx_train]/255.0
        self.y_train = y_train[idx_train]
        self.y_train = tf.one_hot(y_train.astype(np.int32), depth=10)
        idx_test = np.random.choice(np.arange(len(x_test)), sample_size_test, replace=False)
        self.x_test = x_test[idx_test]/255.0
        self.y_test = y_test[idx_test]
        self.y_test = tf.one_hot(y_test.astype(np.int32), depth=10)
        self.model = define_model(input_shape,num_classes)
        self.fit()
        return pb2.TrainingResponse(local_dataset_samples=len(self.x_train))
    #Chamada de evaluate
    def EvaluateModel(self, request, context):
        loss, acc = self.evaluate(request.aggregated_weights_file_path)
        return pb2.EvaluationResponse(accuracy=acc)

# Define model
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

def run():
    channel = grpc.insecure_channel('localhost:8080')
    stub = pb2_grpc.TrainingServerStub(channel)
    client = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_TrainingClientServicer_to_server(TrainingClient(), client)
    client.add_insecure_port(f'[::]:8080')
    client.start()
    # Registrar cliente
    client_id = int(input("Client ID:"))
    registration_request = pb2.RegistrationRequest(ip='localhost', port=8080,client_id=client_id)
    registration_response = stub.RegisterClient(registration_request, wait_for_ready=True)
    print('Confirmação:', registration_response.confirmation_code)
    client.wait_for_termination()
    
if __name__ == '__main__':
    run()
