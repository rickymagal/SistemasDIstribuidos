import json
import multiprocessing as mp
import paho.mqtt.client as mqtt
import random

# Configurações do broker MQTT
broker = "localhost"
port = 1883
topic_init = "sd/init"
topic_election = "sd/election"
topic_challenge = "sd/challenge"
topic_solution = "sd/solution"
topic_pubkey = "sd/pubkey"
topic_cert = "sd/cert"

# Variáveis para controle da eleição
participants = set()
init_messages_received = set()
election_messages_received = {}

# Dados do líder eleito
leader_id = None
leader_vote_id = None

# Controles internos
fila = mp.SimpleQueue()
transactions = {}

# Defina aqui o número de participantes do sistema
num_participants = 4

# Gera um ClientID aleatório de 16 bits
client_id = str(random.randint(0, 65535))

# Chave pública do participante (exemplo)
public_key_hex = "a1b2c3d4e5f6"

# Certificado digital do participante (exemplo)
certificate = "..."

# Variáveis para controle de certificados
certificates_received = set()

# Função para processar a mensagem de inicialização
def process_init_message(client, userdata, message):
    payload = json.loads(message.payload)
    client_id = payload["ClientID"]

    # Adiciona o participante à lista
    participants.add(client_id)
    init_messages_received.add(client_id)

    if len(init_messages_received) == num_participants:
        # Todos os participantes enviaram suas mensagens de inicialização
        start_pubkey_exchange()

# Função para iniciar a fase de troca de chaves públicas (PubKeys)
def start_pubkey_exchange():
    for participant_id in participants:
        if participant_id != client_id:
            # Envia a chave pública e o certificado para cada participante
            pubkey_data = {
                "ClientID": client_id,
                "PubKey": public_key_hex,
                "Cert": certificate
            }
            client.publish(topic_pubkey, json.dumps(pubkey_data), qos=1)  # Utilize QoS 1 para garantir entrega

    # Aguarda a recepção das chaves públicas e certificados dos demais participantes
    # Neste ponto, todos os participantes devem ter a chave pública e o certificado de todos os outros participantes

    # Inicia a fase de eleição
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

# Função para processar a mensagem de eleição
def process_election_message(client, userdata, message):
    payload = json.loads(message.payload)
    client_id = payload["ClientID"]
    vote_id = payload["VoteID"]

    election_messages_received[client_id] = vote_id

    if len(election_messages_received) == num_participants:
        # Todos os votos foram recebidos
        elect_leader()

# Função para eleger o líder
def elect_leader():
    global leader_id, leader_vote_id
    max_vote_id = max(election_messages_received.values())
    leader_candidates = [client_id for client_id, vote_id in election_messages_received.items() if vote_id == max_vote_id]
    leader_id = leader_candidates[0]
    leader_vote_id = max_vote_id
    # O líder assume o papel de controlador
    if leader_id == client_id:
        print("Eu sou o líder! ClientID:", leader_id)
        controller_run()
    else:
        miner_run()

# Função que define a interface do minerador
def miner_run():
    while True:
        user_input = input("Opções:\n1. Publicar novo desafio\n2. Imprimir tabela de transações\n3. Sair\nEscolha uma opção: ")
        if user_input == "3":
            break
        if user_input == "1":
            # Publica um novo desafio
            new_challenge = {
                "TransactionID": len(transactions),
                "Challenge": random.randint(1, 6)  # Substitua pelo valor desejado para o challenge
            }
            client.publish(topic_challenge, json.dumps(new_challenge))
            print("Novo desafio publicado:")
            print("TransactionID:", new_challenge["TransactionID"])
            print("Challenge:", new_challenge["Challenge"])

            # Adiciona a transação na lista
            new_transaction = {
                "Challenge": new_challenge["Challenge"],
                "Solution": None,
                "Winner": None
            }
            transactions[new_challenge["TransactionID"]] = new_transaction

        if user_input == "2":
            # Atualiza a tabela de transações
            print_transactions()

# Função que define a interface do controlador
def controller_run():
    while True:
        # Verifica se há desafios pendentes sem vencedor
        unsolved_transactions = [tid for tid, trans in transactions.items() if trans["Winner"] is None]

        if unsolved_transactions:
            # Ordena as transações pelo número de challenge
            unsolved_transactions.sort()

            # Seleciona a primeira transação na ordem de número de challenge
            transaction_id = unsolved_transactions[0]
            transaction = transactions[transaction_id]
            challenge = transaction["Challenge"]

            print("Minerador buscando solução para o TransactionID:", transaction_id)
            print("Desafio:", challenge)

            pool = mp.Pool(processes=10)
            pool.apply_async(solve, args=(challenge,))
            pool.close()
            pool.join()

            solution = fila.get()
            print("Solução encontrada:", solution)

            # Atualiza a transação com a solução encontrada

            # Envia a solução encontrada
            solution_data = {
                "ClientID": client_id,
                "TransactionID": transaction_id,
                "Solution": solution
            }
            client.publish(topic_solution, json.dumps(solution_data))
        else:
            print("Não há desafios pendentes sem vencedor.")

            # Atualiza a tabela de transações
            print_transactions()

            user_input = input("Opções:\n1. Continuar buscando soluções\n2. Sair\nEscolha uma opção: ")
            if user_input == "2":
                break

# Função para resolver um desafio
def solve(challenge):
    while True:
        guess = generateBinaryString(128)
        if guess[0:challenge] == "0" * challenge:
            fila.put(guess)
            break

# Função para processar um desafio
def process_challenge(client, userdata, message):
    payload = json.loads(message.payload)
    transaction_id = payload["TransactionID"]
    challenge = payload["Challenge"]

    print("Recebido novo desafio:")
    print("TransactionID:", transaction_id)
    print("Desafio:", challenge)

    # Adiciona a transação na lista
    new_transaction = {
        "Challenge": challenge,
        "Solution": None,
        "Winner": None
    }
    transactions[transaction_id] = new_transaction

# Função para processar a mensagem de solução
def process_solution(client, userdata, message):
    payload = json.loads(message.payload)
    client_id = payload["ClientID"]
    transaction_id = payload["TransactionID"]
    solution = payload["Solution"]

    if transaction_id in transactions:
        transaction = transactions[transaction_id]
        if transaction["Solution"] is None:
            challenge = transaction["Challenge"]
            if solution.startswith("0" * challenge):
                print("Solução válida encontrada para o TransactionID:", transaction_id)
                print("ClientID:", client_id)
                print("Solution:", solution)
                transaction["Solution"] = solution
                transaction["Winner"] = client_id
            else:
                print("Solução inválida para o TransactionID:", transaction_id)
        else:
            print("Transação já possui uma solução válida.")
    else:
        print("TransactionID inválido:", transaction_id)

    # Atualiza a tabela de transações
    print_transactions()

# Função para processar a mensagem de certificado
def process_certificate(client, userdata, message):
    global certificates_received
    payload = json.loads(message.payload)
    node_id = payload["NodeID"]
    certificate = payload["Cert"]

    certificates_received.add(node_id)

    if len(certificates_received) == num_participants:
        # Todos os certificados foram recebidos
        extract_pubkeys()

# Função para extrair chaves públicas dos certificados recebidos
def extract_pubkeys():
    for participant_id in participants:
        if participant_id != client_id:
            # Extraia a chave pública do certificado
            pubkey = extract_pubkey_from_cert(certificate)
            # Aqui você pode armazenar as chaves públicas extraídas em uma estrutura de dados ou utilizá-las conforme necessário
            print("Chave pública do participante", participant_id, ":", pubkey)

# Função para extrair a chave pública de um certificado (implementação fictícia)
def extract_pubkey_from_cert(certificate):
    # Esta é apenas uma implementação fictícia de extração de chave pública do certificado
    # Substitua este trecho pela lógica real de extração da chave pública do certificado
    return "a1b2c3d4e5f6"  # Exemplo de chave pública extraída do certificado

# Função para imprimir a tabela de transações
def print_transactions():
    print("Tabela de Transações:")
    print("TransactionID | Challenge | Solution | Winner")
    for transaction_id, transaction in transactions.items():
        challenge = transaction["Challenge"]
        solution = transaction["Solution"]
        winner = transaction["Winner"]
        print(f"{transaction_id:13} | {challenge:9} | {solution} | {winner}")

def generateBinaryString(size):
    binary_list = [str(random.randint(0, 1)) for _ in range(size)]
    binary_string = ''.join(binary_list)
    return binary_string

# Configura o cliente MQTT
client = mqtt.Client()
client.connect(broker, port)

# Assina a fila de mensagens de inicialização
client.subscribe(topic_init)
client.message_callback_add(topic_init, process_init_message)

# Assina a fila de mensagens de eleição
client.subscribe(topic_election)
client.message_callback_add(topic_election, process_election_message)

# Assina a fila de mensagens de solução
client.subscribe(topic_solution)
client.message_callback_add(topic_solution, process_solution)

# Assina a fila de mensagens de desafio
client.subscribe(topic_challenge)
client.message_callback_add(topic_challenge, process_challenge)

# Assina a fila de mensagens de certificado
client.subscribe(topic_cert)
client.message_callback_add(topic_cert, process_certificate)

# Publica a mensagem de inicialização
init_data = {
    "ClientID": client_id
}
client.publish(topic_init, json.dumps(init_data))

# Mantém o cliente MQTT em execução
client.loop_forever()
