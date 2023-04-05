

O trabalho foi feito em python, usando a biblioteca multiprocessing para implementação dos algoritmos de mergesort para threads e para processos (no caso das threads, foi utilizado o atributo multiprocessing.pool.ThreadPool). A função merge_sort_process implementa a ordenação por processos, recebendo o vetor a ser ordenado e o número de chunks iniciais, e a função merge_sort_thread faz exatamente a mesma coisa, mas usando a ThreadPool mencionada anteriormente. A função merge_sort é uma implementação do algoritmo de ordenação rodado por cada processo ou thread. A cada iteração dessas funções, é mostrado na tela o estado atual da divisão dos vetores. Já a função merge foi feita para mesclar chunks do vetor de forma a não juntar os elementos e executar um novo sort simplesmente, tirando vantagem do fato de chunks já estarem ordenados.

O programa `Lab.py` recebe como entrada o tamanho do vetor e o número de chunks iniciais. Ele então cria um vetor de tamanho n com números aleatórios e chama as funções merge_sort_process e merge_sort_thread sequencialmente, usando a biblioteca time para computar o tempo de execução.

Além disso, foi usado um novo programa, `Lab-1-plot.py`, para simular o tempo de execução dado um número de chunks iniciais com o tamanho do vetor variando de 1000 a 100000, de 1000 em 1000.

Para k=1, 2, 4, 8 e 16, escolhas orientadas pelo professor, os gráficos são os seguintes:

![k=1](https://user-images.githubusercontent.com/26047473/229954395-efb6ca1f-383d-4e9c-8de8-2815b7ef0bb7.png)
![k=2](https://user-images.githubusercontent.com/26047473/229954724-88f3685d-dd7d-4099-83c9-b34100915750.png)
![k=4](https://user-images.githubusercontent.com/26047473/229954417-1cebcbe7-97d7-409d-a3c9-695e69df4aed.png)
![k=8](https://user-images.githubusercontent.com/26047473/229954436-352a393c-391a-4431-a73d-49a901a7b8ef.png)
![k=16](https://user-images.githubusercontent.com/26047473/229954449-e957fcec-e2d9-430b-a4c0-2204a35d06d2.png)

Para esses valores de k, que são pequenos, percebe-se que as threads perdem em desempenho. Repare, porém, que a partir de k=16 as threads começam a ganhar espaço. Então, foram feitas medições para valores de k maiores, especificamente k = 50, k = 100, k = 200 e k = 300:

![k=50](https://user-images.githubusercontent.com/26047473/229954457-693858ef-6427-4bac-80ca-deaca2b05feb.png)
![k=100](https://user-images.githubusercontent.com/26047473/229954465-9ca0d5a6-9b34-42d9-b65b-ce4077b49aa7.png)
![k=200](https://user-images.githubusercontent.com/26047473/229954471-52f57e51-df73-483e-a357-e602e2fff1e1.png)
![k=300](https://user-images.githubusercontent.com/26047473/229954476-59ae71f0-1742-4a3e-947f-edd025b490f0.png)

As threads apresentam grande desempenho para valores maiores atribuídos a k. Isso acontece porque o overhead para a criação de um processo é muito maior do que o da criação de uma thread, e esse overhead se acumula para valores muito grandes de k.
