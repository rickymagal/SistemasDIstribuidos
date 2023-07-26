import json
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D, Flatten, Dense
from tensorflow.keras.optimizers import SGD
import random
import paho.mqtt.client as mqtt
import numpy as np

# Configurações do broker MQTT
broker = "localhost"
port = 1883
topic_init = "sd/init"
topic_election = "sd/election"
topic_start_server = "sd/start_server"
topic_start_client = "sd/start_client"

# Variáveis para controle da eleição
participants = set()
init_messages_received = set()
election_messages_received = {}

# Dados do líder eleito
leader_id = None
leader_vote_id = None

# Variável para armazenar se este cliente foi eleito como servidor
this_client_is_server = False

# Constants for control of Federated Learning process
NUM_CLIENTS_CHOSEN = 3
MIN_CLIENTS_PARTICIPATING = 3
MAX_ROUNDS = 10
ACCURACY_THRESHOLD = 0.95


# Cliente MQTT
client = mqtt.Client()

# Lista para armazenar as acuracias de cada round
accuracy_per_round = []


# Variável para armazenar se este cliente foi eleito como servidor
this_client_is_server = False

# Variável para controlar o número atual de rodadas
round_num = 0


# Funcao para processar a mensagem de inicializacao
def process_init_message(client, userdata, message):
    payload = json.loads(message.payload)
    client_id = payload["ClientID"]
    #Adiciona o cliente como participante
    participants.add(client_id)
    init_messages_received.add(client_id)
    if len(init_messages_received) == MIN_CLIENTS_PARTICIPATING:
        # Todos os 3 participantes enviaram suas mensagens de inicializacao -> Comeca eleicao.
        start_election()
        
# Função para iniciar a fase de eleição
def start_election():
    vote_id = random.randint(0, 65535)  # Gera o VoteID aleatoriamente
    # Publica a mensagem de eleição com o VoteID e o ClientID
    election_data = {
        "ClientID": client_id,
        "VoteID": vote_id
    }
    client.publish(topic_election, json.dumps(election_data))

#Funcao para processar a mensagem de eleicao
def process_election_message(client, userdata, message):
    payload = json.loads(message.payload)
    client_id = payload["ClientID"]
    vote_id = payload["VoteID"]
    election_messages_received[client_id] = vote_id
    if len(election_messages_received) == len(participants):  # Verifica se todos os clientes votaram
        elect_leader()

        
# Função para eleger o líder
def elect_leader():
    global leader_id, leader_vote_id, this_client_is_server
    max_vote_id = max(election_messages_received.values())
    leader_candidates = [client_id for client_id, vote_id in election_messages_received.items() if vote_id == max_vote_id]
    leader_id = leader_candidates[0]
    leader_vote_id = max_vote_id

    if leader_id == client_id:
        # Se declara lideR
        print("I am the leader! ClientID:", leader_id)
        this_client_is_server = True
        client.publish(topic_start_server, json.dumps({"ClientID": leader_id}))
    else:
        print("The leader is:", leader_id)
        this_client_is_server = False
        client.publish(topic_start_client, json.dumps({"ClientID": leader_id}))

# Função para processar a mensagem de início como servidor
def process_start_server(client, userdata, message):
    global this_client_is_server
    payload = json.loads(message.payload)
    leader_id = payload["ClientID"]
    print(f"Cliente {client_id} iniciando como servidor para líder {leader_id}.")
    this_client_is_server = True
    start_as_server()

# Função para processar a mensagem de início como cliente
def process_start_client(client, userdata, message):
    global this_client_is_server
    payload = json.loads(message.payload)
    leader_id = payload["ClientID"]
    print(f"Cliente {client_id} iniciando como cliente para líder {leader_id}.")
    this_client_is_server = False
    start_as_client()

#Funcao para comecar como o servidor
def start_as_server():
    global this_client_is_server, round_num
    input_shape = (28, 28, 1)
    num_classes = 10
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train = x_train / 255.0
    y_train = tf.one_hot(y_train.astype(np.int32), depth=num_classes)
    model = define_model(input_shape, num_classes)
    epochs = 5
    while round_num < MAX_ROUNDS:
        round_num += 1
        federated_learning_round(round_num, model, x_train, y_train)
        evaluate_model(model, round_num)  # Adicione esta linha para avaliar o modelo após cada round
        # Verifica se a acurácia é maior ou igual ao limiar
        if accuracy_per_round[-1] >= ACCURACY_THRESHOLD:
            break
    client.publish("sd/training_complete", "Training is complete.")



#Funcao para comecar como o cliente 
def start_as_client():
    global this_client_is_server
    def on_message(client, userdata, message):
        payload = json.loads(message.payload)
        weights = payload["Weights"]
        input_shape = (28, 28, 1)
        num_classes = 10
        model = define_model(input_shape, num_classes)
        model.set_weights(weights)
        _, (x_test, y_test) = tf.keras.datasets.mnist.load_data()
        x_test = x_test / 255.0
        y_test = tf.one_hot(y_test.astype(np.int32), depth=num_classes)
        loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
        print(f"Client {client_id} - Test accuracy: {accuracy:.4f}")
    client.message_callback_add("sd/weights", on_message)
    client.subscribe("sd/weights")

#Funcao para executar um round de aprendizado federado.
def federated_learning_round(round_num, model, x_train, y_train):
    global this_client_is_server, accuracy_per_round
    coordinator_id = leader_id 
    while len(participants) < MIN_CLIENTS_PARTICIPATING:
        pass
    selected_clients = select_trainers(coordinator_id)
    while len(selected_clients) < MIN_CLIENTS_PARTICIPATING:
        pass

    selected_clients_ids = [client_id for client_id, _ in selected_clients]
    x_train_selected = [x_train[idx] for idx in range(len(x_train)) if str(y_train[idx]) in selected_clients_ids]
    y_train_selected = [y_train[idx] for idx in range(len(y_train)) if str(y_train[idx]) in selected_clients_ids]

    model.fit(np.array(x_train_selected), np.array(y_train_selected), epochs=1, verbose=2)

    if this_client_is_server:  # If this client is the coordinator
        aggregated_weights = federated_average(selected_clients)
        broadcast_aggregated_weights(aggregated_weights)

    evaluate_model(model, round_num)


#Funcao para selecionar treinadores dentre os clientes
def select_trainers(coordinator_id):
    trainers = list(participants - {coordinator_id})
    selected_clients = [client for client in trainers if client in election_messages_received]
    selected_clients = sorted(selected_clients, key=lambda x: election_messages_received[x], reverse=True)
    selected_clients = selected_clients[:NUM_CLIENTS_CHOSEN]
    return [(client, election_messages_received[client]) for client in selected_clients]

#Funcao para agregar os pesos
def federated_average(selected_clients):
    num_params = len(selected_clients[0][1])
    # Initialize an array to store the aggregated weights
    aggregated_weights = np.zeros_like(selected_clients[0][1])
    for _, client_weights in selected_clients:
        aggregated_weights += client_weights
    aggregated_weights /= len(selected_clients)

    return aggregated_weights

#Funcao para publicar os pesos agregados  
def broadcast_aggregated_weights(aggregated_weights):
    for participant_id in participants:
        if participant_id != client_id:
            client.publish("sd/weights", json.dumps({"ClientID": participant_id, "Weights": aggregated_weights}))

#Funcao para avaliar os modelos.
def evaluate_model(model, round_num):
    # Evaluation of the model on local test data
    _, (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_test = x_test / 255.0
    y_test = tf.one_hot(y_test.astype(np.int32), depth=10)
    loss, acc = model.evaluate(x_test, y_test, verbose=2)
    print(f"Client {client_id} - Round {round_num} Test accuracy: {acc:.4f}")
    accuracy_per_round.append(acc)  


# Função para gerar um ClientID aleatório de 16 bits
def generate_client_id():
    return str(random.randint(0, 65535))

#Callback de conexao
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
    else:
        print("Failed to connect, return code: ", rc)

# Callback para receber mensagens MQTT
def on_message(client, userdata, message):
    if message.topic == topic_init:
        process_init_message(client, userdata, message)
    elif message.topic == topic_election:
        process_election_message(client, userdata, message)
    elif message.topic == topic_start_server:
        process_start_server(client, userdata, message)
    elif message.topic == topic_start_client:
        process_start_client(client, userdata, message)


#Funcao para definicao de modelo
def define_model(input_shape, num_classes):
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

# Conecta o cliente
client_id = generate_client_id()
client.on_connect = on_connect
client.on_message = on_message 
client.connect(broker, port)

# Assina a fila de mensagens de inicialização
client.subscribe(topic_init)
client.message_callback_add(topic_init, process_init_message)

# Assina a fila de mensagens de eleição
client.subscribe(topic_election)
client.message_callback_add(topic_election, process_election_message)        


# Assina a fila de mensagens para início como servidor
client.subscribe(topic_start_server)
client.message_callback_add(topic_start_server, process_start_server)

# Assina a fila de mensagens para início como cliente
client.subscribe(topic_start_client)
client.message_callback_add(topic_start_client, process_start_client)

# Publica a mensagem de inicialização
init_data = {
    "ClientID": client_id
}
client.publish(topic_init, json.dumps(init_data))

# Start Federated Learning process as a client or server
if this_client_is_server:
    start_as_server()
else:
    start_as_client()


if this_client_is_server:
    plt.plot(range(1, MAX_ROUNDS + 1), accuracy_per_round, marker='o')
    plt.xlabel('Round')
    plt.ylabel('Accuracy')
    plt.title('Accuracy per Round')
    plt.grid()
    plt.show()


# Mantém o cliente MQTT em execução
client.loop_forever()


