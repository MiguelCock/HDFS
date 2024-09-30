package DN

import (
	"context"
	"crypto/sha256"
	"encoding/json"
    "fmt"
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

	err := os.WriteFile(blockID, data, 0644)
	if err != nil {
		log.Printf("Error escribiendo bloque %s en disco: %v", blockID, err)
		return &DNgRPC.WriteBlockResponse{Status: "Error al almacenar el bloque en disco"}, err
	}

	log.Printf("Bloque %s escrito en disco exitosamente", blockID)
	return &DNgRPC.WriteBlockResponse{Status: "Bloque almacenado exitosamente"}, nil
}

// -------------------- READ BLOCK --------------------
func (dn *DataNode) ReadBlock(ctx context.Context, req *DNgRPC.ReadBlockRequest) (*DNgRPC.ReadBlockResponse, error) {
	blockID := req.GetBlockId()

	_, exists := dn.Blocks[blockID]
	if !exists {
		log.Printf("Bloque %s no encontrado", blockID)
		return &DNgRPC.ReadBlockResponse{Status: "Bloque no encontrado"}, nil
	}

	data, err := os.ReadFile(blockID)
	if err != nil {
		log.Printf("Error leyendo bloque %s desde el disco: %v", blockID, err)
		return &DNgRPC.ReadBlockResponse{Status: "Error al leer el bloque desde el disco"}, err
	}

	log.Printf("Bloque %s enviado para lectura", blockID)
	return &DNgRPC.ReadBlockResponse{Data: data, Status: "Bloque leído exitosamente"}, nil
}

// -------------------- REPLICATE BLOCK --------------------
func (dn *DataNode) replicateBlock(w http.ResponseWriter, r *http.Request) {
    blockID := r.URL.Query().Get("block_id")
    targetDatanodeIp := r.URL.Query().Get("target_datanode_ip")
    targetDatanodePort := r.URL.Query().Get("target_datanode_port")

    if blockID == "" || targetDatanodeIp == "" || targetDatanodePort == "" {
        http.Error(w, "Missing block_id, target_datanode_ip or target_datanode_port", http.StatusBadRequest)
        return
    }

    targetDatanode := fmt.Sprintf("%s:%s", targetDatanodeIp, targetDatanodePort)

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

    log.Printf("WriteBlock (replication at DataNode: %s) response: %s", targetDatanode, writeRes.Status)

    response := Response{Status: "Bloque replicado exitosamente"}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}
