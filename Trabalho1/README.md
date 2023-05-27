## Cliente e Servidor

O cliente de treinamento do cliente foi implementado com os serviços `StartTraining` e `EvaluateModel`, a serem chamados pelo servidor. Ao chamar `StartTraining`, o servidor passa como parâmetro o `path` para um arquivo onde devem ser salvados os pesos ao final do treinamento. Cada `path` é inicializado pelo servidor de acordo com o ID do cliente. Ao terminar o treinamento, o cliente salva os seus pesos e retorna o número de samples usadas (nesse caso, dividimos o dataset MNIST em samples aleatórias). Depois de fazer a chamada de `StartTraining` para cada cliente, o servidor agrega os pesos e faz uma chamada de `EvaluateModel` para cada cliente, passando o `path` onde estão os pesos agregados, escritos na etapa anterior. O cliente atualiza os seus pesos e avalia seu modelo, retornando a acurácia. Ao fazer isso para cada cliente, o servidor exibe os gráficos da média das precisões por rodada.

Ao ser iniciado, o cliente faz uma chamada de `RegisterClient`, fornecida pelo servidor. Essa chamada adiciona o cliente à sua lista interna, inicia o treinamento federado se essa lista tem tamanho maior ou igual ao número mínimo de clientes (input do usuário, junto com o número máximo de rounds e a tolerância alvo) e retorna um código de confirmação igual a 200 se o cliente for realmente registrado. O servidor, por sua vez, apenas inicia e espera por chamadas.

## Resultados
Os resultados obtidos para 5, 10 e 20 rounds usando 3 clientes são mostrados a seguir:
![5rounds](https://github.com/rickymagal/SistemasDistribuidos/assets/26047473/5415837e-f487-4ca4-adf3-6eafb79c9e63)
![10rounds](https://github.com/rickymagal/SistemasDistribuidos/assets/26047473/0dcef2d8-247c-4f6f-b6fa-12d256437176)
![20rounds](https://github.com/rickymagal/SistemasDistribuidos/assets/26047473/b8897fe6-f222-4854-a5e6-95a0047259e4)

Como esperado, a precisão parece convegir quando se aumenta o número de rounds
