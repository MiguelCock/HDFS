package datanode

import (
	"context"
	"crypto/sha256"
	"os"

	"github.com/MiguelCock/HDFS/dataNode/datanode/dngrcp"
)

func (dn *DataNode) WriteBlock(ctx context.Context, req *dngrcp.WriteBlockRequest) (*dngrcp.WriteBlockResponse, error) {
	blockID := req.GetBlockId()
	data := req.GetData()

	hash := sha256.New()

	hash.Write(data)

	hashres := hash.Sum(nil)

	dn.Files[blockID] = FileMetadata{Checksum: string(hashres), Size: int64(len(data))}

	os.WriteFile(blockID, data, 0644)

	return &dngrcp.WriteBlockResponse{Status: "Block stored successfully"}, nil
}

func (dn *DataNode) ReadBlock(ctx context.Context, req *dngrcp.ReadBlockRequest) (*dngrcp.ReadBlockResponse, error) {
	blockID := req.GetBlockId()

	_, exists := dn.Files[blockID]
	if !exists {
		return &dngrcp.ReadBlockResponse{Status: "Block not found"}, nil
	}

	data, _ := os.ReadFile(blockID)

	return &dngrcp.ReadBlockResponse{Data: data, Status: "Block read successfully"}, nil
}
