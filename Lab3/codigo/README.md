Para gerar o stub
  ```sh
   python -m grpc_tools.protoc --proto_path=. ./grpcMiner.proto --python_out=. --grpc_python_out=.
  ```