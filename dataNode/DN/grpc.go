package DN

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/MiguelCock/HDFS/dataNode/DN/DNgRPC"
	"google.golang.org/grpc"
)

// -------------------- WRITE BLOCK --------------------
func (dn *DataNode) WriteBlock(ctx context.Context, req *dngrcp.WriteBlockRequest) (*dngrcp.WriteBlockResponse, error) {
	blockID := req.GetBlockId()
	data := req.GetData()

	hash := sha256.New()

	hash.Write(data)

	hashres := hash.Sum(nil)

	dn.Blocks[blockID] = BlockMetadata{Checksum: string(hashres), Size: int64(len(data))}

	os.WriteFile(blockID, data, 0644)

	return &dngrcp.WriteBlockResponse{Status: "Block stored successfully"}, nil
}

// -------------------- READ BLOCK --------------------
func (dn *DataNode) ReadBlock(ctx context.Context, req *dngrcp.ReadBlockRequest) (*dngrcp.ReadBlockResponse, error) {
	blockID := req.GetBlockId()

	_, exists := dn.Blocks[blockID]
	if !exists {
		return &dngrcp.ReadBlockResponse{Status: "Block not found"}, nil
	}

	data, _ := os.ReadFile(blockID)

	return &dngrcp.ReadBlockResponse{Data: data, Status: "Block read successfully"}, nil
}

// -------------------- REPLICATE BLOCK --------------------
func (dn *DataNode) replicateBlock(w http.ResponseWriter, r *http.Request) {
	blockID := r.URL.Query().Get("block_id")
	target_datanode := r.URL.Query().Get("target_datanode")

	conn, err := grpc.NewClient(target_datanode)
	if err != nil {
		log.Fatalf("Failed to connect: %v", err)
	}
	defer conn.Close()

	client := dngrcp.NewDataNodeServiceClient(conn)

	block_data, _ := os.ReadFile(blockID)
	writeRes, err := client.WriteBlock(context.Background(), &dngrcp.WriteBlockRequest{
		BlockId: blockID,
		Data:    block_data,
	})
	if err != nil {
		log.Fatalf("Error writing block: %v", err)
	}

	log.Printf("WriteBlock response: %v", writeRes.Status)

	response := Response{Status: "Bloque replicado exitosamente"}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}
