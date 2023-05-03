### Instalando dependências

As dependências podem ser instaladas usando pip, que pode ser instalado, por exemplo, com o seguinte comando (para distribuições que usam o gerenciador de pacotes APT):

`sudo apt install python3-pip`

Em seguida, as dependências podem ser instaladas com os comandos:

`python3 -m pip install flwr`
`pip install tensorflow`
`pip install ray`
`pip install matplotlib`

### Compilação

Os programas podem ser interpretados e executados pelo comando `python3 client.py` ou `python3 server.py`, tomando a precaução de iniciar o servidor antes de iniciar os clientes, todos em terminais separados.
