# Sistema de Archivos Distribuidos por Bloques

Este proyecto es un sistema de archivos distribuidos minimalista basado en bloques, inspirado en GFS y HDFS. Está diseñado para gestionar archivos distribuidos, particionados en bloques, con replicación mínima en los DataNodes y coordinación a través de un NameNode.

## Componentes Principales

1. **Client**: Solicita la creación, lectura, escritura, y eliminación de archivos. Se conecta al **NameNode** para obtener metadatos y a los **DataNodes** para subir o descargar bloques de archivos.
2. **NameNode**: Administra los metadatos, la asignación de bloques y la replicación. No maneja directamente los archivos, sino que coordina la ubicación de los bloques entre los DataNodes.
3. **DataNodes**: Almacenan los bloques de archivos. Reciben, envían y replican bloques a petición del **Client** o del **NameNode**.


## Compilar el .proto

### En Python (client):

```bash
pip install grpcio
pip install grpcio-tools


python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. datanode_service.proto
```

### En Go (datanode):

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

export PATH="$PATH:$(go env GOPATH)/bin"

protoc --go_out=. --go-grpc_out=. datanode_service.proto
```