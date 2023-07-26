Por Ricardo Magalhães Santos Filho

## Introdução

O objetivo do trabalho é implementar um sistema distribuído, serverless, para a execução de um processo de aprendizado federado. Para isso, a cada rodada um dos “clientes” deve ser eleito para realizar o papel de servidor de agregação de pesos. Os demais clientes realizam seu papel habitual naquela rodada e o treinamento começa quando um número mínimo de clientes é conectado ao broker (definido pelo usuário). Outros parâmetros a serem definidos pelo usuário incluem o número máximo de rodadas e a tolerância alvo. Como modelo de comunicação, usamos a comunicação publish/subscribe através de um broker MQTT.

## Implementação

O programa funciona da seguinte maneira: Cada cliente conecta-se ao broker MQTT local e publica sua mensagem de inicialização para o tópico "sd/init". Quando o número mínimo de clientes é atingido, o servidor inicia a eleição do líder através do tópico "sd/election". Cada cliente envia um voto contendo seu ID e um ID de voto gerado aleatoriamente. Em seguida, o cliente com o maior ID de voto é eleito o líder e os outros clientes são notificados através dos tópicos "sd/start_server" ou "sd/start_client", dependendo de serem escolhidos como servidor ou cliente, respectivamente. Se o cliente for escolhido como servidor, ele realizará o treinamento do modelo de aprendizado profundo usando a base de dados MNIST local. Em cada rodada, ele seleciona um número fixo de outros clientes para participar do treinamento através da função "federated_learning_round", agregando seus pesos e enviando o modelo atualizado para eles. Se o cliente for escolhido como cliente, ele receberá os pesos atualizados do servidor através do tópico "sd/weights" e avaliará o modelo local com a base de dados de teste MNIST. Percebe-se que não há aprendizado federado.
Uma breve descrição de cada função do código é apresentada a seguir:

`process_init_message(client, userdata, message)`: Chamada quando uma mensagem de inicialização é recebida no tópico "sd/init". Ela processa a mensagem, adiciona o cliente que enviou a mensagem à lista de participantes e, quando o número mínimo de clientes é alcançado, inicia a eleição do líder chamando a função `start_election()`.

`start_election()`: Responsável por iniciar a fase de eleição do líder. Ela gera um ID de voto aleatório e publica uma mensagem de eleição contendo o ID de voto e o ID do cliente atual para o tópico "sd/election".

`process_election_message(client, userdata, message)`: Chamada quando uma mensagem de eleição é recebida no tópico "sd/election". Ela processa a mensagem, armazenando o ID de voto do cliente que enviou a mensagem e, quando todos os clientes enviaram seus votos, chama a função `elect_leader()` para eleger o líder.

`elect_leader()`: Elege o líder com base no ID de voto mais alto. Ela identifica os candidatos ao líder, seleciona o cliente com o maior ID de voto como líder e publica a informação para que os outros clientes saibam quem é o líder eleito. Se o cliente atual for eleito como líder, ele se declara líder e publica uma mensagem no tópico "sd/start_server" para iniciar o treinamento como servidor, caso contrário, publica uma mensagem no tópico "sd/start_client" para iniciar o treinamento como cliente.

`process_start_server(client, userdata, message)`:  Chamada quando uma mensagem é recebida no tópico "sd/start_server". Ela processa a mensagem e inicia o treinamento como servidor chamando a função `start_as_server()`.

`process_start_client(client, userdata, message)`: Chamada quando uma mensagem é recebida no tópico "sd/start_client". Ela processa a mensagem e inicia o treinamento como cliente chamando a função `start_as_client()`.

`start_as_server()`: Realiza o treinamento como servidor. Ela carrega a base de dados MNIST, define o modelo de aprendizado profundo, e inicia várias rodadas de aprendizado federado chamando a função `federated_learning_round()` em cada rodada. Ao final de cada rodada, o modelo é avaliado usando a função `evaluate_model()`, e se a acurácia desejada for alcançada, o treinamento é interrompido.

`start_as_client()`: Realiza o treinamento como cliente. Ela é configurada para receber mensagens contendo os pesos atualizados do servidor no tópico "sd/weights". Quando uma mensagem é recebida, a função avalia o modelo local usando a base de dados de teste MNIST.

(Treinamento Federado não está sendo realizado. O servidor deveria ter a única função de agregar os pesos e os clientes deveriam enviar seus pesos para serem agregados).

`federated_learning_round(round_num, model, x_train, y_train)`: Realiza um round de aprendizado federado. O servidor seleciona um conjunto de clientes participantes para treinamento chamando a função select_trainers(). Em seguida, os clientes selecionados treinam seus modelos localmente e enviam seus pesos atualizados para o servidor. O servidor agrega esses pesos usando a função `federated_average()` e envia o modelo atualizado de volta para todos os clientes.

`select_trainers(coordinator_id)`: Usada pelo servidor para selecionar um conjunto de clientes para treinamento em cada round. Ela retorna uma lista de clientes selecionados e seus respectivos IDs de voto, ordenados com base no ID de voto.

`federated_average(selected_clients)`: Usada pelo servidor para agregar os pesos dos clientes selecionados. Deveria calcular a média dos pesos de todos os clientes selecionados e retornar os pesos agregados, mas isso não ocorre pois não há passagem de pesos dos clientes para o servidor.

`broadcast_aggregated_weights(aggregated_weights)`: Usada pelo servidor para enviar os pesos agregados para todos os clientes. Ele publica as informações no tópico "sd/weights".

`evaluate_model(model, round_num)`: Avalia o modelo em cada round de treinamento. Ela carrega a base de dados de teste MNIST e calcula a acurácia do modelo em relação aos dados de teste. A acurácia é registrada para análise posterior.

Outras funções como `generate_client_id()` para gerar IDs de cliente aleatórios e as funções relacionadas ao MQTT para lidar com a conexão e recepção de mensagens também estão presentes.

## Resultados

O programa não realiza um aprendizado federado. Os pesos nunca são passados de cliente para servidor, apenas de servidor para cliente. 
