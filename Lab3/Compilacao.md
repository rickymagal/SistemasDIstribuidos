## Dependências

`grpc 1.51.3`
`grpcio-tools 1.51.3`
`pybreaker 1.0.1`

## Gerar Stub

  ```sh
   python -m grpc_tools.protoc --proto_path=. ./grpcMiner.proto --python_out=. --grpc_python_out=.
  ```

## Compilação

Compilar e exectuar primeiro o servidor, usando `python3 grpcMiner_server.py` e depois os clientes com `python3 grpcMiner_client.py`.
