O trabalho foi feito em python, usando a biblioteca multiprocessing para implementação dos algoritmos de mergesort para threads e para processos (no caso das threads, foi utilizado o atributo multiprocessing.pool.ThreadPool). A função merge_sort_process implementa a ordenação por processos, recebendo o vetor a ser ordenado e o número de chunks iniciais, e a função merge_sort_thread faz exatamente a mesma coisa, mas usando a ThreadPool mencionada anteriormente. A função merge_sort é uma implementação do algoritmo de ordenação rodado por cada processo ou thread. A cada iteração dessas funções, é mostrado na tela o estado atual da divisão dos vetores. Já a função merge foi feita para mesclar chunks do vetor de forma a não juntar os elementos e executar um novo sort simplesmente, tirando vantagem do fato de chunks já estarem ordenados.

O programa `Lab.py` recebe como entrada o tamanho do vetor e o número de chunks iniciais. Ele então cria um vetor de tamanho n com números aleatórios e chama as funções merge_sort_process e merge_sort_thread sequencialmente, usando a biblioteca time para computar o tempo de execução.

Além disso, foi usado um novo programa, `Lab-1-plot.py`, para simular o tempo de execução dado um número de chunks iniciais com o tamanho do vetor variando de 1000 a 100000, de 1000 em 1000.

Para k=1, 2, 4, 8 e 16, escolhas orientadas pelo professor, os gráficos são os seguintes:

![Uploading k=1.png…]()
![Uploading k=2.png…]()
![Uploading k=4.png…]()
![Uploading k=8.png…]()
![Uploading k=16.png…]()

Para esses valores de k, que são pequenos, percebe-se que as threads perdem em desempenho. Repare, porém, que a partir de k=16 as threads começam a ganhar espaço. Então, foram feitas medições para valores de k maiores, especificamente k = 50, k = 100, k = 200 e k = 300:

![Uploading k=50.png…]()
![Uploading k=100.png…]()
![Uploading k=200.png…]()
![Uploading k=300.png…]()

As threads apresentam grande desempenho para valores maiores atribuídos a k. Isso acontece porque o overhead para a criação de um processo é muito maior do que o da criação de uma thread, e este overhead se acumula para valores muito grandes de k.
