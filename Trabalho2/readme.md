Por Ricardo Magalhães Santos Filho

## Introdução

O objetivo do trabalho é implementar um sistema distribuído, serverless, para a execução de um processo de aprendizado federado. Para isso, a cada rodada um dos “clientes” deve ser eleito para realizar o papel de servidor de agregação de pesos. Os demais clientes realizam seu papel habitual naquela rodada e o treinamento começa quando um número mínimo de clientes é conectado ao broker (definido pelo usuário). Outros parâmetros a serem definidos pelo usuário incluem o número máximo de rodadas e a tolerância alvo. Como modelo de comunicação, usamos a comunicação publish/subscribe através de um broker MQTT.

## Implementação

Para a comunicação, são usadas 2 filas de mensagens: `init` e `election`. Na fila `init` são publicadas as mensagens de inicialização de cada cliente e na fila de eleição é publicada a mensagem de eleição. Idealmente, se usaria filas adicionais para a troca de pesos entre clientes e servidor de agregação de cada mensagem, mas pelas limitações do broker MQTT a escolha de projeto foi usar um `filepath` comum para os pesos agregados e um arquivo de pesos local para cada cliente. Para o processamentos das mengagens de eleição e de inicialização, são usadas as funções auxiliares `process_init_message` e `process_election_message`. Além disso, a mensagem de líder é publicada por `publish_leader_message`.

A eleição é feita através das funções `start_election` e `elect_leader`. Como o nome diz, a função de início de eleição é chamada quando o requisito do número mínimo de clientes é cumprido, enquanto a função de eleição de líder é responsável por contar votos e, se for o caso, se proclamar como líder. Ao ser informado se é ou não líder, escolhe uma das interfaces para iniciar, `TrainingServer` se for o eleito e `TrainingClient` se não for. Adicionalmente, é definida uma função `average_weights` como a função a ser chamada para agregar os pesos.


## Resultados

O programa produzido pode não funcionar bem em todos os ambientes. Tive sérios problemas na passagem de pesos pelo broker MQTT e creio que a solução que encontrei não foi satisfatória.
