 Esse trabalho foi feito usando as bibliotecas flower, para o aprendizado federado, tensorflow, para carregar os dados para treinamento e teste e numpy e matplotlib para processamento e demonstração dos dados. Para o treinamento, foram definidos dois programas `client.py` e `server.py`, e um número de clientes igual a 5. O programa `server.py` define o método de agregação de parâmetros, definido pela função `weighted_average` e a estratégia de aprendizado, tomando como input o número de rounds do processo. Quando o aprendizado é finalizado, o programa-servidor imprime a precisão alcançada por número de rounds.

O programa `client.py`, por outro lado, define o processamento do lado do cliente. Para isso, é definida uma função `define_model`, a ser usada para definir o modelo na instanciação de um objeto `FlowerClient`. A classe `FlowerClient`, que possui parâmetros para o modelo e para os dados de aprendizado e teste, possui métodos para retornar parâmetros (`get_parameters`), treino (`fit`) e para avaliação de resultados (`evaluate`). A função `fit` também recebe como entrada os parâmetros iniciais a serem dados pelo servidor ao final de cada round. Finalmente, é definida a função  `client_fn_random`, para criar um cliente aleatório, selecionando dados aleatórios de tamanho igual ao tamanho dos dados dividido pelo número de clientes.

Para simular a rede, a interface `localhost` foi usada como endereço do servidor, conectado a uma porta padrão `8080`.

Os resultados da simulação, para 2, 5, 10, 20 e 40 rounds são mostrados a seguir:

![2rounds](https://user-images.githubusercontent.com/26047473/233534107-3c8ea7ef-1fde-4569-ba0b-b914f42b6749.png)
![5rounds](https://user-images.githubusercontent.com/26047473/233534115-2b3342c7-c139-42c3-96f5-f2a0193db7b8.png)
![40rounds](https://user-images.githubusercontent.com/26047473/233534234-d7f97835-68e3-4832-a3cf-b681d903542d.png)
![20rounds](https://user-images.githubusercontent.com/26047473/233534152-45f9acb3-3784-4d12-ae1c-c03944ce8dc6.png)
![40rounds](https://user-images.githubusercontent.com/26047473/233534157-069ffa3a-372b-48c8-ad90-374b13c315f1.png)

Podemos que observar que houve grandes mudanças na precisão até o quinto para o décimo round. Depois disso, a precisão parece convergir. Isso é o resultado esperado.
