package DN

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"github.com/MiguelCock/HDFS/dataNode/DN/DNgRPC"
)

// -------------------- WRITE BLOCK --------------------
func (dn *DataNode) WriteBlock(ctx context.Context, req *DNgRPC.WriteBlockRequest) (*DNgRPC.WriteBlockResponse, error) {
	blockID := req.GetBlockId()
	data := req.GetData()

	hash := sha256.New()

	hash.Write(data)

	hashres := hash.Sum(nil)

	dn.Blocks[blockID] = BlockMetadata{Checksum: string(hashres), Size: int64(len(data))}

	os.WriteFile(blockID, data, 0644)

	return &DNgRPC.WriteBlockResponse{Status: "Block stored successfully"}, nil
}

// -------------------- READ BLOCK --------------------
func (dn *DataNode) ReadBlock(ctx context.Context, req *DNgRPC.ReadBlockRequest) (*DNgRPC.ReadBlockResponse, error) {
	blockID := req.GetBlockId()

	_, exists := dn.Blocks[blockID]
	if !exists {
		return &DNgRPC.ReadBlockResponse{Status: "Block not found"}, nil
	}

	data, _ := os.ReadFile(blockID)

	return &DNgRPC.ReadBlockResponse{Data: data, Status: "Block read successfully"}, nil
}

// -------------------- REPLICATE BLOCK --------------------
func (dn *DataNode) replicateBlock(w http.ResponseWriter, r *http.Request) {
    blockID := r.URL.Query().Get("block_id")
    targetDatanode := r.URL.Query().Get("target_datanode")

    if blockID == "" || targetDatanode == "" {
        http.Error(w, "Missing block_id or target_datanode", http.StatusBadRequest)
        return
    }

	// DEPRECATED GRPC FUNCTIONS
    // conn, err := grpc.Dial(targetDatanode, grpc.WithInsecure())
    // conn, err := grpc.Dial(targetDatanode, grpc.WithTransportCredentials(insecure.NewCredentials()))
    client, err := grpc.NewClient(targetDatanode, grpc.WithTransportCredentials(insecure.NewCredentials())) 
    if err != nil {
        log.Printf("Failed to create new gRPC client: %v", err)
        http.Error(w, "Failed to create new gRPC client", http.StatusInternalServerError)
        return
    }
    defer client.Close()

    dataNodeServiceClient := DNgRPC.NewDataNodeServiceClient(client)

    blockData, err := os.ReadFile(blockID)
    if err != nil {
        log.Printf("Failed to read block from disk: %v", err)
        http.Error(w, "Failed to read block from disk", http.StatusInternalServerError)
        return
    }

    writeRes, err := dataNodeServiceClient.WriteBlock(context.Background(), &DNgRPC.WriteBlockRequest{
        BlockId: blockID,
        Data:    blockData,
    })
    if err != nil {
        log.Printf("Error writing block to target DataNode: %v", err)
        http.Error(w, "Failed to replicate block", http.StatusInternalServerError)
        return
    }

    log.Printf("WriteBlock response: %v", writeRes.Status)

    response := Response{Status: "Bloque replicado exitosamente"}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}
