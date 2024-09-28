en el readme principal está cómo compilar el .proto, pero ya no necesitas hacerlo
mi truco con el DN y los compilados del .proto fue decir que su paquete era "main" XD
vale huevo la convención estricta de GO, úsalo así

tienes que correr:

```bash
go mod init dataNode (ese es el nombre de la carpeta en la que estás)

go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

go get google.golang.org/grpc                                                       
go get google.golang.org/protobuf

(yo, windows, uso .exe) go build -o main.exe main.go DN.go datanode_service.pb.go datanode_service_grpc.pb.go

(tú deberias de usar) go build -o main main.go DN.go datanode_service.pb.go datanode_service_grpc.pb.go
```
