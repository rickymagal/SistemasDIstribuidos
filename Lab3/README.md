## Implementação, cliente e servidor

O trabalho foi feito usando as bibliotecas `grpc` e `grpcio-tools`, para comunicação gRPC e `pybreaker`. Para isso, o programa servidor fornece uma série de funções para obter informações das “transações” e para submeter uma resposta ao desafio, funções essas que devem ser chamadas pelo cliente e respondidas através da passagem de argumentos e retornos pelo padrão definido em `grpcMiner.proto`. Além disso, o servidor possui um menu de opções para imprimir uma tabela de transações e para adicionar uma nova transação. Por padrão, o server é iniciado com uma transação com um número de desafio aleatório entre 1 e 6. O programa cliente, por sua vez, possui um menu para solicitar informações sobre transações, pegar o ID da primeira transação (simplificado para uma só transação, como especificado, mas uma implementação futura poderia escolher uma transação aleatória dentre as não resolvidas) e para minerar.

## Mineração

O processo de mineração em si constitui em criar n threads, n especificado pelo usuário, e aplicá-las a uma função que gera uma sequência de bits, do tamanho de uma hash SHA1, e constantemente verifica se essa sequência possui o número de 0’s iniciais igual ao número de challenge da transação especificada pelo ID. A função que chama as threads então bloqueia, esperando pela primeira resposta de uma das threads, que será colocada numa fila. Novamente, em um trabalho futuro, a simplificação de apenas gerar uma sequência de bits deveria ser substituída por gerar entradas aleatórias para uma função hash combinada por servidores e clientes.

## Resultados

A seguir, é gerado um gráfico onde se analisa o tempo para obter uma resposta correta para números de desafio variando de 2 a 20, de 2 em 2, para diferentes números de threads criadas.

![MINER](https://user-images.githubusercontent.com/26047473/236579241-b8edf137-e256-4445-b34e-642206ee49e8.png)


