package main

import (
    "fmt"
    "log"
    "net"
    "net/http"
    "google.golang.org/grpc"
    "google.golang.org/grpc/reflection"
)

func main() {
    // Cargamos el archivo de configuración
    datanode, err := LoadConfig("./bootstrap.json") // Usamos la función de DN.go
    if err != nil {
        log.Fatalf("error loading configuration: %v", err)
    }

    // Registramos el DataNode con el NameNode
    err = datanode.RegisterWithNameNode() // Función definida en DN.go
    if err != nil {
        log.Fatalf("error registering DataNode: %v", err)
    }

    // Iniciamos las rutinas para heartbeats y block reports
    go datanode.SendHeartbeat()  // Función definida en DN.go
    go datanode.SendBlockReport() // Función definida en DN.go

    // Iniciamos el servidor gRPC
    go startGRPCServer(datanode)

    // Iniciamos el servidor HTTP para probar la conexión
    http.HandleFunc("/test", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "DataNode is running")
    })

    log.Fatal(http.ListenAndServe(fmt.Sprintf("%s:%d", datanode.OwnIP, datanode.OwnPort), nil))
}

// Iniciamos el servidor gRPC
func startGRPCServer(dn *DataNode) {
    grpcPort := dn.OwnPort + 1 // El puerto de gRPC es el puerto de API REST + 1
    lis, err := net.Listen("tcp", fmt.Sprintf("%s:%d", dn.OwnIP, grpcPort))
    if err != nil {
        log.Fatalf("failed to listen: %v", err)
    }

    server := grpc.NewServer()
    // Aquí deberías registrar tu servicio gRPC si tienes uno. Por ejemplo:
    // pb.RegisterDataNodeServiceServer(server, dn)
    reflection.Register(server)

    log.Printf("gRPC server running on %s:%d", dn.OwnIP, grpcPort)
    if err := server.Serve(lis); err != nil {
        log.Fatalf("failed to serve: %v", err)
    }
}
