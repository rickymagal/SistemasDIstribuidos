Por Ricardo Magalhães Santos Filho

## Introdução

O objetivo do trabalho é realizar uma eleição distribuída para decidir os papéis que cada participante vai assumir em um processo de “mineração”, que se resume em gerar uma hash que cumpre certos requisitos (neste caso, um número n de 0’s iniciais na string). As decisões tomadas foram que a eleição deve começar com no mínimo 3 participantes, que apenas um deles será o controlador e que, em caso de empate, o controlador será escolhido aleatoriamente. Além disso, cada desafio será “minerado” por 10 threads simultaneamente, sendo que o resultado correto da primeira delas será postado na fila de mensagens.

## Implementação

A implementação se baseia em um modelo publish subscribe com filas de mensagens para a inicialização, eleição, postagem de desafios e de soluções. Para processar mensagens e atualizar suas tabelas internas, foram definidas funções auxiliares como `process_init_message` para processar mensagens de inicialização, ou `process_election_message`, para processar a mensagem dos votos. Também como auxílio, foram criadas funções para os menus de cada um dos dois papéis, sendo chamados de acordo com o papel das eleições. As principais funções são a `elect_leader()` e `solve`. A função de eleição consiste em contar votos para a eleição de um líder e iniciar um dos dois menus baseado no resultado das eleições. A função `solve` é a função de mineração que gera strings de bits aleatórias e verifica se ela possui um número de bits iniciais igual ao número de challenge. A função é chamada por 10 threads (para cada desafio) que compartilham uma fila para colocarem uma solução correta. A primeira solução colocada na fila será publicada e as demais threads serão mortas para aquele desafio.

## Resultados

Creio não ser muito construtivo falar de resultados quantitativos como métricas de tempo de mineração por número de threads e número de challenger, etc. Em termos de funcionamento, o programa produzido não funciona perfeitamente em todos os ambientes. Houveram momentos em que a comunicação entre os participantes foi deficiente, desde atrasos na atualização dos vencedores e soluções nas tabelas até a problemas na eleição, como participantes perdendo a conexão antes do início. 
