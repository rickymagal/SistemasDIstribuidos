O trabalho foi feito em python, usando a biblioteca multiprocessing para implementação dos algoritmos de mergesort para threads e para processos (no caso das threads, foi utilizado o atributo multiprocessing.pool.ThreadPool). A função merge_sort_process implementa a ordenação por processos, recebendo o vetor a ser ordenado e o número de chunks iniciais, e a função merge_sort_thread faz exatamente a mesma coisa, mas usando a ThreadPool mencionada anteriormente. A função merge_sort é uma implementação do algoritmo de ordenação rodado por cada processo ou thread. A cada iteração dessas funções, é mostrado na tela o estado atual da divisão dos vetores. Já a função merge foi feita para mesclar chunks do vetor de forma a não juntar os elementos e executar um novo sort simplesmente, tirando vantagem do fato de chunks já estarem ordenados.

O programa `Lab.py` recebe como entrada o tamanho do vetor e o número de chunks iniciais. Ele então cria um vetor de tamanho n com números aleatórios e chama as funções merge_sort_process e merge_sort_thread sequencialmente, usando a biblioteca time para computar o tempo de execução.

Além disso, foi usado um novo programa, `Lab-1-plot.py`, para simular o tempo de execução dado um número de chunks iniciais com o tamanho do vetor variando de 1000 a 100000, de 1000 em 1000.

A seguir são mostrados os gráficos gerados por `Lab-1-plot.py`

![Uploading image.png…]()




A ordenação por threads demonstrou maior desempenho para todos os k’s. Os motivos para isso podem ser variados, desde o elevado custo para se manter processos até questões de hardwares que têm suporte para threads.
