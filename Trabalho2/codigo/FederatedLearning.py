import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D, Flatten, Dense
from tensorflow.keras.optimizers import SGD
import random
from concurrent import futures
import numpy as np
import json
import paho.mqtt.client as mqtt
import threading

# Configurações do broker MQTT
broker = "localhost"
port = 1883
topic_init = "sd/init"
topic_election = "sd/election"

# Variáveis para controle da eleição
participants = set()
init_messages_received = set()
election_messages_received = {}

# Dados do líder eleito
leader_id = None
leader_vote_id = None

# Variáveis de controle do aprendizado federado
min_clients = 3  # Número mínimo de clientes para iniciar o treinamento federado
max_rounds = 10  # Número máximo de rounds de treinamento
target_tolerance = 0.95  # Meta de acurácia a ser alcançada

# Cliente de Treinamento
class TrainingClient:
    def __init__(self):
        self.model = None
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None
        self.weights_file_path = "weights_file.h5"
    
    def get_parameters(self, config):
        return self.model.get_weights()

    def fit(self):
        self.model.fit(self.x_train, self.y_train, epochs=1, verbose=2)
        self.model.save_weights(self.weights_file_path)

    def evaluate(self, filepath):
        self.model.load_weights(filepath)
        loss, acc = self.model.evaluate(self.x_test, self.y_test, verbose=2)
        return loss, acc

    def start_training(self, current_round, weights_file_path):
        print("Round:", current_round)
        self.weights_file_path = weights_file_path
        input_shape = (28, 28, 1)
        num_classes = 10
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
        sample_size_train = int((1/10) * len(x_train))
        sample_size_test = int((1/10) * len(x_test))
        idx_train = np.random.choice(np.arange(len(x_train)), sample_size_train, replace=False)
        self.x_train = x_train[idx_train] / 255.0
        self.y_train = y_train[idx_train]
        self.y_train = tf.one_hot(y_train.astype(np.int32), depth=10)
        idx_test = np.random.choice(np.arange(len(x_test)), sample_size_test, replace=False)
        self.x_test = x_test[idx_test] / 255.0
        self.y_test = y_test[idx_test]
        self.y_test = tf.one_hot(y_test.astype(np.int32), depth=10)
        self.model = define_model(input_shape, num_classes)
        self.fit()
        return len(self.x_train)

    def evaluate_model(self, aggregated_weights_file_path):
        loss, acc = self.evaluate(aggregated_weights_file_path)
        return acc


# Servidor de Treinamento
class TrainingServer:
    def __init__(self):
        input_shape = (28, 28, 1)
        num_classes = 10
        self.model = define_model(input_shape, num_classes)
        self.clients = {}
        self.round_accuracies = [[]]
        self.current_round = 1
        self.finished_training = False
        self.aggregated_weights_file_path = "aggregated_file.h5"

    def register_client(self, client_id, client_ip, client_port):
        self.clients[client_id] = {
            'ip': client_ip,
            'port': client_port,
            'weights': str(client_id) + "weights.h5"
        }
        if len(self.clients) >= min_clients:
            self.train_federated()

    def train_federated(self):
        round_accuracy = 1
        while self.current_round < max_rounds or round_accuracy <= target_tolerance:
            elect_leader()
            client_weights = []
            for client_id, client_info in self.clients.items():
                client = TrainingClient()
                weights_file_path = client_info['weights']
                local_dataset_samples = client.start_training(self.current_round, weights_file_path)
                client_weights.append(client.get_parameters())
            for client in self.clients:
                self.model.set_weights(average_weights(client_weights))
                self.model.save_weights(self.aggregated_weights_file_path)
                round_accuracy = self.evaluate_model(self.aggregated_weights_file_path)
                self.round_accuracies.append(round_accuracy)
            self.current_round += 1
            self.plot_round_accuracies()

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
def define_model(input_shape, num_classes):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=input_shape))
    model.add(MaxPool2D((2, 2)))
    model.add(Flatten())
    model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
    model.add(Dense(num_classes, activation='softmax'))
    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def average_weights(weights_list):
    avg_weights = []
    num_weights = len(weights_list)

    for weights in zip(*weights_list):
        avg_weights.append(np.mean(weights, axis=0))

    return avg_weights

def elect_leader():
    global leader_id, leader_vote_id
    max_vote_id = max(election_messages_received.values())
    leader_candidates = [client_id for client_id, vote_id in election_messages_received.items() if vote_id == max_vote_id]
    leader_id = random.choice(leader_candidates)
    leader_vote_id = max_vote_id

def publish_leader_message():
    leader_data = {
        "ClientID": client_id
    }
    client.publish(topic_init, json.dumps(leader_data))

def process_init_message(client, userdata, message):
    payload = json.loads(message.payload)
    client_id = payload["ClientID"]
    participants.add(client_id)
    init_messages_received.add(client_id)

    if len(init_messages_received) == min_clients:
        start_election()

def process_election_message(client, userdata, message):
    payload = json.loads(message.payload)
    client_id = payload["ClientID"]
    vote_id = payload["VoteID"]
    election_messages_received[client_id] = vote_id

    if len(election_messages_received) == min_clients:
        elect_leader()

def start_election():
    vote_id = random.randint(0, 65535)
    election_data = {
        "ClientID": client_id,
        "VoteID": vote_id
    }
    client.publish(topic_election, json.dumps(election_data))

# Gera um ClientID aleatório de 16 bits
client_id = str(random.randint(0, 65535))

# Configura o cliente MQTT
client = mqtt.Client()
client.connect(broker, port)

# Assina a fila de mensagens de inicialização
client.subscribe(topic_init)
client.message_callback_add(topic_init, process_init_message)

# Assina a fila de mensagens de eleição
client.subscribe(topic_election)
client.message_callback_add(topic_election, process_election_message)

# Publica a mensagem de inicialização
init_data = {
    "ClientID": client_id
}
client.publish(topic_init, json.dumps(init_data))

# Mantém o cliente MQTT em execução
client.loop_forever()
