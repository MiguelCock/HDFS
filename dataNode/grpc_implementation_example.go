package main

import (
    "context"
    "fmt"
    "log"
    "net"

    "google.golang.org/grpc"
    pb "path/to/datanode_service"
)

type server struct {
    pb.UnimplementedDataNodeServiceServer
    blockStorage map[string][]byte
}

func (s *server) WriteBlock(ctx context.Context, req *pb.WriteBlockRequest) (*pb.WriteBlockResponse, error) {
    blockID := req.GetBlockId()
    data := req.GetData()

    // store the block data in the map
    s.blockStorage[blockID] = data
    return &pb.WriteBlockResponse{Status: "Block stored successfully"}, nil
}

func (s *server) ReadBlock(ctx context.Context, req *pb.ReadBlockRequest) (*pb.ReadBlockResponse, error) {
    blockID := req.GetBlockId()

    data, exists := s.blockStorage[blockID]
    if !exists {
        return &pb.ReadBlockResponse{Status: "Block not found"}, nil
    }

    return &pb.ReadBlockResponse{Data: data, Status: "Block read successfully"}, nil
}

func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("failed to listen: %v", err)
    }

    grpcServer := grpc.NewServer()
    s := &server{
        blockStorage: make(map[string][]byte),
    }
    pb.RegisterDataNodeServiceServer(grpcServer, s)

    fmt.Println("DataNode server is running on port 50051")
    if err := grpcServer.Serve(lis); err != nil {
        log.Fatalf("failed to serve: %v", err)
    }
}
