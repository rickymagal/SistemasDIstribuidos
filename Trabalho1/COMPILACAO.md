## Dependências

`grpc 1.51.3`
`grpcio-tools 1.51.3`
`pybreaker 1.0.1`
`tensorflow 2.12.0`
`matplotlib 3.7.1`

## Gerar Stub

  ```sh
   python -m grpc_tools.protoc --proto_path=. ./FedLearningProto.proto --python_out=. --grpc_python_out=.
  ```

## Compilação

Compilar e exectuar primeiro o servidor, usando `python3 FedLearningServer.py` e depois os clientes com `python3 FedLearningClient.py`.
